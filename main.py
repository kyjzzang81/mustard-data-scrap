"""
데이터 스크래핑 프로젝트 메인 실행 파일
"""
import argparse
import sys
from pathlib import Path
from utils.scraper_manager import ScraperManager

def main():
    parser = argparse.ArgumentParser(description='데이터 스크래핑 도구')
    parser.add_argument('--scraper', '-s', 
                       help='실행할 스크래퍼 타입 (iris, iris_detail)')
    parser.add_argument('--list', '-l', action='store_true',
                       help='사용 가능한 스크래퍼 목록 표시')
    parser.add_argument('--all', '-a', action='store_true',
                       help='모든 스크래퍼 실행')
    parser.add_argument('--info', '-i', 
                       help='특정 스크래퍼 정보 표시')
    
    args = parser.parse_args()
    
    manager = ScraperManager()
    
    if args.list:
        print("📋 사용 가능한 스크래퍼:")
        for scraper_type in manager.get_available_scrapers():
            info = manager.get_scraper_info(scraper_type)
            print(f"  • {scraper_type}: {info['description']}")
        return
    
    if args.info:
        info = manager.get_scraper_info(args.info)
        if info:
            print(f"📊 {args.info} 스크래퍼 정보:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ 스크래퍼를 찾을 수 없습니다: {args.info}")
        return
    
    if args.all:
        print("🔄 모든 스크래퍼 실행")
        scrapers = manager.get_available_scrapers()
        results = manager.run_all(scrapers)
        print(f"✅ {len(results)}개 스크래퍼 실행 완료")
        return
    
    if args.scraper:
        print(f"🚀 {args.scraper} 스크래퍼 실행")
        result = manager.run_scraper(args.scraper)
        if result:
            print("✅ 스크래핑 완료")
        else:
            print("❌ 스크래핑 실패")
            sys.exit(1)
        return
    
    # 인자가 없으면 도움말 표시
    parser.print_help()

if __name__ == "__main__":
    main()
