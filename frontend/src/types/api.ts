export interface Indicator {
  indicator_code: string;
  indicator_name: string;
  category: string;
  frequency: string;
  unit: string;
  source: string;
  country_code: string;
  is_active: boolean;
  first_obs_date: string | null;
  last_obs_date: string | null;
}

export interface Observation {
  observation_date: string;
  value: string;
  value_text: string | null;
  quality_status: string;
}

export interface SeriesData {
  indicator_code: string;
  indicator_name: string;
  unit: string;
  observations: Observation[];
  count: number;
}

export interface LatestSnapshot {
  indicator_code: string;
  indicator_name: string;
  category: string;
  as_of_date: string;
  latest_value: string;
  prev_value: string | null;
  delta_abs: string | null;
  delta_pct: string | null;
  unit: string;
  updated_at: string;
}

export interface DashboardOverview {
  indicators: LatestSnapshot[];
  as_of: string;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  version: string;
  services: {
    redis: string;
    bigquery: string;
  };
}
