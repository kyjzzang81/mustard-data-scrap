"""
데이터 스크래핑 프로젝트 공통 설정
"""
import os
from pathlib import Path
from utils.env_loader import load_environment, validate_environment

# 환경 변수 로드
env_config = load_environment()

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
    "url": env_config["SUPABASE_URL"],
    "anon_key": env_config["SUPABASE_ANON_KEY"],
    "service_role_key": env_config["SUPABASE_SERVICE_ROLE_KEY"],
    "storage_bucket": env_config["SUPABASE_STORAGE_BUCKET"],
    "backup_bucket": env_config["SUPABASE_BACKUP_BUCKET"]
}

# 데이터베이스 설정
DATABASE_CONFIG = {
    "url": env_config["DATABASE_URL"]
}

# API 설정
API_CONFIG = {
    "host": env_config["API_HOST"],
    "port": env_config["API_PORT"],
    "debug": env_config["API_DEBUG"]
}

# 로깅 설정
LOGGING_CONFIG = {
    "level": env_config["LOG_LEVEL"],
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": env_config["LOG_FILE"]
}

# 파일 관리 설정
FILE_CONFIG = {
    "max_size_mb": env_config["MAX_FILE_SIZE_MB"],
    "allowed_types": env_config["ALLOWED_FILE_TYPES"],
    "storage_prefix": env_config["STORAGE_FOLDER_PREFIX"]
}

# 백업 설정
BACKUP_CONFIG = {
    "retention_days": env_config["BACKUP_RETENTION_DAYS"],
    "auto_enabled": env_config["AUTO_BACKUP_ENABLED"]
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

# 환경 변수 유효성 검사
def validate_config():
    """설정 유효성 검사"""
    return validate_environment(env_config)

if __name__ == "__main__":
    # 설정 검증
    is_valid = validate_config()
    
    if is_valid:
        print("✅ 모든 설정이 올바르게 구성되었습니다.")
        print(f"📊 Supabase URL: {SUPABASE_CONFIG['url']}")
        print(f"📁 Storage Bucket: {SUPABASE_CONFIG['storage_bucket']}")
        print(f"🔧 API Host: {API_CONFIG['host']}:{API_CONFIG['port']}")
    else:
        print("❌ 설정을 확인하고 수정하세요.")
