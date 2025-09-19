# IRIS+ 데이터 스크래핑 프로젝트 대화 로그

## 프로젝트 개요

- **목표**: IRIS+ 웹사이트에서 750개 메트릭의 상세 정보 수집
- **소스**: https://iris.thegiin.org/metrics/ (63페이지)
- **완료일**: 2025-09-18

## 주요 결정사항

### 1. 초기 요구사항

- 63페이지에 걸친 IRIS+ 메트릭 목록 수집
- `.catalog-list` 내 a 태그에서 텍스트, 경로, data-id 추출
- 추후 상세 페이지 접근을 위한 JSON 구조 설계

### 2. JSON 구조 설계 결정

- **초기**: full_url과 detail_url 모두 포함
- **수정**: detail_url만 유지 (중복 제거)
- **최종 구조**:

```json
{
  "title": "Account Value",
  "data_id": "PI1653",
  "relative_path": "metric/5.3b/pi1653/",
  "detail_url": "https://iris.thegiin.org/metric/5.3b/pi1653/"
}
```

### 3. 상세 페이지 구조 분석

- **발견**: div.metric-box 구조로 각 섹션이 구분됨
- **구조**: div.metric-box > header (제목), section (내용)
- **중요 발견**: section#metadata에 메타데이터 있음

### 4. 스크래핑 방식 개선 과정

1. **1차 시도**: 제목-내용 매칭 실패
2. **2차 시도**: HTML 구조 정확 분석
3. **3차 시도**: metric-box 구조 기반 성공
4. **최종**: 메타데이터 + 완전한 내용 수집

### 5. 수집된 데이터 구조

```json
{
  "metadata": {
    "Reporting Format": "Selection",
    "Metric Type": "Metric",
    "Metric Level": "Product/Service",
    "IRIS Metric Citation": "IRIS, 2022. Account Value (PI1653). v5.3."
  },
  "definition": "메트릭 정의...",
  "usage_guidance": {
    "title": "Usage Guidance",
    "content": {
      "paragraphs": [...],
      "lists": [...],
      "headings": [...],
      "other_elements": [...]
    }
  },
  "impact_categories": {...},
  "sdg_goals": {...},
  "metric_history": {...}
}
```

## 기술적 결정사항

### 1. 라이브러리 선택

- **requests**: HTTP 요청
- **BeautifulSoup**: HTML 파싱
- **lxml 제외**: 설치 문제로 html.parser 사용

### 2. 파일 구조 정리

```
data-scrap/
├── data/                          # 최종 결과 파일들
│   ├── iris_metrics.json         # 기본 메트릭 목록 (750개)
│   └── iris_metrics_complete.json # 상세 정보 포함 완전 데이터
├── data_temp/                     # 임시/테스트 파일들
│   ├── *.log                     # 로그 파일들
│   └── *_test_*.json            # 테스트 결과들
├── final_scraper.py              # 최종 스크래퍼
├── run_full_scraping.py          # 전체 수집 실행
└── README.md
```

### 3. 성능 최적화

- **배치 처리**: 50개씩 나누어 처리
- **중간 저장**: 10개마다 임시 저장
- **서버 부하 방지**: 요청 간 1.5초 딜레이
- **에러 처리**: 실패 시에도 기본 구조 유지

## 수집 결과

### 최종 성과

- ✅ **총 메트릭**: 750개 (100% 성공)
- ✅ **처리 시간**: 약 30분
- ✅ **데이터 완성도**: 모든 섹션 수집 완료

### 섹션별 수집 통계

- **metadata**: 750개 (100%)
- **usage_guidance**: 750개 (100%)
- **impact_categories**: 744개 (99.2%)
- **definition**: 736개 (98.1%)
- **sdg_goals**: 624개 (83.2%)
- **related_metrics**: 66개 (8.8%)

### Impact Categories 분포

1. Cross Category: 381개
2. Real Estate: 104개
3. Financial Services: 90개
4. Agriculture: 81개
5. Water: 80개
6. Health: 77개
7. Diversity and Inclusion: 72개
8. Climate: 71개
9. Education: 67개
10. Land: 67개

## Supabase 테이블 구조 논의

### 현재 검토 중인 옵션들

#### 옵션 1: 단일 테이블 + JSON

```sql
CREATE TABLE iris_metrics (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    data_id TEXT UNIQUE NOT NULL,
    -- 메타데이터 정규화
    reporting_format TEXT,
    metric_type TEXT,
    metric_level TEXT,
    -- JSON 컬럼들
    definition TEXT,
    usage_guidance JSONB,
    impact_categories JSONB,
    sdg_goals JSONB,
    metric_history JSONB
);
```

#### 옵션 2: 정규화된 다중 테이블

- 메인 테이블 + 각 섹션별 별도 테이블

#### 다국어 지원 고려사항

- **한글 번역본 필요**
- **업데이트 용이성** 중요
- **확장성** (추후 다른 언어 추가 가능성)

### 미결정 사항

1. Impact Category를 별도 테이블로 둘지 JSON 내 포함할지
2. 다국어 지원 방식 (컬럼 분리 vs JSON 구조 vs 별도 번역 테이블)

## 다음 단계

1. Supabase 테이블 구조 최종 결정
2. 데이터 업로드 스크립트 작성
3. 한글 번역 작업 계획

---

_마지막 업데이트: 2025-09-19 02:43_
