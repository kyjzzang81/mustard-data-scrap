# IRIS+ 메트릭 API 문서

## 📋 **테이블 구조: `iris_metrics`**

### 기본 정보

- **테이블명**: `iris_metrics`
- **총 레코드 수**: 750개
- **언어 지원**: 영문 (한국어 준비됨)
- **버전**: v5.3b

## 🗄️ **컬럼 구조**

### 기본 필드

| 컬럼명          | 타입   | 필수 | 설명                        |
| --------------- | ------ | ---- | --------------------------- |
| `id`            | SERIAL | ✅   | 기본키                      |
| `title_en`      | TEXT   | ✅   | 영문 제목                   |
| `title_ko`      | TEXT   | ❌   | 한국어 제목 (준비됨)        |
| `data_id`       | TEXT   | ✅   | 고유 메트릭 ID (예: PI1653) |
| `relative_path` | TEXT   | ❌   | 상대 경로                   |
| `detail_url`    | TEXT   | ❌   | 상세 페이지 URL             |

### 메타데이터 필드

| 컬럼명             | 타입 | 설명           |
| ------------------ | ---- | -------------- |
| `reporting_format` | TEXT | 보고 형식      |
| `metric_type`      | TEXT | 메트릭 타입    |
| `metric_level`     | TEXT | 메트릭 레벨    |
| `iris_citation`    | TEXT | IRIS 인용 정보 |

### JSON 필드 (다국어 지원)

| 컬럼명              | 타입  | 구조                        | 설명            |
| ------------------- | ----- | --------------------------- | --------------- |
| `definition`        | JSONB | `{"en": {...}, "ko": null}` | 정의            |
| `usage_guidance`    | JSONB | `{"en": {...}, "ko": null}` | 사용 가이드라인 |
| `impact_categories` | JSONB | `{"en": {...}, "ko": null}` | 임팩트 카테고리 |
| `sdg_goals`         | JSONB | `{"en": {...}, "ko": null}` | SDG 목표        |
| `metric_history`    | JSONB | `{...}`                     | 버전 히스토리   |
| `related_metrics`   | JSONB | `{...}`                     | 관련 메트릭     |

### 시스템 필드

| 컬럼명          | 타입      | 설명           |
| --------------- | --------- | -------------- |
| `scraped_at`    | TIMESTAMP | 수집 시점      |
| `translated_at` | TIMESTAMP | 번역 완료 시점 |
| `success`       | BOOLEAN   | 수집 성공 여부 |
| `version`       | TEXT      | 버전 정보      |
| `created_at`    | TIMESTAMP | 생성 시점      |
| `updated_at`    | TIMESTAMP | 수정 시점      |

## 🔍 **주요 쿼리 예시**

### 1. 기본 메트릭 조회

```sql
SELECT id, title_en, title_ko, data_id, metric_type
FROM iris_metrics
WHERE metric_type = 'Metric'
LIMIT 10;
```

### 2. Impact Category별 메트릭 조회

```sql
SELECT title_en, data_id, metric_type
FROM iris_metrics
WHERE impact_categories @> '{"en": {"content": {"headings": [{"text": "Water"}]}}}';
```

### 3. SDG 목표별 메트릭 조회

```sql
SELECT title_en, data_id
FROM iris_metrics
WHERE sdg_goals @> '{"en": {"content": {"headings": [{"text": "Clean Water and Sanitation"}]}}}';
```

### 4. 전체 텍스트 검색

```sql
SELECT title_en, data_id
FROM iris_metrics
WHERE definition->>'en' ILIKE '%water%'
   OR usage_guidance->'en'->'content'->>'raw_text' ILIKE '%water%';
```

## 📊 **통계 정보**

### Impact Categories 요약

```sql
SELECT
    jsonb_array_elements_text(
        jsonb_path_query_array(impact_categories, '$.en.content.headings[*].text')
    ) as category_name,
    COUNT(*) as metric_count
FROM iris_metrics
WHERE impact_categories IS NOT NULL
GROUP BY category_name
ORDER BY metric_count DESC;
```

### 메트릭 타입별 분포

```sql
SELECT metric_type, COUNT(*) as count
FROM iris_metrics
GROUP BY metric_type
ORDER BY count DESC;
```

## 🌐 **다국어 지원**

### 현재 상태

- **영문**: 완료 (750개 메트릭)
- **한국어**: 준비됨 (필드 예약됨)

### 번역 업데이트 예시

```sql
UPDATE iris_metrics
SET
    title_ko = '계정 가치',
    definition = jsonb_set(
        definition,
        '{ko}',
        '{"title": "계정 가치", "content": {...}}'
    ),
    translated_at = NOW()
WHERE data_id = 'PI1653';
```

## 🔗 **연결 정보**

### Supabase URL

```
https://bianqiestqutnbbnnwmk.supabase.co
```

### 환경변수 설정

```bash
SUPABASE_URL=https://bianqiestqutnbbnnwmk.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

## 📦 **NPM 패키지로 공유** (선택사항)

TypeScript 타입과 유틸리티 함수를 NPM 패키지로 만들어 공유할 수 있습니다:

```bash
npm install @your-org/iris-metrics-types
```

```typescript
import { IrisMetric, MetricSearchParams } from "@your-org/iris-metrics-types";
```
