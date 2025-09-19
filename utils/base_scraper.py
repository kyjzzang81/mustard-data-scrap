"""
데이터 스크래핑을 위한 베이스 클래스
"""
import time
import logging
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from config.settings import SCRAPING_CONFIG, DATA_DIR, LOGS_DIR

class BaseScraper(ABC):
    """모든 스크래퍼의 베이스 클래스"""
    
    def __init__(self, name: str):
        self.name = name
        self.setup_logging()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': SCRAPING_CONFIG['user_agent']
        })
    
    def setup_logging(self):
        """로깅 설정"""
        log_file = LOGS_DIR / f"{self.name.lower()}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.name)
    
    def make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """HTTP 요청을 안전하게 수행"""
        for attempt in range(SCRAPING_CONFIG['max_retries']):
            try:
                response = self.session.get(
                    url, 
                    timeout=SCRAPING_CONFIG['timeout'],
                    **kwargs
                )
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                self.logger.warning(f"요청 실패 (시도 {attempt + 1}/{SCRAPING_CONFIG['max_retries']}): {e}")
                if attempt < SCRAPING_CONFIG['max_retries'] - 1:
                    time.sleep(2 ** attempt)  # 지수 백오프
                else:
                    self.logger.error(f"최대 재시도 횟수 초과: {url}")
                    return None
    
    def delay(self):
        """요청 간 딜레이"""
        time.sleep(SCRAPING_CONFIG['delay_between_requests'])
    
    def save_to_json(self, data: Dict[str, Any], filename: str) -> Path:
        """데이터를 JSON 파일로 저장"""
        filepath = DATA_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"데이터 저장 완료: {filepath}")
        return filepath
    
    def load_from_json(self, filename: str) -> Optional[Dict[str, Any]]:
        """JSON 파일에서 데이터 로드"""
        filepath = DATA_DIR / filename
        if not filepath.exists():
            self.logger.warning(f"파일이 존재하지 않습니다: {filepath}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @abstractmethod
    def scrape(self, **kwargs) -> Dict[str, Any]:
        """스크래핑 실행 (서브클래스에서 구현)"""
        pass
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """스크래핑 실행 및 로깅"""
        self.logger.info(f"{self.name} 스크래핑 시작")
        start_time = time.time()
        
        try:
            result = self.scrape(**kwargs)
            elapsed_time = time.time() - start_time
            self.logger.info(f"{self.name} 스크래핑 완료 (소요시간: {elapsed_time:.2f}초)")
            return result
        except Exception as e:
            self.logger.error(f"{self.name} 스크래핑 실패: {e}")
            raise
