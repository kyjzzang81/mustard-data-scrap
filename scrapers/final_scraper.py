#!/usr/bin/env python3
"""
metric-box 구조를 기반으로 한 최종 IRIS+ 메트릭 스크래퍼
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_temp/final_scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinalScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def load_base_metrics(self, filename: str = "data/iris_metrics.json") -> Dict:
        """기존 메트릭 데이터를 로드합니다."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"기존 JSON 파일 로드 실패: {e}")
            return {}
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """웹페이지 내용을 가져옵니다."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"페이지 요청 실패 {url}: {e}")
            return None
    
    def extract_section_content(self, section) -> Dict:
        """section 태그에서 내용을 추출합니다."""
        content = {
            'paragraphs': [],
            'lists': [],
            'headings': [],
            'other_elements': [],
            'raw_text': ''
        }
        
        try:
            # 모든 제목 요소 추출 (h1-h6)
            headings = section.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for h in headings:
                text = h.get_text(strip=True)
                if text:
                    content['headings'].append({
                        'tag': h.name,
                        'text': text
                    })
            
            # 모든 단락 추출
            paragraphs = section.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text:
                    content['paragraphs'].append(text)
            
            # 모든 리스트 추출
            lists = section.find_all(['ul', 'ol'])
            for lst in lists:
                list_items = []
                for li in lst.find_all('li'):
                    item_text = li.get_text(strip=True)
                    if item_text:
                        list_items.append(item_text)
                
                if list_items:
                    content['lists'].append({
                        'type': lst.name,
                        'items': list_items
                    })
            
            # 기타 중요한 요소들 (div, span 등에서 직접 텍스트)
            other_elements = section.find_all(['div', 'span'])
            for elem in other_elements:
                # 자식 요소가 없고 직접 텍스트만 있는 경우
                if not elem.find_all() and elem.get_text(strip=True):
                    text = elem.get_text(strip=True)
                    # 이미 다른 곳에서 수집되지 않은 텍스트만 추가
                    if text not in content['raw_text']:
                        content['other_elements'].append({
                            'tag': elem.name,
                            'text': text,
                            'class': elem.get('class', [])
                        })
            
            # 전체 텍스트 (백업용)
            content['raw_text'] = section.get_text(separator=' ', strip=True)
            
        except Exception as e:
            logger.error(f"섹션 내용 추출 중 오류: {e}")
        
        return content
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """section#metadata에서 메타데이터를 추출합니다."""
        metadata = {}
        
        try:
            # section#metadata 찾기
            metadata_section = soup.find('section', id='metadata')
            if metadata_section:
                # ul 태그에서 메타데이터 추출
                metadata_list = metadata_section.find('ul')
                if metadata_list:
                    for li in metadata_list.find_all('li'):
                        text = li.get_text(strip=True)
                        if 'Reporting Format' in text:
                            metadata['Reporting Format'] = text.replace('Reporting Format', '').strip()
                        elif 'Metric Type' in text:
                            metadata['Metric Type'] = text.replace('Metric Type', '').strip()
                        elif 'Metric Level' in text:
                            metadata['Metric Level'] = text.replace('Metric Level', '').strip()
                        elif 'IRIS Metric Citation' in text:
                            metadata['IRIS Metric Citation'] = text.replace('IRIS Metric Citation', '').strip()
        except Exception as e:
            logger.error(f"메타데이터 추출 중 오류: {e}")
        
        return metadata

    def extract_metric_details(self, soup: BeautifulSoup) -> Dict:
        """metric-box 구조를 기반으로 상세 정보를 추출합니다."""
        content_area = soup.find(class_='content-area')
        if not content_area:
            return {}
        
        details = {}
        
        # 메타데이터 추출
        details['metadata'] = self.extract_metadata(soup)
        
        # 모든 metric-box 찾기
        metric_boxes = content_area.find_all('div', class_='metric-box')
        
        for box in metric_boxes:
            try:
                # header에서 제목 추출
                header = box.find(['header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if not header:
                    continue
                
                section_title = header.get_text(strip=True)
                
                # section에서 내용 추출
                section = box.find('section')
                if section:
                    section_content = self.extract_section_content(section)
                else:
                    # section이 없으면 box에서 직접 추출
                    section_content = self.extract_section_content(box)
                
                # 섹션별로 적절한 키 생성
                if 'Account Value' in section_title or any(id_pattern in section_title for id_pattern in ['(PI', '(FP', '(OI', '(PD', '(OD']):
                    # 메트릭 정의 섹션
                    details['definition'] = {
                        'title': section_title,
                        'content': section_content
                    }
                elif 'Usage Guidance' in section_title:
                    details['usage_guidance'] = {
                        'title': section_title,
                        'content': section_content
                    }
                elif 'Impact Categories' in section_title:
                    details['impact_categories'] = {
                        'title': section_title,
                        'content': section_content
                    }
                elif 'SDG Goals' in section_title:
                    details['sdg_goals'] = {
                        'title': section_title,
                        'content': section_content
                    }
                elif 'Metric History' in section_title:
                    details['metric_history'] = {
                        'title': section_title,
                        'content': section_content
                    }
                elif 'Related metrics' in section_title:
                    details['related_metrics'] = {
                        'title': section_title,
                        'content': section_content
                    }
                else:
                    # 기타 섹션들
                    key = section_title.lower().replace(' ', '_').replace('&', 'and')
                    details[key] = {
                        'title': section_title,
                        'content': section_content
                    }
                
            except Exception as e:
                logger.error(f"metric-box 처리 중 오류: {e}")
                continue
        
        return details
    
    def process_single_metric(self, metric: Dict) -> Dict:
        """단일 메트릭의 상세 정보를 처리합니다."""
        try:
            # 상세 페이지 가져오기
            soup = self.get_page_content(metric['detail_url'])
            if soup is None:
                return {
                    **metric,
                    'details': {
                        'success': False,
                        'error': 'Page load failed',
                        'scraped_at': datetime.now().isoformat()
                    }
                }
            
            # 상세 정보 추출
            details = self.extract_metric_details(soup)
            details['success'] = True
            details['scraped_at'] = datetime.now().isoformat()
            
            return {
                **metric,
                'details': details
            }
            
        except Exception as e:
            logger.error(f"메트릭 {metric['data_id']} 처리 실패: {e}")
            return {
                **metric,
                'details': {
                    'success': False,
                    'error': str(e),
                    'scraped_at': datetime.now().isoformat()
                }
            }
    
    def process_all_metrics(self, base_data: Dict, batch_size: int = 50) -> Dict:
        """모든 메트릭을 배치 단위로 처리합니다."""
        metrics = base_data['metrics']
        total_metrics = len(metrics)
        
        logger.info(f"전체 {total_metrics}개 메트릭 처리 시작")
        
        for start_idx in range(0, total_metrics, batch_size):
            end_idx = min(start_idx + batch_size, total_metrics)
            batch_num = start_idx // batch_size + 1
            total_batches = (total_metrics + batch_size - 1) // batch_size
            
            logger.info(f"배치 {batch_num}/{total_batches} 처리 중 ({start_idx+1}-{end_idx})")
            
            for i in range(start_idx, end_idx):
                current_progress = i - start_idx + 1
                batch_total = end_idx - start_idx
                
                logger.info(f"[{current_progress}/{batch_total}] {metrics[i]['title']} ({metrics[i]['data_id']})")
                
                # 메트릭 처리
                metrics[i] = self.process_single_metric(metrics[i])
                
                success = metrics[i]['details']['success']
                logger.info(f"처리 {'성공' if success else '실패'}")
                
                # 서버 부하 방지
                time.sleep(1.5)
            
            # 중간 저장
            temp_filename = f"data_temp/final_metrics_temp_{batch_num}.json"
            with open(temp_filename, 'w', encoding='utf-8') as f:
                json.dump(base_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"배치 {batch_num} 완료 - 중간 저장됨")
            
            # 배치 간 휴식
            if end_idx < total_metrics:
                logger.info("다음 배치를 위해 3초 대기...")
                time.sleep(3)
        
        return base_data

def main():
    """테스트용 메인 함수 - 처음 5개만 처리"""
    scraper = FinalScraper()
    
    # 기존 데이터 로드
    logger.info("기존 메트릭 데이터 로드 중...")
    base_data = scraper.load_base_metrics()
    
    if not base_data:
        print("❌ 기존 메트릭 데이터를 로드할 수 없습니다.")
        return
    
    print(f"🧪 테스트: 처음 5개 메트릭 처리")
    
    # 처음 5개만 테스트
    test_metrics = base_data['metrics'][:5]
    for i, metric in enumerate(test_metrics):
        logger.info(f"[{i+1}/5] {metric['title']} ({metric['data_id']})")
        test_metrics[i] = scraper.process_single_metric(metric)
        success = test_metrics[i]['details']['success']
        logger.info(f"처리 {'성공' if success else '실패'}")
        time.sleep(1)
    
    # 결과 저장
    base_data['metrics'] = test_metrics + base_data['metrics'][5:]
    with open('data_temp/final_test_metrics.json', 'w', encoding='utf-8') as f:
        json.dump(base_data, f, ensure_ascii=False, indent=2)
    
    # 결과 확인
    successful = sum(1 for m in test_metrics if m['details']['success'])
    print(f"\n✅ 테스트 완료: {successful}/5개 성공")
    
    # 샘플 출력
    if successful > 0:
        sample = test_metrics[0]
        if sample['details']['success']:
            print(f"\n📋 샘플: {sample['title']}")
            
            details = sample['details']
            for key, value in details.items():
                if key in ['success', 'scraped_at', 'error']:
                    continue
                if isinstance(value, dict) and 'content' in value:
                    content = value['content']
                    para_count = len(content.get('paragraphs', []))
                    list_count = len(content.get('lists', []))
                    print(f"  {value['title']}: 단락 {para_count}개, 리스트 {list_count}개")

if __name__ == "__main__":
    main()
