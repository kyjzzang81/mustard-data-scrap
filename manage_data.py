"""
데이터 관리 통합 스크립트
"""
import argparse
import json
from pathlib import Path
from datetime import datetime
from data_catalog import DataCatalog, DataFile
from config.data_sources_config import get_data_source_config

def register_existing_files():
    """기존 파일들을 카탈로그에 등록"""
    catalog = DataCatalog()
    
    # IRIS 데이터 파일들 등록
    iris_files = [
        {
            "filename": "iris_metrics_v1_20241219.json",
            "data_source": "iris",
            "data_type": "metrics",
            "version": "v1",
            "file_path": "data_sources/iris/raw/iris_metrics_v1_20241219.json",
            "description": "IRIS+ 메트릭 기본 목록 (750개)",
            "tags": ["iris", "metrics", "impact_investing"]
        },
        {
            "filename": "iris_metrics_complete_v1_20241219.json",
            "data_source": "iris",
            "data_type": "metrics",
            "version": "v1",
            "file_path": "data_sources/iris/processed/iris_metrics_complete_v1_20241219.json",
            "description": "IRIS+ 메트릭 상세 정보 포함 완전 데이터",
            "tags": ["iris", "metrics", "detailed", "impact_investing"]
        },
        {
            "filename": "iris_metrics_supabase_v1_20241219.json",
            "data_source": "iris",
            "data_type": "metrics",
            "version": "v1",
            "file_path": "data_sources/iris/processed/iris_metrics_supabase_v1_20241219.json",
            "description": "Supabase 형식으로 변환된 IRIS+ 메트릭 데이터",
            "tags": ["iris", "metrics", "supabase", "database"]
        }
    ]
    
    for file_info in iris_files:
        file_path = Path(file_info["file_path"])
        if file_path.exists():
            file_size = file_path.stat().st_size
            data_file = DataFile(
                filename=file_info["filename"],
                data_source=file_info["data_source"],
                data_type=file_info["data_type"],
                version=file_info["version"],
                file_path=file_info["file_path"],
                file_size=file_size,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                description=file_info["description"],
                tags=file_info["tags"]
            )
            catalog.register_data_file(data_file)
        else:
            print(f"⚠️ 파일이 존재하지 않습니다: {file_info['file_path']}")

def list_data_sources():
    """데이터 소스 목록 표시"""
    catalog = DataCatalog()
    sources = catalog.list_data_sources()
    
    print("📊 등록된 데이터 소스:")
    for source in sources:
        print(f"  • {source.code}: {source.name}")
        print(f"    - 설명: {source.description}")
        print(f"    - 웹사이트: {source.website}")
        print(f"    - 업데이트 주기: {source.update_frequency}")
        print()

def list_data_files(data_source=None):
    """데이터 파일 목록 표시"""
    catalog = DataCatalog()
    files = catalog.list_data_files(data_source)
    
    if data_source:
        print(f"📁 {data_source} 데이터 파일:")
    else:
        print("📁 모든 데이터 파일:")
    
    for file in files:
        size_mb = file.file_size / (1024 * 1024)
        print(f"  • {file.filename}")
        print(f"    - 경로: {file.file_path}")
        print(f"    - 크기: {size_mb:.2f}MB")
        print(f"    - 설명: {file.description}")
        print(f"    - 태그: {', '.join(file.tags)}")
        print()

def show_stats():
    """데이터 통계 표시"""
    catalog = DataCatalog()
    stats = catalog.get_file_stats()
    
    print("📊 데이터 통계:")
    print(f"  • 총 파일 수: {stats['total_files']}개")
    print(f"  • 총 용량: {stats['total_size_mb']}MB")
    print()
    
    print("📁 데이터 소스별 파일 수:")
    for source, count in stats['by_source'].items():
        print(f"  • {source}: {count}개")
    print()
    
    print("📄 데이터 유형별 파일 수:")
    for data_type, count in stats['by_type'].items():
        print(f"  • {data_type}: {count}개")

def search_files(query):
    """파일 검색"""
    catalog = DataCatalog()
    results = catalog.search_files(query)
    
    print(f"🔍 '{query}' 검색 결과 ({len(results)}개):")
    for file in results:
        print(f"  • {file.filename} ({file.data_source})")
        print(f"    - {file.description}")

def generate_report():
    """리포트 생성"""
    catalog = DataCatalog()
    report = catalog.generate_report()
    
    report_file = Path("data_catalog_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 리포트 생성됨: {report_file}")
    print(report)

def main():
    parser = argparse.ArgumentParser(description='데이터 관리 도구')
    parser.add_argument('--register', action='store_true', help='기존 파일들 등록')
    parser.add_argument('--list-sources', action='store_true', help='데이터 소스 목록')
    parser.add_argument('--list-files', help='데이터 파일 목록 (소스 지정 가능)')
    parser.add_argument('--stats', action='store_true', help='데이터 통계')
    parser.add_argument('--search', help='파일 검색')
    parser.add_argument('--report', action='store_true', help='리포트 생성')
    
    args = parser.parse_args()
    
    if args.register:
        register_existing_files()
    elif args.list_sources:
        list_data_sources()
    elif args.list_files is not None:
        list_data_files(args.list_files if args.list_files else None)
    elif args.stats:
        show_stats()
    elif args.search:
        search_files(args.search)
    elif args.report:
        generate_report()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
