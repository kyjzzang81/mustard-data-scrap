-- SDGs 데이터용 Supabase 스키마

-- SDGs 목표 테이블
CREATE TABLE IF NOT EXISTS sdg_goals (
    id SERIAL PRIMARY KEY,
    goal_number INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    color_code VARCHAR(7), -- HEX 색상 코드
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SDGs 지표 테이블
CREATE TABLE IF NOT EXISTS sdg_indicators (
    id SERIAL PRIMARY KEY,
    indicator_id VARCHAR(50) UNIQUE NOT NULL, -- 예: 1.1.1
    goal_id INTEGER REFERENCES sdg_goals(id),
    title TEXT NOT NULL,
    description TEXT,
    tier_classification VARCHAR(20), -- Tier I, II, III
    custodian_agencies TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SDGs 메타데이터 파일 테이블
CREATE TABLE IF NOT EXISTS sdg_metadata_files (
    id SERIAL PRIMARY KEY,
    indicator_id VARCHAR(50) REFERENCES sdg_indicators(indicator_id),
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    file_type VARCHAR(10) DEFAULT 'pdf',
    title TEXT,
    author TEXT,
    pages INTEGER,
    creation_date TIMESTAMP,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(20) DEFAULT 'pending' -- pending, processing, completed, failed
);

-- SDGs 프레임워크 데이터 테이블
CREATE TABLE IF NOT EXISTS sdg_framework_data (
    id SERIAL PRIMARY KEY,
    indicator_id VARCHAR(50) REFERENCES sdg_indicators(indicator_id),
    framework_version VARCHAR(20),
    data_source TEXT,
    raw_data JSONB,
    processed_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SDGs 국가별 데이터 테이블 (향후 확장용)
CREATE TABLE IF NOT EXISTS sdg_country_data (
    id SERIAL PRIMARY KEY,
    indicator_id VARCHAR(50) REFERENCES sdg_indicators(indicator_id),
    country_code VARCHAR(3) NOT NULL,
    country_name TEXT NOT NULL,
    year INTEGER NOT NULL,
    value NUMERIC,
    unit VARCHAR(50),
    source TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(indicator_id, country_code, year)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_sdg_indicators_goal_id ON sdg_indicators(goal_id);
CREATE INDEX IF NOT EXISTS idx_sdg_indicators_indicator_id ON sdg_indicators(indicator_id);
CREATE INDEX IF NOT EXISTS idx_sdg_metadata_files_indicator_id ON sdg_metadata_files(indicator_id);
CREATE INDEX IF NOT EXISTS idx_sdg_metadata_files_processing_status ON sdg_metadata_files(processing_status);
CREATE INDEX IF NOT EXISTS idx_sdg_framework_data_indicator_id ON sdg_framework_data(indicator_id);
CREATE INDEX IF NOT EXISTS idx_sdg_country_data_indicator_country ON sdg_country_data(indicator_id, country_code);
CREATE INDEX IF NOT EXISTS idx_sdg_country_data_year ON sdg_country_data(year);

-- RLS (Row Level Security) 설정
ALTER TABLE sdg_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE sdg_indicators ENABLE ROW LEVEL SECURITY;
ALTER TABLE sdg_metadata_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE sdg_framework_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE sdg_country_data ENABLE ROW LEVEL SECURITY;

-- 공개 읽기 정책 (필요에 따라 수정)
CREATE POLICY "Allow public read access" ON sdg_goals FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON sdg_indicators FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON sdg_metadata_files FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON sdg_framework_data FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON sdg_country_data FOR SELECT USING (true);

-- 기본 SDGs 목표 데이터 삽입
INSERT INTO sdg_goals (goal_number, title, description, color_code) VALUES
(1, 'No Poverty', 'End poverty in all its forms everywhere', '#E5243B'),
(2, 'Zero Hunger', 'End hunger, achieve food security and improved nutrition and promote sustainable agriculture', '#DDA63A'),
(3, 'Good Health and Well-being', 'Ensure healthy lives and promote well-being for all at all ages', '#4C9F38'),
(4, 'Quality Education', 'Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all', '#C5192D'),
(5, 'Gender Equality', 'Achieve gender equality and empower all women and girls', '#FF3A21'),
(6, 'Clean Water and Sanitation', 'Ensure availability and sustainable management of water and sanitation for all', '#26BDE2'),
(7, 'Affordable and Clean Energy', 'Ensure access to affordable, reliable, sustainable and modern energy for all', '#FCC30B'),
(8, 'Decent Work and Economic Growth', 'Promote sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all', '#A21942'),
(9, 'Industry, Innovation and Infrastructure', 'Build resilient infrastructure, promote inclusive and sustainable industrialization and foster innovation', '#FD6925'),
(10, 'Reduced Inequalities', 'Reduce inequality within and among countries', '#DD1367'),
(11, 'Sustainable Cities and Communities', 'Make cities and human settlements inclusive, safe, resilient and sustainable', '#FD9D24'),
(12, 'Responsible Consumption and Production', 'Ensure sustainable consumption and production patterns', '#BF8B2E'),
(13, 'Climate Action', 'Take urgent action to combat climate change and its impacts', '#3F7E44'),
(14, 'Life Below Water', 'Conserve and sustainably use the oceans, seas and marine resources for sustainable development', '#0A97D9'),
(15, 'Life on Land', 'Protect, restore and promote sustainable use of terrestrial ecosystems, sustainably manage forests, combat desertification, and halt and reverse land degradation and halt biodiversity loss', '#56C02B'),
(16, 'Peace, Justice and Strong Institutions', 'Promote peaceful and inclusive societies for sustainable development, provide access to justice for all and build effective, accountable and inclusive institutions at all levels', '#00689D'),
(17, 'Partnerships for the Goals', 'Strengthen the means of implementation and revitalize the global partnership for sustainable development', '#19486A')
ON CONFLICT (goal_number) DO NOTHING;
