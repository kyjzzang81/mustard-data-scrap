# 데이터 스크래핑 프로젝트

다양한 데이터 소스에서 정보를 수집하는 통합 스크래핑 도구입니다.

## 🏗️ 프로젝트 구조

```
mustard-data-scrap/
├── scrapers/              # 스크래퍼 모듈들
│   ├── iris_scraper.py    # IRIS+ 메트릭 스크래퍼
│   ├── detail_analyzer.py # 상세 분석 스크래퍼
│   └── final_scraper.py   # 최종 통합 스크래퍼
├── utils/                 # 공통 유틸리티
│   ├── base_scraper.py    # 베이스 스크래퍼 클래스
│   ├── scraper_manager.py # 스크래퍼 관리자
│   ├── convert_to_supabase.py
│   └── supabase_uploader.py
├── config/                # 설정 파일들
│   ├── settings.py        # 공통 설정
│   ├── supabase_schema.sql
│   └── supabase_sample_queries.sql
├── scripts/               # 실행 스크립트들
│   └── run_full_scraping.py
├── data/                  # 수집된 데이터
├── data_temp/             # 임시 파일들
├── logs/                  # 로그 파일들
├── types/                 # 타입 정의
├── docs/                  # 문서
└── main.py               # 메인 실행 파일
```

## 🚀 사용법

### 1. 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 설정

```bash
cp env.example .env
# .env 파일에 실제 설정값 입력
```

### 3. 실행

#### 사용 가능한 스크래퍼 목록 보기
```bash
python main.py --list
```

#### 특정 스크래퍼 실행
```bash
python main.py --scraper iris
python main.py --scraper iris_detail
```

#### 모든 스크래퍼 실행
```bash
python main.py --all
```

#### 스크래퍼 정보 보기
```bash
python main.py --info iris
```

## 📊 지원하는 스크래퍼

### IRIS+ Metrics (`iris`)
- **설명**: IRIS+ 임팩트 투자 메트릭 데이터 수집
- **출력**: `data/iris_metrics.json`
- **기능**: 63페이지에 걸친 모든 메트릭 정보 수집

### IRIS+ Detail Analysis (`iris_detail`)
- **설명**: IRIS+ 메트릭 상세 정보 분석
- **출력**: `data/iris_metrics_complete.json`
- **기능**: 각 메트릭의 상세 정보 추출 및 분석

## 🔧 새로운 스크래퍼 추가하기

### 1. 스크래퍼 클래스 생성

`scrapers/` 디렉토리에 새 파일 생성:

```python
# scrapers/my_scraper.py
from utils.base_scraper import BaseScraper

class MyScraper(BaseScraper):
    def __init__(self):
        super().__init__("MyScraper")
    
    def scrape(self, **kwargs):
        # 스크래핑 로직 구현
        return {"data": "your_data"}
```

### 2. 설정에 등록

`config/settings.py`의 `SUPPORTED_SCRAPERS`에 추가:

```python
SUPPORTED_SCRAPERS = {
    # ... 기존 스크래퍼들
    "my_scraper": {
        "name": "My Scraper",
        "module": "scrapers.my_scraper",
        "class": "MyScraper",
        "description": "내 커스텀 스크래퍼"
    }
}
```

### 3. 실행

```bash
python main.py --scraper my_scraper
```

## 📁 데이터 관리

### 출력 디렉토리
- `data/`: 최종 결과 파일들
- `data_temp/`: 임시/테스트 파일들
- `logs/`: 로그 파일들

### 파일 명명 규칙
- `{scraper_name}_data.json`: 기본 데이터
- `{scraper_name}_complete.json`: 완전한 데이터
- `{scraper_name}_supabase.json`: Supabase 형식 데이터

## 🔄 Supabase 연동

### 데이터 변환 및 업로드
```bash
python utils/convert_to_supabase.py
python utils/supabase_uploader.py
```

## 📝 로깅

모든 스크래퍼는 `logs/` 디렉토리에 로그를 저장합니다:
- `{scraper_name}.log`: 개별 스크래퍼 로그
- `scraping.log`: 통합 로그

## ⚙️ 설정

`config/settings.py`에서 다음 설정을 조정할 수 있습니다:
- 요청 간 딜레이
- 최대 재시도 횟수
- 타임아웃 설정
- User-Agent 설정

## 🛠️ 개발 가이드

### 베이스 클래스 사용
모든 스크래퍼는 `BaseScraper`를 상속받아야 합니다:

```python
from utils.base_scraper import BaseScraper

class MyScraper(BaseScraper):
    def scrape(self, **kwargs):
        # make_request() 사용
        response = self.make_request(url)
        
        # 딜레이 적용
        self.delay()
        
        # 데이터 저장
        self.save_to_json(data, "output.json")
        
        return data
```

### 에러 처리
- 자동 재시도 (지수 백오프)
- 상세한 로깅
- 안전한 요청 처리

## 📋 TODO

- [ ] 더 많은 데이터 소스 추가
- [ ] 실시간 모니터링 대시보드
- [ ] 자동 스케줄링 기능
- [ ] 데이터 검증 및 품질 체크
- [ ] API 엔드포인트 제공

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.
