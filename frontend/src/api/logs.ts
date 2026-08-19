import { apiRequest } from "./client";
import type { CrawlLog } from "../types";

export function getLogs(): Promise<CrawlLog[]> {
  return apiRequest<CrawlLog[]>("/logs");
}

export function getCrawlLogs(
  jobId: string,
): Promise<CrawlLog[]> {
  return apiRequest<CrawlLog[]>(
    `/crawls/${jobId}/logs`,
  );
}