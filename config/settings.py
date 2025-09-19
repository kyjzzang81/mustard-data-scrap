"""
데이터 스크래핑 프로젝트 공통 설정
"""
import os
from pathlib import Path

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent

# 데이터 디렉토리
DATA_DIR = PROJECT_ROOT / "data"
TEMP_DIR = PROJECT_ROOT / "data_temp"
LOGS_DIR = PROJECT_ROOT / "logs"

# 출력 디렉토리 생성
DATA_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# 스크래핑 설정
SCRAPING_CONFIG = {
    "delay_between_requests": 1.0,  # 요청 간 딜레이 (초)
    "max_retries": 3,  # 최대 재시도 횟수
    "timeout": 30,  # 요청 타임아웃 (초)
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Supabase 설정
SUPABASE_CONFIG = {
    "url": os.getenv("SUPABASE_URL"),
    "anon_key": os.getenv("SUPABASE_ANON_KEY"),
    "service_role_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY")
}

# 로깅 설정
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "scraping.log"
}

# 지원하는 스크래퍼 타입
SUPPORTED_SCRAPERS = {
    "iris": {
        "name": "IRIS+ Metrics",
        "module": "scrapers.iris_scraper",
        "class": "IRISScraper",
        "description": "IRIS+ 임팩트 투자 메트릭 데이터 수집"
    },
    "iris_detail": {
        "name": "IRIS+ Detail Analysis",
        "module": "scrapers.detail_analyzer", 
        "class": "DetailAnalyzer",
        "description": "IRIS+ 메트릭 상세 정보 분석"
    }
}
