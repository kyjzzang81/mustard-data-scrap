-- IRIS+ 메트릭 데이터를 위한 Supabase 테이블 구조
-- 방식 A: JSON 안에 다국어 포함

CREATE TABLE iris_metrics (
    id SERIAL PRIMARY KEY,
    
    -- 기본 정보 (다국어)
    title_en TEXT NOT NULL,
    title_ko TEXT,
    data_id TEXT UNIQUE NOT NULL,
    relative_path TEXT,
    detail_url TEXT,
    
    -- 메타데이터 (검색 최적화를 위해 별도 컬럼)
    reporting_format TEXT,
    metric_type TEXT,
    metric_level TEXT,
    iris_citation TEXT,
    
    -- 상세 정보 (다국어 JSON 구조)
    definition JSONB, -- {"en": "...", "ko": "..."}
    usage_guidance JSONB, -- {"en": {...}, "ko": {...}}
    impact_categories JSONB, -- {"en": {...}, "ko": {...}}
    sdg_goals JSONB, -- {"en": {...}, "ko": {...}}
    metric_history JSONB, -- 버전 히스토리 (영문만)
    related_metrics JSONB, -- 관련 메트릭들
    
    -- 메타 정보
    scraped_at TIMESTAMP,
    translated_at TIMESTAMP,
    success BOOLEAN DEFAULT true,
    version TEXT DEFAULT 'v5.3b',
    
    -- 타임스탬프
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_iris_metrics_data_id ON iris_metrics(data_id);
CREATE INDEX idx_iris_metrics_metric_type ON iris_metrics(metric_type);
CREATE INDEX idx_iris_metrics_metric_level ON iris_metrics(metric_level);
CREATE INDEX idx_iris_metrics_updated_at ON iris_metrics(updated_at);

-- JSON 검색 최적화 인덱스
CREATE INDEX idx_iris_metrics_impact_categories ON iris_metrics USING GIN (impact_categories);
CREATE INDEX idx_iris_metrics_sdg_goals ON iris_metrics USING GIN (sdg_goals);
CREATE INDEX idx_iris_metrics_usage_guidance ON iris_metrics USING GIN (usage_guidance);

-- 업데이트 트리거 (updated_at 자동 갱신)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_iris_metrics_updated_at 
    BEFORE UPDATE ON iris_metrics 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 유용한 뷰들

-- 1. Impact Category 마스터 뷰 (다국어)
CREATE VIEW impact_categories_summary AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) as rank,
    jsonb_array_elements_text(jsonb_path_query_array(impact_categories, '$.en.content.headings[*].text')) as category_en,
    -- 추후 한국어 번역 추가 시: jsonb_array_elements_text(jsonb_path_query_array(impact_categories, '$.ko.content.headings[*].text')) as category_ko,
    COUNT(*) as metric_count,
    ARRAY_AGG(DISTINCT metric_type) as metric_types,
    ARRAY_AGG(data_id ORDER BY title_en) as sample_metrics
FROM iris_metrics 
WHERE impact_categories IS NOT NULL
GROUP BY category_en
ORDER BY metric_count DESC;

-- 2. SDG 목표 요약 뷰
CREATE VIEW sdg_goals_summary AS
SELECT 
    jsonb_array_elements_text(jsonb_path_query_array(sdg_goals, '$.en.content.headings[*].text')) as sdg_en,
    COUNT(*) as metric_count,
    ARRAY_AGG(data_id ORDER BY title_en) as sample_metrics
FROM iris_metrics 
WHERE sdg_goals IS NOT NULL
GROUP BY sdg_en
ORDER BY metric_count DESC;

-- 3. 메트릭 검색 뷰 (다국어 지원)
CREATE VIEW metrics_search AS
SELECT 
    id,
    data_id,
    COALESCE(title_ko, title_en) as title,
    title_en,
    title_ko,
    metric_type,
    metric_level,
    COALESCE(definition->>'ko', definition->>'en') as definition,
    impact_categories,
    sdg_goals,
    created_at
FROM iris_metrics;

-- 샘플 쿼리들

-- Impact Category별 메트릭 조회 (영문)
/*
SELECT title_en, data_id, metric_type
FROM iris_metrics 
WHERE impact_categories @> '{"en": {"content": {"headings": [{"text": "Water"}]}}}';
*/

-- 특정 SDG 관련 메트릭 조회
/*
SELECT title_en, data_id
FROM iris_metrics 
WHERE sdg_goals @> '{"en": {"content": {"headings": [{"text": "Clean Water and Sanitation"}]}}}';
*/

-- 메트릭 타입별 통계
/*
SELECT metric_type, COUNT(*) as count
FROM iris_metrics 
GROUP BY metric_type
ORDER BY count DESC;
*/

-- 전체 텍스트 검색 (정의에서)
/*
SELECT title_en, data_id
FROM iris_metrics 
WHERE definition->>'en' ILIKE '%water%'
   OR definition->>'ko' ILIKE '%물%';
*/
