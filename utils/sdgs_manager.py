"""
SDGs 데이터 하이브리드 관리 시스템
"""
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from data_catalog import DataCatalog, DataFile, DataSource
from utils.sdgs_analyzer import SDGsAnalyzer

class SDGsManager:
    """SDGs 데이터 하이브리드 관리자"""
    
    def __init__(self):
        self.catalog = DataCatalog()
        self.analyzer = SDGsAnalyzer()
        self.sdgs_data_path = Path("data_sources/un_sdg")
        self.lib_path = Path("lib")
        
    def migrate_to_structured_storage(self):
        """lib 폴더의 데이터를 구조화된 저장소로 마이그레이션"""
        print("🔄 SDGs 데이터 마이그레이션 시작...")
        
        # 1. 원본 파일들을 raw 폴더로 복사
        self._copy_original_files()
        
        # 2. 메타데이터 분석 및 추출
        analysis_data = self.analyzer.extract_structured_data()
        
        # 3. 분석 결과를 processed 폴더에 저장
        self._save_analysis_results(analysis_data)
        
        # 4. 데이터 카탈로그에 등록
        self._register_in_catalog(analysis_data)
        
        print("✅ SDGs 데이터 마이그레이션 완료!")
    
    def _copy_original_files(self):
        """원본 파일들을 raw 폴더로 복사"""
        print("📁 원본 파일 복사 중...")
        
        # 메타데이터 PDF 파일들 복사
        metadata_dest = self.sdgs_data_path / "raw" / "metadata"
        metadata_dest.mkdir(parents=True, exist_ok=True)
        
        for pdf_file in self.lib_path.glob("SDG-indicator-metadata/*.pdf"):
            dest_file = metadata_dest / pdf_file.name
            shutil.copy2(pdf_file, dest_file)
            print(f"  📄 복사됨: {pdf_file.name}")
        
        # 프레임워크 Excel 파일 복사
        framework_dest = self.sdgs_data_path / "raw" / "framework"
        framework_dest.mkdir(parents=True, exist_ok=True)
        
        excel_file = self.lib_path / "Global-Indicator-Framework-after-2025-review-English.xlsx"
        if excel_file.exists():
            dest_file = framework_dest / excel_file.name
            shutil.copy2(excel_file, dest_file)
            print(f"  📊 복사됨: {excel_file.name}")
    
    def _save_analysis_results(self, analysis_data: Dict[str, Any]):
        """분석 결과를 processed 폴더에 저장"""
        print("💾 분석 결과 저장 중...")
        
        processed_dir = self.sdgs_data_path / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # 메타데이터 분석 결과 저장
        metadata_file = processed_dir / f"sdgs_metadata_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        # 개별 지표별 메타데이터 저장
        indicators_dir = processed_dir / "indicators"
        indicators_dir.mkdir(exist_ok=True)
        
        for metadata in analysis_data.get("metadata_files", []):
            indicator_file = indicators_dir / f"indicator_{metadata['indicator_id']}.json"
            with open(indicator_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 분석 결과 저장됨: {metadata_file}")
    
    def _register_in_catalog(self, analysis_data: Dict[str, Any]):
        """데이터 카탈로그에 등록"""
        print("📋 데이터 카탈로그에 등록 중...")
        
        # SDGs 데이터 소스 등록 (아직 없다면)
        if not self.catalog.get_data_source("un_sdg"):
            sdgs_source = DataSource(
                code="un_sdg",
                name="UN Sustainable Development Goals",
                description="유엔 지속가능발전목표 지표 및 메타데이터",
                website="https://unstats.un.org/sdgs/",
                category="sustainability",
                update_frequency="annual"
            )
            self.catalog.register_data_source(sdgs_source)
        
        # 메타데이터 파일들 등록
        for metadata in analysis_data.get("metadata_files", []):
            data_file = DataFile(
                filename=metadata["filename"],
                data_source="un_sdg",
                data_type="metadata",
                version="v1",
                file_path=metadata["file_path"],
                file_size=metadata["size_bytes"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                description=f"SDG 지표 {metadata['indicator_id']} 메타데이터",
                tags=["sdg", "metadata", f"goal_{metadata['goal']}", f"indicator_{metadata['indicator_id']}"]
            )
            self.catalog.register_data_file(data_file)
        
        # 프레임워크 파일 등록
        if analysis_data.get("framework_data"):
            framework_file = DataFile(
                filename="Global-Indicator-Framework-after-2025-review-English.xlsx",
                data_source="un_sdg",
                data_type="framework",
                version="v1",
                file_path="data_sources/un_sdg/raw/framework/Global-Indicator-Framework-after-2025-review-English.xlsx",
                file_size=Path("data_sources/un_sdg/raw/framework/Global-Indicator-Framework-after-2025-review-English.xlsx").stat().st_size,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                description="SDGs 글로벌 지표 프레임워크 (2025년 리뷰 후)",
                tags=["sdg", "framework", "indicators", "global"]
            )
            self.catalog.register_data_file(framework_file)
    
    def generate_supabase_import_data(self) -> Dict[str, Any]:
        """Supabase 임포트용 데이터 생성"""
        print("🔄 Supabase 임포트용 데이터 생성 중...")
        
        # 분석 데이터 로드
        analysis_file = self.sdgs_data_path / "processed" / f"sdgs_metadata_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        if not analysis_file.exists():
            print("❌ 분석 데이터 파일이 없습니다. 먼저 마이그레이션을 실행하세요.")
            return {}
        
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # Supabase 형식으로 변환
        supabase_data = {
            "sdg_indicators": [],
            "sdg_metadata_files": [],
            "sdg_framework_data": []
        }
        
        # 지표 데이터 변환
        for metadata in analysis_data.get("metadata_files", []):
            indicator = {
                "indicator_id": metadata["indicator_id"],
                "goal_id": int(metadata["goal"]) if metadata["goal"].isdigit() else None,
                "title": metadata["title"],
                "description": f"SDG 지표 {metadata['indicator_id']} 메타데이터"
            }
            supabase_data["sdg_indicators"].append(indicator)
            
            # 메타데이터 파일 정보
            metadata_file = {
                "indicator_id": metadata["indicator_id"],
                "filename": metadata["filename"],
                "file_path": metadata["file_path"],
                "file_size_bytes": metadata["size_bytes"],
                "file_type": "pdf",
                "title": metadata["title"],
                "pages": metadata["pages"],
                "is_processed": True,
                "processing_status": "completed"
            }
            supabase_data["sdg_metadata_files"].append(metadata_file)
        
        # 프레임워크 데이터 변환
        if analysis_data.get("framework_data"):
            framework_data = {
                "framework_version": "2025-review",
                "data_source": "UN Statistics Division",
                "raw_data": analysis_data["framework_data"],
                "processed_data": analysis_data["framework_data"]
            }
            supabase_data["sdg_framework_data"].append(framework_data)
        
        # Supabase 형식 파일 저장
        supabase_file = self.sdgs_data_path / "processed" / f"sdgs_supabase_format_{datetime.now().strftime('%Y%m%d')}.json"
        with open(supabase_file, 'w', encoding='utf-8') as f:
            json.dump(supabase_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Supabase 형식 데이터 생성됨: {supabase_file}")
        return supabase_data
    
    def get_file_access_info(self) -> Dict[str, Any]:
        """파일 접근 정보 제공"""
        return {
            "file_system": {
                "raw_data_path": str(self.sdgs_data_path / "raw"),
                "processed_data_path": str(self.sdgs_data_path / "processed"),
                "total_files": len(list(self.sdgs_data_path.rglob("*"))),
                "total_size_mb": sum(f.stat().st_size for f in self.sdgs_data_path.rglob("*") if f.is_file()) / (1024 * 1024)
            },
            "database": {
                "schema_file": "config/sdgs_schema.sql",
                "tables": ["sdg_goals", "sdg_indicators", "sdg_metadata_files", "sdg_framework_data", "sdg_country_data"],
                "recommended_use": "구조화된 쿼리, 관계형 분석, 실시간 API 접근"
            },
            "recommendations": {
                "file_system": "원본 파일 보관, 오프라인 접근, 간단한 파일 관리",
                "database": "복잡한 쿼리, 다른 데이터와의 통합, 실시간 분석",
                "hybrid": "원본은 파일로, 메타데이터와 구조화된 데이터는 DB로"
            }
        }

if __name__ == "__main__":
    manager = SDGsManager()
    
    print("🚀 SDGs 데이터 관리 시스템 시작...")
    
    # 1. 마이그레이션 실행
    manager.migrate_to_structured_storage()
    
    # 2. Supabase 임포트 데이터 생성
    supabase_data = manager.generate_supabase_import_data()
    
    # 3. 접근 정보 출력
    access_info = manager.get_file_access_info()
    print("\n📊 파일 접근 정보:")
    print(json.dumps(access_info, indent=2, ensure_ascii=False))
