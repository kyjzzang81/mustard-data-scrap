# 🚀 다른 프로젝트와 공유하기 (간단 버전)

## 🎯 **가장 쉬운 방법**

### 1. **타입 파일만 복사해가기**

다른 프로젝트에서 이렇게 하세요:

```bash
# 타입 파일 다운로드
curl -o iris-types.ts https://raw.githubusercontent.com/kyjzzang81/mustard/data-scrap/types/iris-metrics.types.ts

# 또는 직접 복사
cp /path/to/this/repo/types/iris-metrics.types.ts ./src/types/
```

### 2. **바로 사용**

```typescript
import { IrisMetric, MetricSearchParams } from "./iris-types";

// 타입 안전하게 사용
const metric: IrisMetric = {
  id: 1,
  title_en: "Account Value",
  data_id: "PI1653",
  // ... 나머지 필드들
};

// 검색 파라미터도 타입 안전
const params: MetricSearchParams = {
  metric_type: "Metric",
  limit: 20,
};
```

## 📋 **필요한 파일들**

### **필수 파일** ⭐

- `types/iris-metrics.types.ts` - TypeScript 타입 정의

### **참고 파일**

- `docs/api-documentation.md` - 테이블 구조 설명
- `supabase_schema.sql` - 테이블 생성 스크립트
- `supabase_sample_queries.sql` - 쿼리 예시

## 🔗 **GitHub 링크**

팀원들에게 이 링크 공유하세요:

- **타입 파일**: https://github.com/kyjzzang81/mustard/blob/data-scrap/types/iris-metrics.types.ts
- **API 문서**: https://github.com/kyjzzang81/mustard/blob/data-scrap/docs/api-documentation.md
- **테이블 스키마**: https://github.com/kyjzzang81/mustard/blob/data-scrap/supabase_schema.sql

## 🌐 **Supabase 연결 정보**

```bash
# 환경변수 설정
SUPABASE_URL=https://bianqiestqutnbbnnwmk.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

## 🔄 **업데이트 방법**

새 테이블이 추가되거나 구조가 변경되면:

1. 이 저장소에서 파일 업데이트
2. 팀원들에게 "파일 다시 복사해가세요" 알림
3. 끝! 😊

---

**이게 제일 간단합니다!** 복잡한 패키지 관리 없이 필요한 파일만 복사해서 쓰면 됩니다.
