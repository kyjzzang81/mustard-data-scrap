// IRIS+ 메트릭 데이터 타입 정의
// 생성일: 2025-09-19
// Supabase 테이블: iris_metrics

export interface IrisMetric {
  id: number;

  // 기본 정보 (다국어)
  title_en: string;
  title_ko: string | null;
  data_id: string;
  relative_path: string | null;
  detail_url: string | null;

  // 메타데이터
  reporting_format: string | null;
  metric_type: string | null;
  metric_level: string | null;
  iris_citation: string | null;

  // 상세 정보 (다국어 JSON)
  definition: MultiLanguageContent | null;
  usage_guidance: MultiLanguageContent | null;
  impact_categories: MultiLanguageContent | null;
  sdg_goals: MultiLanguageContent | null;
  metric_history: any | null; // 버전 히스토리
  related_metrics: any | null; // 관련 메트릭들

  // 메타 정보
  scraped_at: string | null;
  translated_at: string | null;
  success: boolean;
  version: string;

  // 타임스탬프
  created_at: string;
  updated_at: string;
}

// 다국어 컨텐츠 구조
export interface MultiLanguageContent {
  en: ContentData | null;
  ko: ContentData | null;
}

// 컨텐츠 데이터 구조
export interface ContentData {
  title: string;
  content: {
    paragraphs: string[];
    lists: ListItem[];
    headings: HeadingItem[];
    other_elements: OtherElement[];
    raw_text: string;
  };
}

export interface ListItem {
  type: "ul" | "ol";
  items: string[];
}

export interface HeadingItem {
  tag: string;
  text: string;
}

export interface OtherElement {
  tag: string;
  text: string;
  class: string[];
}

// 검색/필터용 타입들
export interface MetricSearchParams {
  title?: string;
  data_id?: string;
  metric_type?: string;
  metric_level?: string;
  impact_category?: string;
  sdg_goal?: string;
  limit?: number;
  offset?: number;
}

// API 응답 타입들
export interface MetricsResponse {
  data: IrisMetric[];
  count: number;
  error: string | null;
}

export interface SingleMetricResponse {
  data: IrisMetric | null;
  error: string | null;
}

// 통계용 타입들
export interface ImpactCategorySummary {
  rank: number;
  category_en: string;
  category_ko?: string;
  metric_count: number;
  metric_types: string[];
  sample_metrics: string[];
}

export interface SdgGoalSummary {
  sdg_en: string;
  sdg_ko?: string;
  metric_count: number;
  sample_metrics: string[];
}

// 상수들
export const METRIC_TYPES = [
  "Metric",
  "Product/Service",
  "Organization",
  // 추가 타입들...
] as const;

export const METRIC_LEVELS = [
  "Product/Service",
  "Organization",
  // 추가 레벨들...
] as const;

export type MetricType = (typeof METRIC_TYPES)[number];
export type MetricLevel = (typeof METRIC_LEVELS)[number];
