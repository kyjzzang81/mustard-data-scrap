"""
SDGs 데이터 분석 및 메타데이터 추출 도구
"""
import os
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import PyPDF2
import fitz  # PyMuPDF
from datetime import datetime

class SDGsAnalyzer:
    """SDGs 데이터 분석기"""
    
    def __init__(self, lib_path: str = "lib"):
        self.lib_path = Path(lib_path)
        self.metadata_path = self.lib_path / "SDG-indicator-metadata"
        self.framework_file = self.lib_path / "Global-Indicator-Framework-after-2025-review-English.xlsx"
        
    def analyze_metadata_files(self) -> Dict[str, Any]:
        """메타데이터 파일들 분석"""
        print("📊 SDGs 메타데이터 파일 분석 중...")
        
        metadata_files = list(self.metadata_path.glob("*.pdf"))
        analysis = {
            "total_files": len(metadata_files),
            "files": [],
            "goals": set(),
            "indicators": set(),
            "file_sizes": []
        }
        
        for file_path in metadata_files:
            file_info = self._analyze_metadata_file(file_path)
            analysis["files"].append(file_info)
            analysis["goals"].add(file_info.get("goal", "unknown"))
            analysis["indicators"].add(file_info.get("indicator", "unknown"))
            analysis["file_sizes"].append(file_info["size"])
        
        analysis["goals"] = sorted(list(analysis["goals"]))
        analysis["indicators"] = sorted(list(analysis["indicators"]))
        analysis["total_size_mb"] = sum(analysis["file_sizes"]) / (1024 * 1024)
        
        return analysis
    
    def _analyze_metadata_file(self, file_path: Path) -> Dict[str, Any]:
        """개별 메타데이터 파일 분석"""
        filename = file_path.stem
        size = file_path.stat().st_size
        
        # 파일명에서 정보 추출
        parts = filename.split("-")
        goal = parts[1] if len(parts) > 1 else "unknown"
        indicator = parts[2] if len(parts) > 2 else "unknown"
        
        # PDF 메타데이터 추출 시도
        metadata = self._extract_pdf_metadata(file_path)
        
        return {
            "filename": filename,
            "file_path": str(file_path),
            "size": size,
            "goal": goal,
            "indicator": indicator,
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "creation_date": metadata.get("creation_date", ""),
            "pages": metadata.get("pages", 0)
        }
    
    def _extract_pdf_metadata(self, file_path: Path) -> Dict[str, Any]:
        """PDF 메타데이터 추출"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                return {
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "creation_date": str(metadata.get("/CreationDate", "")),
                    "pages": len(pdf_reader.pages)
                }
        except Exception as e:
            print(f"⚠️ PDF 메타데이터 추출 실패: {file_path} - {e}")
            return {}
    
    def analyze_framework_file(self) -> Dict[str, Any]:
        """프레임워크 Excel 파일 분석"""
        print("📊 SDGs 프레임워크 파일 분석 중...")
        
        try:
            # Excel 파일 읽기
            df = pd.read_excel(self.framework_file)
            
            analysis = {
                "file_path": str(self.framework_file),
                "file_size": self.framework_file.stat().st_size,
                "sheets": [],
                "total_rows": 0,
                "total_columns": 0,
                "goals": set(),
                "indicators": set()
            }
            
            # 모든 시트 분석
            excel_file = pd.ExcelFile(self.framework_file)
            for sheet_name in excel_file.sheet_names:
                sheet_df = pd.read_excel(self.framework_file, sheet_name=sheet_name)
                sheet_info = {
                    "name": sheet_name,
                    "rows": len(sheet_df),
                    "columns": len(sheet_df.columns),
                    "column_names": list(sheet_df.columns)
                }
                analysis["sheets"].append(sheet_info)
                analysis["total_rows"] += len(sheet_df)
                analysis["total_columns"] = max(analysis["total_columns"], len(sheet_df.columns))
            
            analysis["total_size_mb"] = analysis["file_size"] / (1024 * 1024)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Excel 파일 분석 실패: {e}")
            return {"error": str(e)}
    
    def generate_summary_report(self) -> str:
        """SDGs 데이터 요약 리포트 생성"""
        metadata_analysis = self.analyze_metadata_files()
        framework_analysis = self.analyze_framework_file()
        
        report = f"""
# SDGs 데이터 분석 리포트
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 메타데이터 파일 분석
- 총 파일 수: {metadata_analysis['total_files']}개
- 총 용량: {metadata_analysis['total_size_mb']:.2f}MB
- 평균 파일 크기: {sum(metadata_analysis['file_sizes'])/len(metadata_analysis['file_sizes'])/1024:.2f}KB

### 목표별 분포
"""
        for goal in metadata_analysis['goals']:
            count = len([f for f in metadata_analysis['files'] if f['goal'] == goal])
            report += f"- Goal {goal}: {count}개 파일\n"
        
        report += f"""
## 📋 프레임워크 파일 분석
- 파일: {framework_analysis.get('file_path', 'N/A')}
- 파일 크기: {framework_analysis.get('total_size_mb', 0):.2f}MB
- 총 시트 수: {len(framework_analysis.get('sheets', []))}개
- 총 행 수: {framework_analysis.get('total_rows', 0)}개
- 총 열 수: {framework_analysis.get('total_columns', 0)}개

### 시트별 정보
"""
        for sheet in framework_analysis.get('sheets', []):
            report += f"- {sheet['name']}: {sheet['rows']}행 x {sheet['columns']}열\n"
        
        return report
    
    def extract_structured_data(self) -> Dict[str, Any]:
        """구조화된 데이터 추출"""
        print("🔄 구조화된 데이터 추출 중...")
        
        # 메타데이터 파일들의 기본 정보 추출
        metadata_files = list(self.metadata_path.glob("*.pdf"))
        structured_metadata = []
        
        for file_path in metadata_files:
            file_info = self._analyze_metadata_file(file_path)
            structured_metadata.append({
                "indicator_id": file_info["indicator"],
                "goal": file_info["goal"],
                "filename": file_info["filename"],
                "file_path": file_info["file_path"],
                "size_bytes": file_info["size"],
                "title": file_info["title"],
                "pages": file_info["pages"]
            })
        
        # 프레임워크 데이터 추출
        framework_data = self._extract_framework_data()
        
        return {
            "metadata_files": structured_metadata,
            "framework_data": framework_data,
            "extraction_date": datetime.now().isoformat(),
            "total_metadata_files": len(structured_metadata)
        }
    
    def _extract_framework_data(self) -> Dict[str, Any]:
        """프레임워크 데이터 추출"""
        try:
            # 첫 번째 시트 읽기 (일반적으로 메인 데이터)
            df = pd.read_excel(self.framework_file, sheet_name=0)
            
            # 기본 통계
            framework_info = {
                "total_indicators": len(df),
                "columns": list(df.columns),
                "sample_data": df.head(5).to_dict('records') if len(df) > 0 else []
            }
            
            return framework_info
            
        except Exception as e:
            print(f"❌ 프레임워크 데이터 추출 실패: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    analyzer = SDGsAnalyzer()
    
    # 분석 실행
    print("🚀 SDGs 데이터 분석 시작...")
    report = analyzer.generate_summary_report()
    print(report)
    
    # 구조화된 데이터 추출
    structured_data = analyzer.extract_structured_data()
    
    # 결과 저장
    output_file = Path("data_sources/un_sdg/raw/sdgs_analysis_20241219.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 분석 결과 저장됨: {output_file}")
