#!/usr/bin/env python3
"""
전체 750개 메트릭 최종 수집 실행 스크립트
"""

from final_scraper import FinalScraper
import json

def main():
    """전체 메트릭 수집 실행"""
    scraper = FinalScraper()
    
    # 기존 데이터 로드
    print("🚀 전체 750개 IRIS+ 메트릭 상세 정보 수집 시작")
    print("⏱️  예상 소요 시간: 약 20-25분")
    print("💾 배치별 중간 저장으로 안전하게 처리됩니다.")
    print()
    
    base_data = scraper.load_base_metrics()
    
    if not base_data:
        print("❌ 기존 메트릭 데이터를 로드할 수 없습니다.")
        return
    
    total_metrics = len(base_data['metrics'])
    print(f"📊 처리할 메트릭: {total_metrics}개")
    
    # 전체 처리
    final_data = scraper.process_all_metrics(base_data, batch_size=50)
    
    # 최종 저장
    final_filename = "data/iris_metrics_complete.json"
    with open(final_filename, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    # 결과 통계
    successful = sum(1 for m in final_data['metrics'] if m.get('details', {}).get('success', False))
    
    print(f"\n🎉 전체 수집 완료!")
    print(f"📁 최종 파일: {final_filename}")
    print(f"📊 성공률: {successful}/{total_metrics}개 ({successful/total_metrics*100:.1f}%)")
    
    # 섹션별 통계
    section_stats = {}
    for metric in final_data['metrics']:
        if metric.get('details', {}).get('success', False):
            details = metric['details']
            for key in details:
                if key not in ['success', 'scraped_at', 'error']:
                    if key not in section_stats:
                        section_stats[key] = 0
                    section_stats[key] += 1
    
    print(f"\n📋 섹션별 수집 통계:")
    for section, count in sorted(section_stats.items()):
        print(f"  {section}: {count}개")

if __name__ == "__main__":
    main()
