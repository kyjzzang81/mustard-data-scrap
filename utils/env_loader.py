"""
환경 변수 로더
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """환경 변수 로드"""
    # .env 파일 경로 설정
    env_file = Path(__file__).parent.parent / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ 환경 변수 로드됨: {env_file}")
    else:
        print(f"⚠️ .env 파일이 없습니다: {env_file}")
        print("   .env.example을 .env로 복사하고 설정값을 입력하세요.")
    
    return {
        # Supabase 설정
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
        "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        "SUPABASE_STORAGE_BUCKET": os.getenv("SUPABASE_STORAGE_BUCKET", "sdgs-files"),
        "SUPABASE_BACKUP_BUCKET": os.getenv("SUPABASE_BACKUP_BUCKET", "sdgs-backup"),
        
        # 데이터베이스 설정
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        
        # API 설정
        "API_HOST": os.getenv("API_HOST", "0.0.0.0"),
        "API_PORT": int(os.getenv("API_PORT", "8000")),
        "API_DEBUG": os.getenv("API_DEBUG", "True").lower() == "true",
        
        # 파일 관리 설정
        "MAX_FILE_SIZE_MB": int(os.getenv("MAX_FILE_SIZE_MB", "100")),
        "ALLOWED_FILE_TYPES": os.getenv("ALLOWED_FILE_TYPES", "pdf,xlsx,xls,json").split(","),
        "STORAGE_FOLDER_PREFIX": os.getenv("STORAGE_FOLDER_PREFIX", "sdgs"),
        
        # 로깅 설정
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "LOG_FILE": os.getenv("LOG_FILE", "logs/scraping.log"),
        
        # 백업 설정
        "BACKUP_RETENTION_DAYS": int(os.getenv("BACKUP_RETENTION_DAYS", "30")),
        "AUTO_BACKUP_ENABLED": os.getenv("AUTO_BACKUP_ENABLED", "True").lower() == "true"
    }

def validate_environment(config: dict) -> bool:
    """환경 변수 유효성 검사"""
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_ROLE_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not config.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("   .env 파일을 확인하고 필요한 값들을 설정하세요.")
        return False
    
    print("✅ 모든 필수 환경 변수가 설정되었습니다.")
    return True

def get_supabase_config():
    """Supabase 설정만 반환"""
    config = load_environment()
    return {
        "url": config["SUPABASE_URL"],
        "anon_key": config["SUPABASE_ANON_KEY"],
        "service_role_key": config["SUPABASE_SERVICE_ROLE_KEY"]
    }

if __name__ == "__main__":
    # 환경 변수 로드 및 검증
    config = load_environment()
    
    print("\n📋 로드된 환경 변수:")
    for key, value in config.items():
        if "KEY" in key or "URL" in key:
            # 보안상 민감한 정보는 일부만 표시
            display_value = f"{str(value)[:20]}..." if value and len(str(value)) > 20 else value
        else:
            display_value = value
        print(f"  {key}: {display_value}")
    
    # 유효성 검사
    is_valid = validate_environment(config)
    
    if is_valid:
        print("\n✅ 환경 설정이 올바르게 구성되었습니다.")
    else:
        print("\n❌ 환경 설정을 확인하고 수정하세요.")
