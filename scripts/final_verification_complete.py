"""
최종 완성된 구조 검증 스크립트
"""
from supabase import create_client, Client
from config.settings import SUPABASE_CONFIG

def create_supabase_client():
    return create_client(SUPABASE_CONFIG["url"], SUPABASE_CONFIG["service_role_key"])

def verify_complete_structure():
    """완성된 구조 최종 검증"""
    print("🔍 완성된 구조 최종 검증 중...")
    
    supabase = create_supabase_client()
    
    try:
        # 데이터베이스에서 모든 파일 정보 가져오기
        files = supabase.table('sdg_metadata_files').select('*').execute()
        
        print(f"📄 총 {len(files.data)}개 파일 확인")
        
        # 접근 가능한 파일과 불가능한 파일 분류
        accessible_files = []
        inaccessible_files = []
        
        for file_info in files.data:
            filename = file_info['filename']
            file_path = file_info['file_path']
            
            try:
                # Storage에서 파일 접근 테스트
                file_data = supabase.storage.from_('sdgs-files').download(file_path)
                
                if file_data:
                    accessible_files.append(file_info)
                else:
                    inaccessible_files.append(file_info)
                    
            except Exception as e:
                inaccessible_files.append(file_info)
        
        print(f"\n📊 접근 가능성 분석:")
        print(f"  ✅ 접근 가능: {len(accessible_files)}개")
        print(f"  ❌ 접근 불가: {len(inaccessible_files)}개")
        
        # 목표별 접근 가능한 파일 분류
        goal_accessible = {}
        for file_info in accessible_files:
            filename = file_info['filename']
            
            # filename에서 목표 번호 추출
            if 'Metadata-' in filename:
                parts = filename.replace('Metadata-', '').replace('.pdf', '').split('-')
                if len(parts) > 0:
                    try:
                        goal_number = int(parts[0])
                        goal_key = f"목표 {goal_number}"
                        
                        if goal_key not in goal_accessible:
                            goal_accessible[goal_key] = []
                        
                        goal_accessible[goal_key].append(filename)
                    except ValueError:
                        pass
        
        print(f"\n📁 목표별 접근 가능한 파일:")
        total_accessible = 0
        for goal_key in sorted(goal_accessible.keys()):
            file_count = len(goal_accessible[goal_key])
            total_accessible += file_count
            print(f"  📂 {goal_key}: {file_count}개 파일")
        
        print(f"\n📊 총 접근 가능한 파일: {total_accessible}개")
        
        # 접근 가능한 파일의 URL 예시
        if accessible_files:
            print(f"\n🔗 접근 가능한 파일 URL 예시:")
            for i, file_info in enumerate(accessible_files[:3]):
                print(f"  {i+1}. {file_info['filename']}")
                print(f"     URL: {file_info['storage_url']}")
        
        # 접근 불가능한 파일의 원인 분석
        if inaccessible_files:
            print(f"\n❌ 접근 불가능한 파일 분석:")
            print(f"  총 {len(inaccessible_files)}개 파일이 접근 불가능합니다.")
            
            # 처음 5개 접근 불가능한 파일 표시
            print(f"  처음 5개 접근 불가능한 파일:")
            for i, file_info in enumerate(inaccessible_files[:5]):
                print(f"    {i+1}. {file_info['filename']}")
                print(f"       경로: {file_info['file_path']}")
        
        return len(accessible_files), len(inaccessible_files)
        
    except Exception as e:
        print(f"❌ 검증 실패: {e}")
        return 0, 0

def main():
    print("🚀 완성된 구조 최종 검증 시작...")
    
    try:
        # 완성된 구조 검증
        accessible, inaccessible = verify_complete_structure()
        
        print(f"\n🎉 최종 검증 완료!")
        print(f"\n📋 최종 상태 요약:")
        print(f"  ✅ 접근 가능한 파일: {accessible}개")
        print(f"  ❌ 접근 불가능한 파일: {inaccessible}개")
        print(f"  📊 성공률: {(accessible/(accessible+inaccessible)*100):.1f}%" if (accessible+inaccessible) > 0 else "  📊 성공률: 0%")
        
        if accessible > 0:
            print(f"\n🎊 축하합니다! {accessible}개 파일에 정상적으로 접근할 수 있습니다!")
            print(f"   이제 SDGs 메타데이터 파일들을 목표별로 체계적으로 관리할 수 있습니다.")
        
    except Exception as e:
        print(f"❌ 최종 검증 실패: {e}")

if __name__ == "__main__":
    main()
