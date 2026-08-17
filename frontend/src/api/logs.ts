import { apiRequest } from "./client";
import type { CrawlLog } from "../types";

export function getLogs(): Promise<CrawlLog[]> {
  return apiRequest<CrawlLog[]>("/logs");
}
