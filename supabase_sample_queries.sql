-- IRIS+ 메트릭 데이터 샘플 쿼리들
-- 생성일: 2025-09-19 03:36:39

-- 1. 모든 Impact Categories 조회
SELECT 
    jsonb_array_elements_text(
        jsonb_path_query_array(impact_categories, '$.en.content.headings[*].text')
    ) as category_name,
    COUNT(*) as metric_count
FROM iris_metrics 
WHERE impact_categories IS NOT NULL
GROUP BY category_name
ORDER BY metric_count DESC;

-- 2. 특정 카테고리 메트릭 조회 (예: Water)
SELECT title_en, data_id, metric_type
FROM iris_metrics 
WHERE impact_categories @> '{"en": {"content": {"headings": [{"text": "Water"}]}}}';

-- 3. SDG 목표별 메트릭 통계
SELECT 
    jsonb_array_elements_text(
        jsonb_path_query_array(sdg_goals, '$.en.content.headings[*].text')
    ) as sdg_name,
    COUNT(*) as metric_count
FROM iris_metrics 
WHERE sdg_goals IS NOT NULL
GROUP BY sdg_name
ORDER BY metric_count DESC;

-- 4. 메트릭 타입별 분포
SELECT metric_type, COUNT(*) as count
FROM iris_metrics 
GROUP BY metric_type
ORDER BY count DESC;

-- 5. 정의에서 키워드 검색 (영문)
SELECT title_en, data_id, definition->>'en' as definition_en
FROM iris_metrics 
WHERE definition->>'en' ILIKE '%water%'
LIMIT 10;

-- 6. 사용 가이드라인에서 검색
SELECT title_en, data_id
FROM iris_metrics 
WHERE usage_guidance->'en'->'content'->>'raw_text' ILIKE '%measurement%'
LIMIT 10;

-- 7. 복합 조건 검색 (Water 카테고리 + Clean Water SDG)
SELECT title_en, data_id, metric_type
FROM iris_metrics 
WHERE impact_categories @> '{"en": {"content": {"headings": [{"text": "Water"}]}}}' 
  AND sdg_goals @> '{"en": {"content": {"headings": [{"text": "Clean Water and Sanitation"}]}}}';

-- 8. 최근 업데이트된 메트릭들
SELECT title_en, data_id, updated_at
FROM iris_metrics 
ORDER BY updated_at DESC
LIMIT 20;

-- 발견된 데이터 통계:
-- Impact Categories: 17개
-- SDG Goals: 17개  
-- Metric Types: 3개
-- 주요 Impact Categories: Water, Biodiversity and Ecosystems, Cross Category, Financial Services, Land, Oceans & Coastal Zones, Real Estate, Energy, Education, Climate
-- 주요 SDG Goals: Life on Land, No Poverty, Industry, Innovation and Infrastructure, Peace and Justice Strong Institutions, Good Health and Well-being, Sustainable Cities and Communities, Life Below Water, Climate Action, Responsible Consumption and Production, Reduced Inequality
-- Metric Types: Metrics, Submetric, Metric
