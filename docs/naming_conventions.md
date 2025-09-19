# 파일명 및 폴더명 명명 규칙

## 📁 폴더 구조

```
data_sources/
├── {data_source}/           # 데이터 소스별 폴더
│   ├── raw/                 # 원본 데이터 (스크래핑 직후)
│   ├── processed/           # 가공된 데이터
│   ├── validated/           # 검증된 데이터
│   └── archived/            # 아카이브된 데이터
```

## 📄 파일명 규칙

### 기본 형식
```
{data_source}_{data_type}_{version}_{date}.{extension}
```

### 구성 요소
- **data_source**: 데이터 소스 (iris, un_sdg, esg_ratings 등)
- **data_type**: 데이터 유형 (metrics, indicators, reports 등)
- **version**: 버전 (v1, v2, latest 등)
- **date**: 수집일 (YYYYMMDD 형식)
- **extension**: 파일 확장자 (json, csv, xlsx 등)

### 예시
```
iris_metrics_v1_20241219.json
un_sdg_indicators_latest_20241219.csv
esg_ratings_companies_v2_20241219.xlsx
```

## 🏷️ 데이터 소스 코드

| 데이터 소스 | 코드 | 설명 |
|------------|------|------|
| IRIS+ | iris | 임팩트 투자 메트릭 |
| UN SDG | un_sdg | 유엔 지속가능발전목표 |
| ESG Ratings | esg_ratings | ESG 평가 데이터 |
| Impact Metrics | impact_metrics | 임팩트 측정 지표 |
| Sustainability Reports | sustainability_reports | 지속가능성 보고서 |
| Financial Data | financial_data | 금융 데이터 |
| Market Data | market_data | 시장 데이터 |
| Regulatory Data | regulatory_data | 규제 데이터 |
| News Sentiment | news_sentiment | 뉴스 감정 분석 |
| Benchmark Data | benchmark_data | 벤치마크 데이터 |

## 📊 데이터 유형 코드

| 데이터 유형 | 코드 | 설명 |
|------------|------|------|
| Metrics | metrics | 메트릭/지표 |
| Indicators | indicators | 지표 |
| Reports | reports | 보고서 |
| Companies | companies | 기업 데이터 |
| Countries | countries | 국가 데이터 |
| Sectors | sectors | 섹터 데이터 |
| Time Series | timeseries | 시계열 데이터 |
| Metadata | metadata | 메타데이터 |

## 🔄 버전 관리

- **v1, v2, v3...**: 주요 버전
- **latest**: 최신 버전
- **draft**: 초안 버전
- **beta**: 베타 버전

## 📅 날짜 형식

- **YYYYMMDD**: 20241219
- **YYYY-MM-DD**: 2024-12-19 (가독성이 필요한 경우)
- **YYYY_MM_DD**: 2024_12_19 (파일명에 적합)

## 📁 특수 폴더

- **temp/**: 임시 파일
- **backup/**: 백업 파일
- **logs/**: 로그 파일
- **config/**: 설정 파일
- **schemas/**: 스키마 파일
