#!/usr/bin/env python3
"""
수집된 IRIS+ 데이터를 Supabase 테이블 구조에 맞게 변환하는 도구
"""

import json
import os
from datetime import datetime
import logging
from typing import Dict, List, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_temp/supabase_conversion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_env_file(env_file: str = '.env'):
    """환경변수 파일을 로드합니다."""
    if os.path.exists(env_file):
        logger.info(f"환경변수 파일 로드 중: {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        logger.info("환경변수 로드 완료")
    else:
        logger.info(f"환경변수 파일 없음: {env_file} (선택사항)")

class SupabaseConverter:
    def __init__(self):
        """
        Supabase 연결 정보 (환경변수에서 로드)
        """
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase 연결 정보가 환경변수에 설정되지 않았습니다. (SUPABASE_URL, SUPABASE_ANON_KEY)")
            logger.info("현재는 데이터 변환만 수행합니다.")
        
    def load_collected_data(self, filename: str = "data/iris_metrics_complete.json") -> Dict:
        """수집된 데이터를 로드합니다."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
            return {}
    
    def convert_metric_to_supabase_format(self, metric: Dict) -> Dict:
        """단일 메트릭을 Supabase 형식으로 변환합니다."""
        try:
            details = metric.get('details', {})
            
            # 기본 정보 (모든 필드를 명시적으로 설정)
            converted = {
                'title_en': metric.get('title', ''),
                'title_ko': None,  # 추후 번역 추가
                'data_id': metric.get('data_id', ''),
                'relative_path': metric.get('relative_path', ''),
                'detail_url': metric.get('detail_url', '')
            }
            
            # 메타데이터 (정규화) - 모든 필드를 명시적으로 설정
            metadata = details.get('metadata', {})
            converted.update({
                'reporting_format': metadata.get('Reporting Format'),
                'metric_type': metadata.get('Metric Type'),
                'metric_level': metadata.get('Metric Level'),
                'iris_citation': metadata.get('IRIS Metric Citation')
            })
            
            # 상세 정보를 다국어 JSON 구조로 변환 - 모든 필드를 명시적으로 설정
            
            # 정의
            converted['definition'] = {
                'en': details.get('definition'),
                'ko': None  # 추후 번역 추가
            } if 'definition' in details else None
            
            # 사용 가이드라인
            converted['usage_guidance'] = {
                'en': details.get('usage_guidance'),
                'ko': None  # 추후 번역 추가
            } if 'usage_guidance' in details else None
            
            # 임팩트 카테고리
            converted['impact_categories'] = {
                'en': details.get('impact_categories'),
                'ko': None  # 추후 번역 추가
            } if 'impact_categories' in details else None
            
            # SDG 목표
            converted['sdg_goals'] = {
                'en': details.get('sdg_goals'),
                'ko': None  # 추후 번역 추가
            } if 'sdg_goals' in details else None
            
            # 메트릭 히스토리 (영문만)
            converted['metric_history'] = details.get('metric_history')
            
            # 관련 메트릭
            converted['related_metrics'] = details.get('related_metrics')
            
            # 메타 정보 - 모든 필드를 명시적으로 설정
            converted.update({
                'scraped_at': details.get('scraped_at'),
                'translated_at': None,
                'success': details.get('success', True),
                'version': 'v5.3b'
            })
            
            return converted
            
        except Exception as e:
            logger.error(f"메트릭 {metric.get('data_id', 'unknown')} 변환 실패: {e}")
            return None
    
    def convert_all_metrics(self, data: Dict) -> List[Dict]:
        """모든 메트릭을 변환합니다."""
        metrics = data.get('metrics', [])
        converted_metrics = []
        
        logger.info(f"총 {len(metrics)}개 메트릭 변환 시작...")
        
        for i, metric in enumerate(metrics):
            converted = self.convert_metric_to_supabase_format(metric)
            if converted:
                converted_metrics.append(converted)
                
            if (i + 1) % 100 == 0:
                logger.info(f"{i + 1}/{len(metrics)} 변환 완료")
        
        logger.info(f"변환 완료: {len(converted_metrics)}/{len(metrics)}개 성공")
        return converted_metrics
    
    def save_converted_data(self, converted_metrics: List[Dict], filename: str = "data/iris_metrics_supabase_format.json"):
        """변환된 데이터를 저장합니다."""
        try:
            output_data = {
                "metadata": {
                    "total_metrics": len(converted_metrics),
                    "converted_at": datetime.now().isoformat(),
                    "format": "supabase_ready",
                    "language_support": ["en", "ko"],
                    "version": "v5.3b"
                },
                "metrics": converted_metrics
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"변환된 데이터 저장: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"저장 실패: {e}")
            return None
    
    def generate_sample_queries(self, converted_metrics: List[Dict]):
        """샘플 쿼리들을 생성합니다."""
        
        # Impact Categories 분석
        impact_categories = set()
        sdg_goals = set()
        metric_types = set()
        
        for metric in converted_metrics:
            # 메트릭 타입
            if metric.get('metric_type'):
                metric_types.add(metric['metric_type'])
            
            # Impact Categories 추출
            impact_cat = metric.get('impact_categories')
            if impact_cat and isinstance(impact_cat, dict):
                en_data = impact_cat.get('en')
                if en_data and 'content' in en_data and 'headings' in en_data['content']:
                    for heading in en_data['content']['headings']:
                        if 'text' in heading:
                            impact_categories.add(heading['text'])
            
            # SDG 목표 추출
            sdg = metric.get('sdg_goals')
            if sdg and isinstance(sdg, dict):
                en_data = sdg.get('en')
                if en_data and 'content' in en_data and 'headings' in en_data['content']:
                    for heading in en_data['content']['headings']:
                        if 'text' in heading:
                            sdg_goals.add(heading['text'])
        
        # 샘플 쿼리 파일 생성
        queries = f"""-- IRIS+ 메트릭 데이터 샘플 쿼리들
-- 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

-- 1. 모든 Impact Categories 조회
SELECT 
    jsonb_array_elements_text(
        jsonb_path_query_array(impact_categories, '$.en.content.headings[*].text')
    ) as category_name,
    COUNT(*) as metric_count
FROM iris_metrics 
WHERE impact_categories IS NOT NULL
GROUP BY category_name
ORDER BY metric_count DESC;

-- 2. 특정 카테고리 메트릭 조회 (예: Water)
SELECT title_en, data_id, metric_type
FROM iris_metrics 
WHERE impact_categories @> '{{"en": {{"content": {{"headings": [{{"text": "Water"}}]}}}}}}';

-- 3. SDG 목표별 메트릭 통계
SELECT 
    jsonb_array_elements_text(
        jsonb_path_query_array(sdg_goals, '$.en.content.headings[*].text')
    ) as sdg_name,
    COUNT(*) as metric_count
FROM iris_metrics 
WHERE sdg_goals IS NOT NULL
GROUP BY sdg_name
ORDER BY metric_count DESC;

-- 4. 메트릭 타입별 분포
SELECT metric_type, COUNT(*) as count
FROM iris_metrics 
GROUP BY metric_type
ORDER BY count DESC;

-- 5. 정의에서 키워드 검색 (영문)
SELECT title_en, data_id, definition->>'en' as definition_en
FROM iris_metrics 
WHERE definition->>'en' ILIKE '%water%'
LIMIT 10;

-- 6. 사용 가이드라인에서 검색
SELECT title_en, data_id
FROM iris_metrics 
WHERE usage_guidance->'en'->'content'->>'raw_text' ILIKE '%measurement%'
LIMIT 10;

-- 7. 복합 조건 검색 (Water 카테고리 + Clean Water SDG)
SELECT title_en, data_id, metric_type
FROM iris_metrics 
WHERE impact_categories @> '{{"en": {{"content": {{"headings": [{{"text": "Water"}}]}}}}}}' 
  AND sdg_goals @> '{{"en": {{"content": {{"headings": [{{"text": "Clean Water and Sanitation"}}]}}}}}}';

-- 8. 최근 업데이트된 메트릭들
SELECT title_en, data_id, updated_at
FROM iris_metrics 
ORDER BY updated_at DESC
LIMIT 20;

-- 발견된 데이터 통계:
-- Impact Categories: {len(impact_categories)}개
-- SDG Goals: {len(sdg_goals)}개  
-- Metric Types: {len(metric_types)}개
-- 주요 Impact Categories: {', '.join(list(impact_categories)[:10])}
-- 주요 SDG Goals: {', '.join(list(sdg_goals)[:10])}
-- Metric Types: {', '.join(metric_types)}
"""
        
        with open('supabase_sample_queries.sql', 'w', encoding='utf-8') as f:
            f.write(queries)
        
        logger.info("샘플 쿼리 파일 생성: supabase_sample_queries.sql")

def main():
    """메인 실행 함수"""
    # 환경변수 파일 로드 (선택사항)
    load_env_file()
    
    converter = SupabaseConverter()
    
    # 데이터 로드
    logger.info("수집된 데이터 로드 중...")
    data = converter.load_collected_data()
    
    if not data:
        print("❌ 데이터를 로드할 수 없습니다.")
        return
    
    print(f"🚀 {len(data['metrics'])}개 메트릭을 Supabase 형식으로 변환 시작")
    
    # 변환
    converted_metrics = converter.convert_all_metrics(data)
    
    if converted_metrics:
        # 저장
        filename = converter.save_converted_data(converted_metrics)
        
        # 샘플 쿼리 생성
        converter.generate_sample_queries(converted_metrics)
        
        print(f"\n✅ 변환 완료!")
        print(f"📁 변환된 데이터: {filename}")
        print(f"📊 성공: {len(converted_metrics)}개")
        print(f"📝 샘플 쿼리: supabase_sample_queries.sql")
        
        # 통계 출력
        successful = len([m for m in converted_metrics if m.get('success', True)])
        print(f"📈 성공률: {successful}/{len(converted_metrics)} ({successful/len(converted_metrics)*100:.1f}%)")
        
    else:
        print("❌ 변환 실패")

if __name__ == "__main__":
    main()
