# IRIS+ 메트릭 상세 페이지 구조

IRIS+ 메트릭 상세 페이지의 `.content-area` 내 표준 구조를 분석한 결과입니다.

## 📋 표준 페이지 구조

```
📄 메트릭 상세 페이지 (.content-area)
├── 📖 제목 (h1): 메트릭명(ID)
├── 🧮 계산 방법 (h5: Calculation)
├── 📋 각주 (h5: Footnote)
├── 📘 사용 가이드라인 (h4: Usage Guidance)
├── 🔗 관련 메트릭들 (h4: Related metrics)
├── 📊 임팩트 카테고리 & 테마 (h4: Impact Categories & Themes)
│   └── 카테고리들 (h5: Water, Real Estate 등)
├── 🎯 SDG 목표 & 타겟 (h4: SDG Goals & Targets)
│   └── SDG들 (h5: Clean Water and Sanitation 등)
├── 📈 메트릭 히스토리 (h4: Metric History)
└── ℹ️ IRIS 사용 권장사항 (h3: IRIS Metrics Work Better in Sets)
```

## 🔍 각 섹션 설명

### 1. 메트릭 제목 (h1)

- 형식: `메트릭명(메트릭ID)`
- 예시: `Water Consumed: Surface Water(OI8060)`

### 2. 계산 방법 (h5: Calculation)

- 메트릭 계산 공식 또는 방법론
- 일부 메트릭에만 존재

### 3. 각주 (h5: Footnote)

- 메트릭 사용 시 주의사항 및 가정들
- 대부분의 메트릭에 존재 (28/30개)

### 4. 사용 가이드라인 (h4: Usage Guidance)

- 메트릭의 의도된 사용법과 해석 방법
- 모든 메트릭에 존재 (30/30개)

### 5. 관련 메트릭들 (h4: Related metrics)

- 함께 사용하면 좋은 다른 메트릭들의 링크
- 일부 메트릭에만 존재 (11/30개)

### 6. 임팩트 카테고리 & 테마 (h4: Impact Categories & Themes)

- IRIS+에서 정의한 임팩트 분야 분류
- 모든 메트릭에 존재 (30/30개)
- 주요 카테고리: Water, Real Estate, Cross Category, Land, Agriculture 등

### 7. SDG 목표 & 타겟 (h4: SDG Goals & Targets)

- UN 지속가능발전목표와의 연결
- 대부분의 메트릭에 존재 (27/30개)
- 주요 SDG: Clean Water and Sanitation, Sustainable Cities and Communities 등

### 8. 메트릭 히스토리 (h4: Metric History)

- IRIS 버전별 메트릭 변경 이력
- 모든 메트릭에 존재 (30/30개)

### 9. IRIS 사용 권장사항 (h3: IRIS Metrics Work Better in Sets)

- 메트릭을 세트로 사용하는 것에 대한 안내
- 모든 메트릭에 존재 (30/30개)

## 📊 분석 결과 통계

### 임팩트 카테고리 분포 (상위 10개)

- Water: 22개 메트릭
- Real Estate: 18개 메트릭
- Cross Category: 7개 메트릭
- Land: 5개 메트릭
- Agriculture: 4개 메트릭
- Biodiversity and Ecosystems: 3개 메트릭
- Climate: 3개 메트릭
- Waste: 2개 메트릭
- Pollution: 2개 메트릭
- Financial Services: 1개 메트릭

### SDG 목표 분포 (상위 10개)

- Clean Water and Sanitation (SDG 6): 22개 메트릭
- Sustainable Cities and Communities (SDG 11): 22개 메트릭
- No Poverty (SDG 1): 17개 메트릭
- Responsible Consumption and Production (SDG 12): 16개 메트릭
- Decent Work and Economic Growth (SDG 8): 13개 메트릭
- Good Health and Well-being (SDG 3): 13개 메트릭
- Industry, Innovation and Infrastructure (SDG 9): 9개 메트릭
- Reduced Inequality (SDG 10): 5개 메트릭
- Gender Equality (SDG 5): 3개 메트릭
- Climate Action (SDG 13): 1개 메트릭

### 메트릭 유형 분포

- PD (Product/Service Impact): 11개
- OI (Operational Impact): 10개
- PI (Product/Service Impact): 4개
- OD (Organization Description): 3개
- FP (Financial Performance): 2개

## 🎯 데이터 수집 시 주의사항

1. **필수 섹션**: Usage Guidance, Impact Categories & Themes, Metric History는 모든 메트릭에 존재
2. **선택적 섹션**: Calculation, Related metrics는 일부 메트릭에만 존재
3. **HTML 구조**: h4는 주요 섹션, h5는 하위 항목을 나타냄
4. **텍스트 추출**: 각 섹션의 단락(p 태그) 내용을 수집해야 실제 내용 파악 가능

---

_분석 기준: 마지막 30개 메트릭 상세 페이지 (2025-09-18 분석)_
