import { apiRequest } from "./client";
import type {
  CrawlCreateRequest,
  CrawlJob,
} from "../types";

export function getCrawlJobs(): Promise<CrawlJob[]> {
  return apiRequest<CrawlJob[]>("/crawls");
}

export function getCrawlJob(
  jobId: string,
): Promise<CrawlJob> {
  return apiRequest<CrawlJob>(
    `/crawls/${encodeURIComponent(jobId)}`,
  );
}

export function startCrawl(
  request: CrawlCreateRequest,
): Promise<CrawlJob> {
  return apiRequest<CrawlJob>("/crawls", {
    method: "POST",
    body: JSON.stringify(request),
  });
}
