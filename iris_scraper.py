#!/usr/bin/env python3
"""
IRIS+ 메트릭 데이터 스크래핑 도구
https://iris.thegiin.org/metrics/ 에서 메트릭 목록을 수집합니다.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_temp/iris_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IRISScraper:
    def __init__(self, base_url: str = "https://iris.thegiin.org"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """웹페이지 내용을 가져옵니다."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"페이지 요청 실패 {url}: {e}")
            return None
    
    def extract_metrics_from_page(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """페이지에서 메트릭 정보를 추출합니다."""
        metrics = []
        
        # .catalog-list 요소 찾기
        catalog_list = soup.find(class_='catalog-list')
        if not catalog_list:
            logger.warning("catalog-list 요소를 찾을 수 없습니다.")
            return metrics
        
        # a 태그들 찾기
        metric_links = catalog_list.find_all('a', href=True)
        
        for link in metric_links:
            try:
                # href 속성에서 경로 추출
                href = link.get('href', '')
                
                # span.id 요소에서 data-id 추출
                span_id = link.find('span', class_='id')
                data_id = span_id.get('data-id', '') if span_id else ''
                
                # 링크 텍스트 추출 (span 태그 내용 제외)
                text_content = link.get_text(strip=True)
                # (PI1653) 같은 부분 제거
                if '(' in text_content and ')' in text_content:
                    text_content = text_content.split('(')[0].strip()
                
                metric_info = {
                    'title': text_content,
                    'data_id': data_id,
                    'relative_path': href,
                    'detail_url': f"{self.base_url}/metric/5.3b/{data_id.lower()}/" if data_id else ""
                }
                
                metrics.append(metric_info)
                logger.debug(f"메트릭 추출: {metric_info['title']} ({data_id})")
                
            except Exception as e:
                logger.error(f"메트릭 추출 중 오류: {e}")
                continue
        
        return metrics
    
    def scrape_all_pages(self, total_pages: int = 63) -> List[Dict[str, str]]:
        """모든 페이지에서 메트릭을 스크래핑합니다."""
        all_metrics = []
        
        logger.info(f"총 {total_pages}페이지 스크래핑 시작...")
        
        for page_num in range(1, total_pages + 1):
            url = f"{self.base_url}/metrics/?page={page_num}"
            logger.info(f"페이지 {page_num}/{total_pages} 처리 중: {url}")
            
            soup = self.get_page_content(url)
            if soup is None:
                logger.error(f"페이지 {page_num} 스킵")
                continue
            
            page_metrics = self.extract_metrics_from_page(soup)
            all_metrics.extend(page_metrics)
            
            logger.info(f"페이지 {page_num}에서 {len(page_metrics)}개 메트릭 수집")
            
            # 서버 부하 방지를 위한 딜레이
            time.sleep(1)
        
        logger.info(f"스크래핑 완료: 총 {len(all_metrics)}개 메트릭 수집")
        return all_metrics
    
    def save_to_json(self, metrics: List[Dict[str, str]], filename: str = "data/iris_metrics.json"):
        """메트릭 데이터를 JSON 파일로 저장합니다."""
        try:
            # 메타데이터 포함한 최종 구조
            output_data = {
                "metadata": {
                    "source": "https://iris.thegiin.org/metrics/",
                    "total_metrics": len(metrics),
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "version": "IRIS v5.3b"
                },
                "metrics": metrics
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"데이터가 {filename}에 저장되었습니다.")
            return filename
            
        except Exception as e:
            logger.error(f"JSON 저장 실패: {e}")
            return None

def main():
    """메인 실행 함수"""
    scraper = IRISScraper()
    
    # 모든 페이지 스크래핑
    metrics = scraper.scrape_all_pages(total_pages=63)
    
    if metrics:
        # JSON 파일로 저장
        filename = scraper.save_to_json(metrics)
        
        if filename:
            print(f"\n✅ 스크래핑 완료!")
            print(f"📁 파일: {filename}")
            print(f"📊 수집된 메트릭: {len(metrics)}개")
            
            # 샘플 데이터 출력
            if len(metrics) > 0:
                print(f"\n📋 샘플 데이터:")
                for i, metric in enumerate(metrics[:3]):
                    print(f"{i+1}. {metric['title']} ({metric['data_id']})")
                    print(f"   상세 URL: {metric['detail_url']}")
        else:
            print("❌ JSON 저장에 실패했습니다.")
    else:
        print("❌ 메트릭 데이터를 수집하지 못했습니다.")

if __name__ == "__main__":
    main()
