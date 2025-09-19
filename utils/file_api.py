"""
파일 관리 API
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional
import json
from pathlib import Path
from utils.file_storage_manager import FileStorageManager, FileBackupManager

app = FastAPI(title="SDGs File Management API", version="1.0.0")

# 전역 변수
storage_manager = None
backup_manager = None

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 초기화"""
    global storage_manager, backup_manager
    try:
        storage_manager = FileStorageManager()
        backup_manager = FileBackupManager(storage_manager)
        print("✅ 파일 저장소 관리자 초기화 완료")
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")

@app.get("/")
async def root():
    """API 상태 확인"""
    return {"message": "SDGs File Management API", "status": "running"}

@app.get("/files")
async def list_files(folder: str = ""):
    """파일 목록 조회"""
    try:
        files = storage_manager.list_files(folder)
        return {"files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{file_path:path}")
async def get_file(file_path: str):
    """파일 다운로드"""
    try:
        # 파일 URL 생성
        file_url = storage_manager.get_file_url(file_path)
        return {"file_url": file_url, "download_url": file_url}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다: {e}")

@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...), folder: str = ""):
    """파일 업로드"""
    try:
        # 임시 파일로 저장
        temp_path = f"temp/{file.filename}"
        Path("temp").mkdir(exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 원격 경로 설정
        remote_path = f"{folder}/{file.filename}".strip("/")
        
        # 업로드
        result = storage_manager.upload_file(temp_path, remote_path)
        
        # 임시 파일 삭제
        Path(temp_path).unlink()
        
        if result["success"]:
            return {"message": "파일 업로드 성공", "file_info": result}
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{file_path:path}")
async def delete_file(file_path: str):
    """파일 삭제"""
    try:
        success = storage_manager.delete_file(file_path)
        if success:
            return {"message": "파일 삭제 성공"}
        else:
            raise HTTPException(status_code=500, detail="파일 삭제 실패")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/manifest")
async def get_file_manifest(folder: str = ""):
    """파일 매니페스트 조회"""
    try:
        manifest = storage_manager.generate_file_manifest(folder)
        return manifest
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backup/create")
async def create_backup(backup_name: str, source_folder: str = ""):
    """백업 생성"""
    try:
        success = backup_manager.create_backup(source_folder, backup_name)
        if success:
            return {"message": f"백업 생성 성공: {backup_name}"}
        else:
            raise HTTPException(status_code=500, detail="백업 생성 실패")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backup/restore")
async def restore_backup(backup_name: str, target_folder: str = ""):
    """백업 복원"""
    try:
        success = backup_manager.restore_backup(backup_name, target_folder)
        if success:
            return {"message": f"백업 복원 성공: {backup_name}"}
        else:
            raise HTTPException(status_code=500, detail="백업 복원 실패")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """헬스 체크"""
    try:
        # 저장소 연결 확인
        files = storage_manager.list_files()
        return {
            "status": "healthy",
            "storage_connected": True,
            "total_files": len(files)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "storage_connected": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
