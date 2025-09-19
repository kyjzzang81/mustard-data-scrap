"""
스크래퍼 관리자 - 여러 스크래퍼를 통합 관리
"""
import importlib
from typing import Dict, List, Any, Optional
from pathlib import Path
from config.settings import SUPPORTED_SCRAPERS, DATA_DIR
from utils.base_scraper import BaseScraper

class ScraperManager:
    """여러 스크래퍼를 관리하는 클래스"""
    
    def __init__(self):
        self.scrapers: Dict[str, BaseScraper] = {}
        self.results: Dict[str, Any] = {}
    
    def register_scraper(self, scraper_type: str, scraper_instance: BaseScraper):
        """스크래퍼 등록"""
        self.scrapers[scraper_type] = scraper_instance
        print(f"✅ {scraper_type} 스크래퍼 등록됨")
    
    def load_scraper(self, scraper_type: str) -> Optional[BaseScraper]:
        """설정된 스크래퍼 로드"""
        if scraper_type not in SUPPORTED_SCRAPERS:
            print(f"❌ 지원하지 않는 스크래퍼 타입: {scraper_type}")
            return None
        
        config = SUPPORTED_SCRAPERS[scraper_type]
        try:
            module = importlib.import_module(config['module'])
            scraper_class = getattr(module, config['class'])
            return scraper_class()
        except Exception as e:
            print(f"❌ 스크래퍼 로드 실패 ({scraper_type}): {e}")
            return None
    
    def run_scraper(self, scraper_type: str, **kwargs) -> Optional[Dict[str, Any]]:
        """특정 스크래퍼 실행"""
        if scraper_type not in self.scrapers:
            scraper = self.load_scraper(scraper_type)
            if not scraper:
                return None
            self.register_scraper(scraper_type, scraper)
        
        print(f"🚀 {scraper_type} 스크래퍼 실행 중...")
        result = self.scrapers[scraper_type].run(**kwargs)
        self.results[scraper_type] = result
        return result
    
    def run_all(self, scraper_types: List[str], **kwargs) -> Dict[str, Any]:
        """여러 스크래퍼 순차 실행"""
        print(f"🔄 {len(scraper_types)}개 스크래퍼 실행 시작")
        all_results = {}
        
        for scraper_type in scraper_types:
            result = self.run_scraper(scraper_type, **kwargs)
            if result:
                all_results[scraper_type] = result
                print(f"✅ {scraper_type} 완료")
            else:
                print(f"❌ {scraper_type} 실패")
        
        return all_results
    
    def get_available_scrapers(self) -> List[str]:
        """사용 가능한 스크래퍼 목록 반환"""
        return list(SUPPORTED_SCRAPERS.keys())
    
    def get_scraper_info(self, scraper_type: str) -> Optional[Dict[str, str]]:
        """스크래퍼 정보 반환"""
        return SUPPORTED_SCRAPERS.get(scraper_type)
    
    def list_results(self) -> Dict[str, Any]:
        """실행 결과 목록 반환"""
        return self.results.copy()
