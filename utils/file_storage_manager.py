"""
파일 저장소 관리 시스템
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from supabase import create_client, Client
from config.settings import SUPABASE_CONFIG

class FileStorageManager:
    """파일 저장소 관리자"""
    
    def __init__(self):
        self.supabase: Client = self._init_supabase()
        self.bucket_name = "sdgs-files"
        
    def _init_supabase(self) -> Client:
        """Supabase 클라이언트 초기화"""
        url = SUPABASE_CONFIG["url"]
        key = SUPABASE_CONFIG["service_role_key"]
        
        if not url or not key:
            raise ValueError("Supabase 설정이 필요합니다. .env 파일을 확인하세요.")
        
        return create_client(url, key)
    
    def create_storage_bucket(self):
        """저장소 버킷 생성"""
        try:
            # 버킷 생성
            self.supabase.storage.create_bucket(
                self.bucket_name,
                options={
                    "public": False,  # 비공개 버킷
                    "file_size_limit": 100 * 1024 * 1024,  # 100MB 제한
                    "allowed_mime_types": [
                        "application/pdf",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "application/vnd.ms-excel"
                    ]
                }
            )
            print(f"✅ 저장소 버킷 생성됨: {self.bucket_name}")
        except Exception as e:
            if "already exists" in str(e):
                print(f"ℹ️ 버킷이 이미 존재합니다: {self.bucket_name}")
            else:
                print(f"❌ 버킷 생성 실패: {e}")
    
    def upload_file(self, local_path: str, remote_path: str) -> Dict[str, Any]:
        """파일 업로드"""
        try:
            with open(local_path, 'rb') as f:
                file_data = f.read()
            
            result = self.supabase.storage.from_(self.bucket_name).upload(
                remote_path,
                file_data,
                file_options={
                    "content-type": self._get_content_type(local_path)
                }
            )
            
            # 공개 URL 생성
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(remote_path)
            
            return {
                "success": True,
                "remote_path": remote_path,
                "public_url": public_url,
                "file_size": len(file_data)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_directory(self, local_dir: str, remote_prefix: str = "") -> List[Dict[str, Any]]:
        """디렉토리 전체 업로드"""
        results = []
        local_path = Path(local_dir)
        
        for file_path in local_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_path)
                remote_path = f"{remote_prefix}/{relative_path}".replace("\\", "/")
                
                print(f"📤 업로드 중: {file_path.name}")
                result = self.upload_file(str(file_path), remote_path)
                result["local_path"] = str(file_path)
                results.append(result)
        
        return results
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """파일 다운로드"""
        try:
            file_data = self.supabase.storage.from_(self.bucket_name).download(remote_path)
            
            with open(local_path, 'wb') as f:
                f.write(file_data)
            
            return True
        except Exception as e:
            print(f"❌ 다운로드 실패: {e}")
            return False
    
    def list_files(self, folder: str = "") -> List[Dict[str, Any]]:
        """파일 목록 조회"""
        try:
            files = self.supabase.storage.from_(self.bucket_name).list(folder)
            return files
        except Exception as e:
            print(f"❌ 파일 목록 조회 실패: {e}")
            return []
    
    def get_file_url(self, remote_path: str) -> str:
        """파일 공개 URL 생성"""
        return self.supabase.storage.from_(self.bucket_name).get_public_url(remote_path)
    
    def delete_file(self, remote_path: str) -> bool:
        """파일 삭제"""
        try:
            self.supabase.storage.from_(self.bucket_name).remove([remote_path])
            return True
        except Exception as e:
            print(f"❌ 파일 삭제 실패: {e}")
            return False
    
    def _get_content_type(self, file_path: str) -> str:
        """파일 확장자에 따른 Content-Type 반환"""
        ext = Path(file_path).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.json': 'application/json'
        }
        return content_types.get(ext, 'application/octet-stream')
    
    def generate_file_manifest(self, folder: str = "") -> Dict[str, Any]:
        """파일 매니페스트 생성"""
        files = self.list_files(folder)
        
        manifest = {
            "bucket": self.bucket_name,
            "folder": folder,
            "total_files": len(files),
            "files": []
        }
        
        for file_info in files:
            file_data = {
                "name": file_info["name"],
                "size": file_info.get("metadata", {}).get("size", 0),
                "last_modified": file_info.get("updated_at"),
                "content_type": file_info.get("metadata", {}).get("mimetype"),
                "public_url": self.get_file_url(f"{folder}/{file_info['name']}".strip("/"))
            }
            manifest["files"].append(file_data)
        
        return manifest

class FileBackupManager:
    """파일 백업 관리자"""
    
    def __init__(self, storage_manager: FileStorageManager):
        self.storage = storage_manager
        self.backup_bucket = "sdgs-backup"
    
    def create_backup(self, source_folder: str, backup_name: str) -> bool:
        """백업 생성"""
        try:
            # 백업 버킷 생성
            self.storage.supabase.storage.create_bucket(
                self.backup_bucket,
                options={"public": False}
            )
            
            # 파일들을 백업 폴더로 복사
            files = self.storage.list_files(source_folder)
            backup_path = f"backups/{backup_name}"
            
            for file_info in files:
                source_path = f"{source_folder}/{file_info['name']}"
                backup_file_path = f"{backup_path}/{file_info['name']}"
                
                # 파일 다운로드 후 백업 버킷에 업로드
                file_data = self.storage.supabase.storage.from_(self.storage.bucket_name).download(source_path)
                self.storage.supabase.storage.from_(self.backup_bucket).upload(
                    backup_file_path,
                    file_data
                )
            
            print(f"✅ 백업 생성 완료: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ 백업 생성 실패: {e}")
            return False
    
    def restore_backup(self, backup_name: str, target_folder: str) -> bool:
        """백업 복원"""
        try:
            backup_path = f"backups/{backup_name}"
            backup_files = self.storage.supabase.storage.from_(self.backup_bucket).list(backup_path)
            
            for file_info in backup_files:
                source_path = f"{backup_path}/{file_info['name']}"
                target_path = f"{target_folder}/{file_info['name']}"
                
                # 백업에서 파일 다운로드 후 메인 버킷에 업로드
                file_data = self.storage.supabase.storage.from_(self.backup_bucket).download(source_path)
                self.storage.supabase.storage.from_(self.storage.bucket_name).upload(
                    target_path,
                    file_data
                )
            
            print(f"✅ 백업 복원 완료: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ 백업 복원 실패: {e}")
            return False

if __name__ == "__main__":
    # 파일 저장소 관리자 초기화
    storage = FileStorageManager()
    
    # 저장소 버킷 생성
    storage.create_storage_bucket()
    
    # SDGs 파일들 업로드
    print("🚀 SDGs 파일 업로드 시작...")
    
    # 메타데이터 파일들 업로드
    metadata_results = storage.upload_directory(
        "data_sources/un_sdg/raw/metadata",
        "metadata"
    )
    
    # 프레임워크 파일 업로드
    framework_results = storage.upload_directory(
        "data_sources/un_sdg/raw/framework",
        "framework"
    )
    
    # 결과 요약
    total_uploaded = len([r for r in metadata_results + framework_results if r["success"]])
    total_failed = len([r for r in metadata_results + framework_results if not r["success"]])
    
    print(f"✅ 업로드 완료: {total_uploaded}개 파일")
    if total_failed > 0:
        print(f"❌ 업로드 실패: {total_failed}개 파일")
    
    # 파일 매니페스트 생성
    manifest = storage.generate_file_manifest()
    with open("file_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print("📄 파일 매니페스트 생성됨: file_manifest.json")
