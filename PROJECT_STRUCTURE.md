# 프로젝트 구조 가이드

## 🏗️ 전체 구조

```
mustard-data-scrap/
├── data_sources/                    # 📊 데이터 소스별 폴더
│   ├── iris/                       # IRIS+ 메트릭
│   │   ├── raw/                    # 원본 데이터
│   │   ├── processed/              # 가공된 데이터
│   │   ├── validated/              # 검증된 데이터
│   │   └── archived/               # 아카이브된 데이터
│   ├── un_sdg/                     # UN SDG 지표
│   ├── esg_ratings/                # ESG 평가
│   ├── impact_metrics/             # 임팩트 메트릭
│   ├── sustainability_reports/     # 지속가능성 보고서
│   ├── financial_data/             # 금융 데이터
│   ├── market_data/                # 시장 데이터
│   ├── regulatory_data/            # 규제 데이터
│   ├── news_sentiment/             # 뉴스 감정 분석
│   └── benchmark_data/             # 벤치마크 데이터
├── scrapers/                       # 🕷️ 스크래퍼 모듈들
│   ├── iris_scraper.py
│   ├── detail_analyzer.py
│   └── final_scraper.py
├── utils/                          # 🔧 공통 유틸리티
│   ├── base_scraper.py
│   ├── scraper_manager.py
│   ├── convert_to_supabase.py
│   └── supabase_uploader.py
├── config/                         # ⚙️ 설정 파일들
│   ├── settings.py
│   ├── data_sources_config.py
│   ├── supabase_schema.sql
│   └── supabase_sample_queries.sql
├── scripts/                        # 🚀 실행 스크립트들
│   └── run_full_scraping.py
├── docs/                           # 📚 문서
│   └── naming_conventions.md
├── types/                          # 📝 타입 정의
├── logs/                           # 📋 로그 파일들
├── data_catalog.py                 # 📊 데이터 카탈로그
├── manage_data.py                  # 🛠️ 데이터 관리 도구
├── main.py                         # 🎯 메인 실행 파일
└── README.md
```

## 📄 파일명 규칙

### 기본 형식
```
{data_source}_{data_type}_{version}_{date}.{extension}
```

### 예시
- `iris_metrics_v1_20241219.json`
- `un_sdg_indicators_latest_20241219.csv`
- `esg_ratings_companies_v2_20241219.xlsx`

## 🏷️ 데이터 소스 코드

| 코드 | 이름 | 설명 |
|------|------|------|
| iris | IRIS+ Metrics | 임팩트 투자 메트릭 |
| un_sdg | UN SDG | 유엔 지속가능발전목표 |
| esg_ratings | ESG Ratings | ESG 평가 데이터 |
| impact_metrics | Impact Metrics | 임팩트 측정 지표 |
| sustainability_reports | Sustainability Reports | 지속가능성 보고서 |
| financial_data | Financial Data | 금융 데이터 |
| market_data | Market Data | 시장 데이터 |
| regulatory_data | Regulatory Data | 규제 데이터 |
| news_sentiment | News Sentiment | 뉴스 감정 분석 |
| benchmark_data | Benchmark Data | 벤치마크 데이터 |

## 🔄 데이터 처리 단계

1. **raw/**: 스크래핑 직후 원본 데이터
2. **processed/**: 가공/변환된 데이터
3. **validated/**: 검증된 데이터
4. **archived/**: 아카이브된 데이터

## 🛠️ 관리 도구

### 데이터 카탈로그
```bash
python3 manage_data.py --stats          # 통계 보기
python3 manage_data.py --list-sources   # 데이터 소스 목록
python3 manage_data.py --list-files     # 파일 목록
python3 manage_data.py --search "iris"  # 파일 검색
python3 manage_data.py --report         # 리포트 생성
```

### 스크래퍼 실행
```bash
python3 main.py --list                  # 스크래퍼 목록
python3 main.py --scraper iris          # 특정 스크래퍼 실행
python3 main.py --all                   # 모든 스크래퍼 실행
```

## 📊 데이터 품질 관리

- **검증 규칙**: 각 데이터 소스별 검증 규칙 정의
- **메타데이터**: 파일 생성일, 수정일, 크기 등 추적
- **태그 시스템**: 파일 분류 및 검색용 태그
- **버전 관리**: 데이터 버전 추적

## 🔍 확장성

새로운 데이터 소스 추가 시:
1. `data_sources/` 하위에 새 폴더 생성
2. `config/data_sources_config.py`에 설정 추가
3. `scrapers/`에 스크래퍼 구현
4. `data_catalog.py`에 데이터 소스 등록
