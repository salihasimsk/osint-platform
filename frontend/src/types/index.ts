export type CrawlStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "stopping"
  | "stopped";

export type Severity =
  | "critical"
  | "high"
  | "medium"
  | "moderate"
  | "low"
  | null;

export interface HealthResponse {
  status: string;
  database: string;
  crawler: string;
}

export interface Source {
  id: number;
  name: string;
  base_url: string;
  enabled_status: boolean;
  request_delay: number;
  created_date: string;
  updated_date: string | null;
  last_crawl_date: string | null;
}

export interface SourceCreateRequest {
  name: string;
  base_url: string;
  enabled_status: boolean;
  request_delay: number;
}

export interface CrawlJob {
  job_id: string;
  status: CrawlStatus;
  progress: number;
  pages_visited: number;
  records_extracted: number;
  error_count: number;
  started_date: string | null;
  completed_date: string | null;
}

export interface CrawlCreateRequest {
  source_ids: number[];
  maximum_pages: number;
  date_from?: string | null;
  keywords?: string[] | null;
}

export interface Advisory {
  id: number;
  title: string;
  organization: string;
  publication_date: string | null;
  url: string;
  source_domain: string;
  cve: string | null;
  product: string | null;
  severity: Severity;
  summary: string | null;
  crawl_job_id: number | null;
  collection_date: string;
}

export interface CrawlLog {
  id: number;
  crawl_job_id: number | null;
  log_level: string;
  message: string;
  source: string | null;
  timestamp: string;
}

export interface StatisticsSummary {
  total_advisories: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  active_sources: number;
  completed_crawls: number;
  unknown_severity: number;
  by_organization: Record<string, number>;
}
