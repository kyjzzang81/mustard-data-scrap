#!/usr/bin/env python3
"""
IRIS+ 메트릭 상세 페이지 분석 도구
마지막 30개 메트릭의 detail_url에서 .content-area 내용을 분석합니다.
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_temp/detail_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DetailAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def load_metrics_data(self, filename: str = "data/iris_metrics.json") -> List[Dict]:
        """JSON 파일에서 메트릭 데이터를 로드합니다."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data['metrics']
        except Exception as e:
            logger.error(f"JSON 파일 로드 실패: {e}")
            return []
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """웹페이지 내용을 가져옵니다."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"페이지 요청 실패 {url}: {e}")
            return None
    
    def analyze_content_area(self, soup: BeautifulSoup, metric_info: Dict) -> Dict:
        """content-area 내용을 분석합니다."""
        analysis = {
            'title': metric_info['title'],
            'data_id': metric_info['data_id'],
            'url': metric_info['detail_url'],
            'content_found': False,
            'elements': {},
            'text_content': "",
            'error': None
        }
        
        try:
            # .content-area 요소 찾기
            content_area = soup.find(class_='content-area')
            if not content_area:
                analysis['error'] = "content-area 클래스를 찾을 수 없음"
                return analysis
            
            analysis['content_found'] = True
            
            # 다양한 요소들 분석
            elements = analysis['elements']
            
            # 제목들 (h1, h2, h3 등)
            headings = content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if headings:
                elements['headings'] = [{'tag': h.name, 'text': h.get_text(strip=True)} for h in headings]
            
            # 단락들
            paragraphs = content_area.find_all('p')
            if paragraphs:
                elements['paragraphs'] = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
            
            # 리스트들
            lists = content_area.find_all(['ul', 'ol'])
            if lists:
                elements['lists'] = []
                for lst in lists:
                    items = [li.get_text(strip=True) for li in lst.find_all('li')]
                    elements['lists'].append({'type': lst.name, 'items': items})
            
            # 테이블들
            tables = content_area.find_all('table')
            if tables:
                elements['tables'] = len(tables)
            
            # 링크들
            links = content_area.find_all('a', href=True)
            if links:
                elements['links'] = [{'text': a.get_text(strip=True), 'href': a['href']} for a in links]
            
            # 전체 텍스트 내용 (요약용)
            analysis['text_content'] = content_area.get_text(separator=' ', strip=True)[:500] + "..."
            
            # 특별한 클래스들 찾기
            special_elements = content_area.find_all(class_=True)
            unique_classes = set()
            for elem in special_elements:
                if elem.get('class'):
                    unique_classes.update(elem['class'])
            
            if unique_classes:
                elements['css_classes'] = sorted(list(unique_classes))
            
        except Exception as e:
            analysis['error'] = f"분석 중 오류: {str(e)}"
        
        return analysis
    
    def analyze_last_n_metrics(self, n: int = 30) -> List[Dict]:
        """마지막 n개 메트릭의 상세 페이지를 분석합니다."""
        logger.info(f"마지막 {n}개 메트릭 상세 페이지 분석 시작...")
        
        # 메트릭 데이터 로드
        metrics = self.load_metrics_data()
        if not metrics:
            logger.error("메트릭 데이터를 로드할 수 없습니다.")
            return []
        
        # 마지막 n개 선택
        last_metrics = metrics[-n:]
        logger.info(f"분석할 메트릭: {len(last_metrics)}개")
        
        results = []
        
        for i, metric in enumerate(last_metrics, 1):
            logger.info(f"[{i}/{len(last_metrics)}] 분석 중: {metric['title']} ({metric['data_id']})")
            
            # 상세 페이지 가져오기
            soup = self.get_page_content(metric['detail_url'])
            if soup is None:
                logger.warning(f"페이지 로드 실패: {metric['detail_url']}")
                continue
            
            # content-area 분석
            analysis = self.analyze_content_area(soup, metric)
            results.append(analysis)
            
            logger.info(f"분석 완료: {'성공' if analysis['content_found'] else '실패'}")
            
            # 서버 부하 방지
            time.sleep(1)
        
        logger.info(f"전체 분석 완료: {len(results)}개 결과")
        return results
    
    def save_analysis_results(self, results: List[Dict], filename: str = "data_temp/detail_analysis.json"):
        """분석 결과를 JSON 파일로 저장합니다."""
        try:
            output_data = {
                "metadata": {
                    "total_analyzed": len(results),
                    "analyzed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "successful_analyses": len([r for r in results if r['content_found']])
                },
                "analyses": results
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"분석 결과가 {filename}에 저장되었습니다.")
            return filename
            
        except Exception as e:
            logger.error(f"결과 저장 실패: {e}")
            return None
    
    def print_summary(self, results: List[Dict]):
        """분석 결과 요약을 출력합니다."""
        print("\n" + "="*80)
        print("📊 CONTENT-AREA 분석 결과 요약")
        print("="*80)
        
        successful = [r for r in results if r['content_found']]
        failed = [r for r in results if not r['content_found']]
        
        print(f"✅ 성공: {len(successful)}개")
        print(f"❌ 실패: {len(failed)}개")
        print(f"📈 성공률: {len(successful)/len(results)*100:.1f}%")
        
        if successful:
            print(f"\n📋 발견된 공통 요소들:")
            
            # 공통 CSS 클래스 분석
            all_classes = set()
            for result in successful:
                if 'css_classes' in result['elements']:
                    all_classes.update(result['elements']['css_classes'])
            
            if all_classes:
                print(f"🎨 CSS 클래스들: {', '.join(sorted(list(all_classes))[:10])}...")
            
            # 평균 요소 개수
            avg_paragraphs = sum(len(r['elements'].get('paragraphs', [])) for r in successful) / len(successful)
            avg_headings = sum(len(r['elements'].get('headings', [])) for r in successful) / len(successful)
            
            print(f"📝 평균 단락 수: {avg_paragraphs:.1f}개")
            print(f"📖 평균 제목 수: {avg_headings:.1f}개")
        
        print("\n" + "="*80)

def main():
    """메인 실행 함수"""
    analyzer = DetailAnalyzer()
    
    # 마지막 30개 메트릭 분석
    results = analyzer.analyze_last_n_metrics(30)
    
    if results:
        # 결과 저장
        filename = analyzer.save_analysis_results(results)
        
        # 요약 출력
        analyzer.print_summary(results)
        
        # 몇 가지 샘플 출력
        print("\n🔍 샘플 분석 결과:")
        for i, result in enumerate(results[:3]):  # 처음 3개만
            print(f"\n{i+1}. {result['title']} ({result['data_id']})")
            if result['content_found']:
                elements = result['elements']
                if 'headings' in elements:
                    print(f"   제목들: {[h['text'] for h in elements['headings'][:3]]}")
                if 'paragraphs' in elements:
                    print(f"   단락 수: {len(elements['paragraphs'])}개")
                print(f"   텍스트 미리보기: {result['text_content'][:100]}...")
            else:
                print(f"   오류: {result['error']}")
        
        if filename:
            print(f"\n📁 전체 결과는 {filename}에서 확인하세요!")
    else:
        print("❌ 분석 결과가 없습니다.")

if __name__ == "__main__":
    main()
