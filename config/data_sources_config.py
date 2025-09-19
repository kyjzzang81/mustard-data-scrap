"""
데이터 소스별 설정
"""
from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class ScrapingConfig:
    """스크래핑 설정"""
    delay: float = 1.0
    max_retries: int = 3
    timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    headers: Dict[str, str] = None
    cookies: Dict[str, str] = None
    proxy: str = None

@dataclass
class DataSourceConfig:
    """데이터 소스별 설정"""
    name: str
    base_url: str
    scraping_config: ScrapingConfig
    output_format: str = "json"
    file_naming: str = "{data_source}_{data_type}_{version}_{date}.{ext}"
    required_fields: List[str] = None
    validation_rules: Dict[str, Any] = None

# 데이터 소스별 설정
DATA_SOURCE_CONFIGS = {
    "iris": DataSourceConfig(
        name="IRIS+ Metrics",
        base_url="https://iris.thegiin.org/",
        scraping_config=ScrapingConfig(delay=1.0),
        required_fields=["title", "data_id", "relative_path"],
        validation_rules={
            "min_metrics": 700,
            "required_keys": ["metadata", "metrics"]
        }
    ),
    "un_sdg": DataSourceConfig(
        name="UN SDG Indicators",
        base_url="https://unstats.un.org/sdgs/",
        scraping_config=ScrapingConfig(delay=2.0),
        required_fields=["indicator_id", "title", "description"],
        validation_rules={
            "min_indicators": 200,
            "required_keys": ["indicators", "metadata"]
        }
    ),
    "esg_ratings": DataSourceConfig(
        name="ESG Ratings",
        base_url="",
        scraping_config=ScrapingConfig(delay=1.5),
        required_fields=["company_id", "rating", "score"],
        validation_rules={
            "min_companies": 100,
            "required_keys": ["companies", "ratings"]
        }
    ),
    "impact_metrics": DataSourceConfig(
        name="Impact Metrics",
        base_url="",
        scraping_config=ScrapingConfig(delay=1.0),
        required_fields=["metric_id", "name", "category"],
        validation_rules={
            "min_metrics": 50,
            "required_keys": ["metrics", "categories"]
        }
    ),
    "sustainability_reports": DataSourceConfig(
        name="Sustainability Reports",
        base_url="",
        scraping_config=ScrapingConfig(delay=3.0),
        required_fields=["report_id", "company", "year"],
        validation_rules={
            "min_reports": 10,
            "required_keys": ["reports", "companies"]
        }
    ),
    "financial_data": DataSourceConfig(
        name="Financial Data",
        base_url="",
        scraping_config=ScrapingConfig(delay=0.5),
        required_fields=["symbol", "date", "price"],
        validation_rules={
            "min_records": 1000,
            "required_keys": ["data", "metadata"]
        }
    ),
    "market_data": DataSourceConfig(
        name="Market Data",
        base_url="",
        scraping_config=ScrapingConfig(delay=0.5),
        required_fields=["market", "date", "value"],
        validation_rules={
            "min_records": 500,
            "required_keys": ["markets", "data"]
        }
    ),
    "regulatory_data": DataSourceConfig(
        name="Regulatory Data",
        base_url="",
        scraping_config=ScrapingConfig(delay=2.0),
        required_fields=["regulation_id", "title", "status"],
        validation_rules={
            "min_regulations": 20,
            "required_keys": ["regulations", "metadata"]
        }
    ),
    "news_sentiment": DataSourceConfig(
        name="News Sentiment",
        base_url="",
        scraping_config=ScrapingConfig(delay=1.0),
        required_fields=["article_id", "sentiment", "score"],
        validation_rules={
            "min_articles": 100,
            "required_keys": ["articles", "sentiment"]
        }
    ),
    "benchmark_data": DataSourceConfig(
        name="Benchmark Data",
        base_url="",
        scraping_config=ScrapingConfig(delay=1.0),
        required_fields=["benchmark_id", "name", "value"],
        validation_rules={
            "min_benchmarks": 50,
            "required_keys": ["benchmarks", "data"]
        }
    )
}

def get_data_source_config(source_code: str) -> DataSourceConfig:
    """데이터 소스 설정 조회"""
    return DATA_SOURCE_CONFIGS.get(source_code)

def list_available_sources() -> List[str]:
    """사용 가능한 데이터 소스 목록"""
    return list(DATA_SOURCE_CONFIGS.keys())
