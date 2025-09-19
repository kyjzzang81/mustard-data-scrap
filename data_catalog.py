"""
데이터 카탈로그 관리 시스템
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class DataSource:
    """데이터 소스 정보"""
    code: str
    name: str
    description: str
    website: str
    category: str
    update_frequency: str
    last_updated: Optional[str] = None
    status: str = "active"  # active, inactive, deprecated

@dataclass
class DataFile:
    """데이터 파일 정보"""
    filename: str
    data_source: str
    data_type: str
    version: str
    file_path: str
    file_size: int
    created_at: str
    updated_at: str
    description: str
    tags: List[str]
    quality_score: Optional[float] = None

class DataCatalog:
    """데이터 카탈로그 관리자"""
    
    def __init__(self, catalog_file: str = "data_catalog.json"):
        self.catalog_file = Path(catalog_file)
        self.data_sources: Dict[str, DataSource] = {}
        self.data_files: List[DataFile] = []
        self.load_catalog()
    
    def load_catalog(self):
        """카탈로그 로드"""
        if self.catalog_file.exists():
            with open(self.catalog_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.data_sources = {
                    k: DataSource(**v) for k, v in data.get('data_sources', {}).items()
                }
                self.data_files = [DataFile(**f) for f in data.get('data_files', [])]
    
    def save_catalog(self):
        """카탈로그 저장"""
        data = {
            'data_sources': {k: asdict(v) for k, v in self.data_sources.items()},
            'data_files': [asdict(f) for f in self.data_files],
            'last_updated': datetime.now().isoformat()
        }
        with open(self.catalog_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def register_data_source(self, data_source: DataSource):
        """데이터 소스 등록"""
        self.data_sources[data_source.code] = data_source
        self.save_catalog()
        print(f"✅ 데이터 소스 등록됨: {data_source.name}")
    
    def register_data_file(self, data_file: DataFile):
        """데이터 파일 등록"""
        self.data_files.append(data_file)
        self.save_catalog()
        print(f"✅ 데이터 파일 등록됨: {data_file.filename}")
    
    def get_data_source(self, code: str) -> Optional[DataSource]:
        """데이터 소스 조회"""
        return self.data_sources.get(code)
    
    def list_data_sources(self) -> List[DataSource]:
        """데이터 소스 목록"""
        return list(self.data_sources.values())
    
    def list_data_files(self, data_source: Optional[str] = None) -> List[DataFile]:
        """데이터 파일 목록"""
        if data_source:
            return [f for f in self.data_files if f.data_source == data_source]
        return self.data_files
    
    def search_files(self, query: str) -> List[DataFile]:
        """파일 검색"""
        query = query.lower()
        results = []
        for file in self.data_files:
            if (query in file.filename.lower() or 
                query in file.description.lower() or 
                query in file.tags):
                results.append(file)
        return results
    
    def get_file_stats(self) -> Dict[str, Any]:
        """파일 통계"""
        total_files = len(self.data_files)
        total_size = sum(f.file_size for f in self.data_files)
        by_source = {}
        by_type = {}
        
        for file in self.data_files:
            by_source[file.data_source] = by_source.get(file.data_source, 0) + 1
            by_type[file.data_type] = by_type.get(file.data_type, 0) + 1
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_source': by_source,
            'by_type': by_type
        }
    
    def generate_report(self) -> str:
        """카탈로그 리포트 생성"""
        stats = self.get_file_stats()
        report = f"""
# 데이터 카탈로그 리포트
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 전체 통계
- 총 파일 수: {stats['total_files']}개
- 총 용량: {stats['total_size_mb']}MB

## 📁 데이터 소스별 파일 수
"""
        for source, count in stats['by_source'].items():
            report += f"- {source}: {count}개\n"
        
        report += "\n## 📄 데이터 유형별 파일 수\n"
        for data_type, count in stats['by_type'].items():
            report += f"- {data_type}: {count}개\n"
        
        return report

# 기본 데이터 소스 등록
def initialize_default_sources():
    """기본 데이터 소스들 등록"""
    catalog = DataCatalog()
    
    default_sources = [
        DataSource(
            code="iris",
            name="IRIS+ Metrics",
            description="Global Impact Investing Network의 임팩트 투자 메트릭",
            website="https://iris.thegiin.org/",
            category="impact_investing",
            update_frequency="quarterly"
        ),
        DataSource(
            code="un_sdg",
            name="UN Sustainable Development Goals",
            description="유엔 지속가능발전목표 지표",
            website="https://unstats.un.org/sdgs/",
            category="sustainability",
            update_frequency="annual"
        ),
        DataSource(
            code="esg_ratings",
            name="ESG Ratings",
            description="ESG 평가 및 등급 데이터",
            website="",
            category="esg",
            update_frequency="monthly"
        )
    ]
    
    for source in default_sources:
        catalog.register_data_source(source)
    
    return catalog

if __name__ == "__main__":
    catalog = initialize_default_sources()
    print("데이터 카탈로그 초기화 완료!")
