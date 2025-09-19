"""
Supabase 데이터베이스 설정 스크립트
"""
import os
from supabase import create_client, Client
from config.settings import SUPABASE_CONFIG

def create_supabase_client() -> Client:
    """Supabase 클라이언트 생성"""
    url = SUPABASE_CONFIG["url"]
    key = SUPABASE_CONFIG["service_role_key"]
    
    if not url or not key:
        raise ValueError("Supabase 설정이 필요합니다. .env 파일을 확인하세요.")
    
    return create_client(url, key)

def create_sdgs_tables():
    """SDGs 테이블들 생성"""
    print("🏗️ SDGs 테이블 생성 중...")
    
    # SQL 스키마 파일 읽기
    with open("config/sdgs_schema.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    # SQL을 세미콜론으로 분리하여 각 쿼리 실행
    queries = [q.strip() for q in schema_sql.split(';') if q.strip()]
    
    supabase = create_supabase_client()
    
    for i, query in enumerate(queries, 1):
        if query:
            try:
                print(f"  📝 쿼리 {i}/{len(queries)} 실행 중...")
                result = supabase.rpc('exec_sql', {'sql': query})
                print(f"    ✅ 성공")
            except Exception as e:
                print(f"    ⚠️ 경고: {e}")
                # 일부 쿼리는 이미 존재할 수 있으므로 경고만 표시
    
    print("✅ SDGs 테이블 생성 완료!")

def test_connection():
    """Supabase 연결 테스트"""
    print("🔗 Supabase 연결 테스트 중...")
    
    try:
        supabase = create_supabase_client()
        
        # 간단한 쿼리로 연결 테스트
        result = supabase.table('sdg_goals').select('*').limit(1).execute()
        
        print("✅ Supabase 연결 성공!")
        print(f"📊 SDG Goals 테이블에서 {len(result.data)}개 레코드 발견")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return False

def check_tables():
    """생성된 테이블들 확인"""
    print("📋 생성된 테이블들 확인 중...")
    
    try:
        supabase = create_supabase_client()
        
        tables = [
            'sdg_goals',
            'sdg_indicators', 
            'sdg_metadata_files',
            'sdg_framework_data',
            'sdg_country_data'
        ]
        
        for table in tables:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"  ✅ {table}: {len(result.data)}개 레코드")
            except Exception as e:
                print(f"  ❌ {table}: {e}")
        
    except Exception as e:
        print(f"❌ 테이블 확인 실패: {e}")

def main():
    print("🚀 Supabase 데이터베이스 설정 시작...")
    
    # 1. 연결 테스트
    if not test_connection():
        return
    
    # 2. 테이블 생성
    create_sdgs_tables()
    
    # 3. 테이블 확인
    check_tables()
    
    print("\n🎉 Supabase 데이터베이스 설정 완료!")
    print("이제 SDGs 데이터를 업로드할 수 있습니다.")

if __name__ == "__main__":
    main()
