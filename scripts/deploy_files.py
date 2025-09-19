"""
파일 배포 스크립트
"""
import argparse
import json
from pathlib import Path
from utils.file_storage_manager import FileStorageManager, FileBackupManager

def deploy_sdgs_files():
    """SDGs 파일들을 Supabase Storage에 배포"""
    print("🚀 SDGs 파일 배포 시작...")
    
    # 저장소 관리자 초기화
    storage = FileStorageManager()
    
    # 저장소 버킷 생성
    storage.create_storage_bucket()
    
    # 파일 업로드
    upload_results = []
    
    # 1. 메타데이터 파일들 업로드
    print("📄 메타데이터 파일 업로드 중...")
    metadata_results = storage.upload_directory(
        "data_sources/un_sdg/raw/metadata",
        "metadata"
    )
    upload_results.extend(metadata_results)
    
    # 2. 프레임워크 파일 업로드
    print("📊 프레임워크 파일 업로드 중...")
    framework_results = storage.upload_directory(
        "data_sources/un_sdg/raw/framework",
        "framework"
    )
    upload_results.extend(framework_results)
    
    # 3. 처리된 데이터 파일들 업로드
    print("💾 처리된 데이터 파일 업로드 중...")
    processed_results = storage.upload_directory(
        "data_sources/un_sdg/processed",
        "processed"
    )
    upload_results.extend(processed_results)
    
    # 결과 요약
    successful_uploads = [r for r in upload_results if r.get("success", False)]
    failed_uploads = [r for r in upload_results if not r.get("success", False)]
    
    print(f"\n📊 업로드 결과:")
    print(f"  ✅ 성공: {len(successful_uploads)}개 파일")
    print(f"  ❌ 실패: {len(failed_uploads)}개 파일")
    
    if failed_uploads:
        print("\n❌ 실패한 파일들:")
        for result in failed_uploads:
            print(f"  - {result.get('local_path', 'Unknown')}: {result.get('error', 'Unknown error')}")
    
    # 파일 매니페스트 생성
    manifest = storage.generate_file_manifest()
    manifest_file = Path("file_manifest.json")
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 파일 매니페스트 생성됨: {manifest_file}")
    
    # 백업 생성
    backup_manager = FileBackupManager(storage)
    backup_name = f"initial_backup_{Path().cwd().name}"
    backup_success = backup_manager.create_backup("", backup_name)
    
    if backup_success:
        print(f"✅ 초기 백업 생성됨: {backup_name}")
    else:
        print("❌ 백업 생성 실패")
    
    return len(successful_uploads), len(failed_uploads)

def list_remote_files():
    """원격 파일 목록 조회"""
    storage = FileStorageManager()
    
    print("📁 원격 파일 목록:")
    
    # 메타데이터 파일들
    metadata_files = storage.list_files("metadata")
    print(f"\n📄 메타데이터 파일 ({len(metadata_files)}개):")
    for file_info in metadata_files[:10]:  # 처음 10개만 표시
        print(f"  - {file_info['name']}")
    if len(metadata_files) > 10:
        print(f"  ... 및 {len(metadata_files) - 10}개 더")
    
    # 프레임워크 파일들
    framework_files = storage.list_files("framework")
    print(f"\n📊 프레임워크 파일 ({len(framework_files)}개):")
    for file_info in framework_files:
        print(f"  - {file_info['name']}")
    
    # 처리된 데이터 파일들
    processed_files = storage.list_files("processed")
    print(f"\n💾 처리된 데이터 파일 ({len(processed_files)}개):")
    for file_info in processed_files:
        print(f"  - {file_info['name']}")

def download_files(local_dir: str = "downloads"):
    """원격 파일들을 로컬로 다운로드"""
    storage = FileStorageManager()
    download_dir = Path(local_dir)
    download_dir.mkdir(exist_ok=True)
    
    print(f"📥 파일 다운로드 시작: {download_dir}")
    
    # 모든 파일 목록 조회
    all_files = []
    for folder in ["metadata", "framework", "processed"]:
        files = storage.list_files(folder)
        for file_info in files:
            all_files.append((folder, file_info['name']))
    
    # 파일 다운로드
    downloaded_count = 0
    for folder, filename in all_files:
        remote_path = f"{folder}/{filename}"
        local_path = download_dir / folder / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        if storage.download_file(remote_path, str(local_path)):
            downloaded_count += 1
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename}")
    
    print(f"\n📊 다운로드 완료: {downloaded_count}/{len(all_files)}개 파일")

def main():
    parser = argparse.ArgumentParser(description="SDGs 파일 배포 도구")
    parser.add_argument("--deploy", action="store_true", help="파일 배포")
    parser.add_argument("--list", action="store_true", help="원격 파일 목록 조회")
    parser.add_argument("--download", action="store_true", help="파일 다운로드")
    parser.add_argument("--local-dir", default="downloads", help="다운로드 디렉토리")
    
    args = parser.parse_args()
    
    if args.deploy:
        deploy_sdgs_files()
    elif args.list:
        list_remote_files()
    elif args.download:
        download_files(args.local_dir)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
