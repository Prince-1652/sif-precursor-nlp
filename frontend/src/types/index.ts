export interface Report {
  id: string;
  source: string;
  source_record_id?: string;
  report_type: string;
  original_text: string;
  processing_status: string;
  is_mixed_language: boolean;
  ai_used: boolean;
  pipeline_version: string;
  created_at: string;
  updated_at: string;
  // Included if processed
  extracted_hazards?: string[];
  root_causes?: string[];
  severity_score?: number;
  sif_potential?: boolean;
  sif_score?: number;
  risk_band?: string;
  life_saving_rules?: string[];
  precursors?: string[];
}

export interface DashboardStats {
  total_reports: number;
  completed_reports: number;
  high_severity: number;
}

export interface DashboardSummary {
  total_reports: number;
  sif_count: number;
  sif_percentage: number;
  high_risk_count: number;
  review_count: number;
  ai_processed_count: number;
  total_sites: number;
  lsr_distribution: Record<string, number>;
  generated_at: string;
  volume_trend?: string;
  sif_trend?: string;
  trending_terms?: string[];
}

export interface SiteDensity {
  site_id: string;
  valid_reports: number;
  sif_reports: number;
  density: number;
  low_sample: boolean;
}

export interface Pattern {
  site_id: string;
  activity: string;
  lsr_rule: string;
  failed_barrier: string;
  frequency: number;
  trend: string;
}
