#!/usr/bin/env python3
"""
변환된 데이터를 Supabase에 업로드하는 도구
"""

import json
import os
import requests
from datetime import datetime
import logging
from typing import Dict, List, Optional
from convert_to_supabase import load_env_file

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_temp/supabase_upload.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SupabaseUploader:
    def __init__(self):
        """Supabase 업로더 초기화"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # 업로드용으로 service key 사용
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY 환경변수가 필요합니다.")
        
        self.api_url = f"{self.supabase_url}/rest/v1"
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
    
    def test_connection(self) -> bool:
        """Supabase 연결 테스트"""
        try:
            response = requests.get(
                f"{self.api_url}/iris_metrics?limit=1",
                headers=self.headers
            )
            if response.status_code == 200:
                logger.info("Supabase 연결 성공")
                return True
            else:
                logger.error(f"Supabase 연결 실패: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"연결 테스트 오류: {e}")
            return False
    
    def create_table_if_not_exists(self) -> bool:
        """테이블이 없으면 생성 (SQL 파일 실행 안내)"""
        logger.info("테이블 존재 확인 중...")
        try:
            response = requests.get(
                f"{self.api_url}/iris_metrics?limit=1",
                headers=self.headers
            )
            if response.status_code == 200:
                logger.info("iris_metrics 테이블이 이미 존재합니다.")
                return True
            elif response.status_code == 404:
                logger.warning("iris_metrics 테이블이 존재하지 않습니다.")
                logger.info("먼저 Supabase SQL Editor에서 supabase_schema.sql을 실행해주세요.")
                return False
            else:
                logger.error(f"테이블 확인 실패: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"테이블 확인 오류: {e}")
            return False
    
    def clear_existing_data(self) -> bool:
        """기존 데이터 삭제 (선택사항)"""
        try:
            response = requests.delete(
                f"{self.api_url}/iris_metrics",
                headers=self.headers
            )
            if response.status_code in [200, 204]:
                logger.info("기존 데이터 삭제 완료")
                return True
            else:
                logger.error(f"데이터 삭제 실패: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"데이터 삭제 오류: {e}")
            return False
    
    def upload_batch(self, metrics: List[Dict], batch_size: int = 50) -> int:
        """배치 단위로 데이터 업로드"""
        total_uploaded = 0
        total_batches = (len(metrics) + batch_size - 1) // batch_size
        
        for i in range(0, len(metrics), batch_size):
            batch = metrics[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            logger.info(f"배치 {batch_num}/{total_batches} 업로드 중 ({len(batch)}개)")
            
            try:
                response = requests.post(
                    f"{self.api_url}/iris_metrics",
                    headers=self.headers,
                    json=batch
                )
                
                if response.status_code in [200, 201]:
                    total_uploaded += len(batch)
                    logger.info(f"배치 {batch_num} 업로드 성공")
                else:
                    logger.error(f"배치 {batch_num} 업로드 실패: {response.status_code}")
                    logger.error(f"응답: {response.text}")
                    
            except Exception as e:
                logger.error(f"배치 {batch_num} 업로드 오류: {e}")
        
        return total_uploaded
    
    def load_converted_data(self, filename: str = "data/iris_metrics_supabase_format.json") -> List[Dict]:
        """변환된 데이터 로드"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('metrics', [])
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
            return []
    
    def verify_upload(self, expected_count: int) -> bool:
        """업로드 검증"""
        try:
            response = requests.get(
                f"{self.api_url}/iris_metrics?select=count",
                headers=self.headers
            )
            
            if response.status_code == 200:
                # Supabase count 방식
                response = requests.get(
                    f"{self.api_url}/iris_metrics?select=id&limit=1",
                    headers={**self.headers, 'Prefer': 'count=exact'}
                )
                
                if 'content-range' in response.headers:
                    count_str = response.headers['content-range']
                    actual_count = int(count_str.split('/')[-1])
                    
                    logger.info(f"업로드 검증: {actual_count}/{expected_count}")
                    return actual_count == expected_count
                    
        except Exception as e:
            logger.error(f"업로드 검증 오류: {e}")
        
        return False

def main():
    """메인 실행 함수"""
    # 환경변수 로드
    load_env_file()
    
    try:
        uploader = SupabaseUploader()
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")
        print("📝 env.example 파일을 참고하여 .env 파일을 생성하세요.")
        return
    
    # 연결 테스트
    if not uploader.test_connection():
        print("❌ Supabase 연결 실패")
        return
    
    # 테이블 확인
    if not uploader.create_table_if_not_exists():
        print("❌ 테이블이 존재하지 않습니다.")
        print("📝 먼저 Supabase SQL Editor에서 supabase_schema.sql을 실행하세요.")
        return
    
    # 데이터 로드
    logger.info("변환된 데이터 로드 중...")
    metrics = uploader.load_converted_data()
    
    if not metrics:
        print("❌ 업로드할 데이터가 없습니다.")
        return
    
    print(f"🚀 {len(metrics)}개 메트릭을 Supabase에 업로드 시작")
    
    # 기존 데이터 삭제 여부 확인
    clear_existing = input("기존 데이터를 삭제하시겠습니까? (y/N): ").lower().strip()
    if clear_existing == 'y':
        uploader.clear_existing_data()
    
    # 업로드 실행
    uploaded_count = uploader.upload_batch(metrics)
    
    # 검증
    if uploader.verify_upload(len(metrics)):
        print(f"✅ 업로드 완료: {uploaded_count}/{len(metrics)}개")
    else:
        print(f"⚠️ 업로드 완료되었지만 검증 실패: {uploaded_count}개 업로드됨")

if __name__ == "__main__":
    main()
