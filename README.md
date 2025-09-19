# IRIS+ 메트릭 데이터 스크래핑 도구

IRIS+ (Global Impact Investing Network)에서 제공하는 임팩트 투자 메트릭 데이터를 수집하는 Python 스크래핑 도구입니다.

## 기능

- 📊 **메트릭 목록 수집**: 63페이지에 걸친 모든 IRIS+ 메트릭 정보 수집
- 🔍 **데이터 추출**: 메트릭 제목, data-id, 경로 정보 추출
- 💾 **JSON 저장**: 구조화된 JSON 형태로 데이터 저장
- 🔗 **상세 페이지 준비**: 추후 상세 정보 수집을 위한 URL 구조 포함

## 설치

1. 필요한 라이브러리 설치:

```bash
pip install -r requirements.txt
```

## 사용법

### 기본 실행

```bash
python iris_scraper.py
```

### 프로그래밍 방식 사용

```python
from iris_scraper import IRISScraper

# 스크래퍼 인스턴스 생성
scraper = IRISScraper()

# 모든 페이지 스크래핑 (63페이지)
metrics = scraper.scrape_all_pages(total_pages=63)

# JSON 파일로 저장
scraper.save_to_json(metrics, "my_metrics.json")
```

## 출력 데이터 구조

생성되는 JSON 파일의 구조:

```json
{
  "metadata": {
    "source": "https://iris.thegiin.org/metrics/",
    "total_metrics": 750,
    "scraped_at": "2024-12-19 15:30:45",
    "version": "IRIS v5.3b"
  },
  "metrics": [
    {
      "title": "Account Value",
      "data_id": "PI1653",
      "relative_path": "metric/5.3b/pi1653/",
      "detail_url": "https://iris.thegiin.org/metric/5.3b/pi1653/"
    }
  ]
}
```

### 데이터 필드 설명

- **title**: 메트릭의 제목 (예: "Account Value")
- **data_id**: IRIS+ 메트릭 고유 식별자 (예: "PI1653")
- **relative_path**: 상대 경로
- **detail_url**: 상세 정보 페이지 URL (추후 스크래핑용)

## 추후 확장 가능성

현재 수집된 데이터를 바탕으로 각 메트릭의 상세 정보를 수집할 수 있습니다:

```python
# 예시: 상세 정보 수집
for metric in metrics_data['metrics']:
    detail_url = metric['detail_url']
    # detail_url로 접근하여 상세 정보 수집
    # 예: https://iris.thegiin.org/metric/5.3b/od3520/
```

## 파일 구조

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

## Supabase 연동

### 설정

1. 환경변수 파일 생성:

```bash
cp env.example .env
```

2. `.env` 파일에 실제 Supabase 정보 입력:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

### 데이터베이스 설정

1. Supabase SQL Editor에서 `supabase_schema.sql` 실행
2. 테이블 및 인덱스 생성 확인

### 데이터 변환 및 업로드

```bash
# 1. 데이터를 Supabase 형식으로 변환
python convert_to_supabase.py

# 2. Supabase에 업로드
python supabase_uploader.py
```

### 생성되는 파일들

- `data/iris_metrics_supabase_format.json` - Supabase 형식 데이터
- `supabase_sample_queries.sql` - 활용 쿼리 예시

## 로그

실행 중 로그는 다음 위치에 저장됩니다:

- 파일: `data_temp/*.log`
- 콘솔: 실시간 진행상황 표시

## 주의사항

## 다른 프로젝트와 공유

### 📦 **타입 정의**

- `types/iris-metrics.types.ts` - TypeScript 타입 정의
- `docs/api-documentation.md` - 상세 API 문서
- `examples/supabase-client-setup.js` - 클라이언트 설정 예시

### 🔗 **공유 방법**

1. **파일 복사**: 필요한 타입 파일을 다른 프로젝트로 복사
2. **Git Submodule**: 이 저장소를 서브모듈로 추가
3. **NPM 패키지**: 타입 정의를 NPM 패키지로 배포
4. **API 문서**: 문서를 팀과 공유하여 스키마 이해

### 🌐 **Supabase 연결 정보**

```bash
SUPABASE_URL=https://bianqiestqutnbbnnwmk.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

## 주의사항

- 서버 부하 방지를 위해 각 페이지 요청 간 1초 딜레이가 적용됩니다
- 네트워크 오류 시 해당 페이지는 스킵되고 로그에 기록됩니다
- User-Agent 헤더를 설정하여 봇 차단을 방지합니다

## 라이선스

이 도구는 교육 및 연구 목적으로 제작되었습니다. IRIS+ 데이터의 사용은 해당 웹사이트의 이용약관을 따라야 합니다.
