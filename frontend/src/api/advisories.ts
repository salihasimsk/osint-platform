import { apiRequest } from "./client";
import type { Advisory } from "../types";

export interface AdvisoryFilters {
  page?: number;
  page_size?: number;
  keyword?: string;
  organization?: string;
  severity?: string;
  source_domain?: string;
  date_from?: string;
  date_to?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export function getAdvisories(
  filters: AdvisoryFilters = {},
): Promise<Advisory[]> {
  const query = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (
      value !== undefined &&
      value !== null &&
      value !== ""
    ) {
      query.set(key, String(value));
    }
  });

  const queryString = query.toString();

  const endpoint = queryString
    ? `/advisories?${queryString}`
    : "/advisories";

  return apiRequest<Advisory[]>(endpoint);
}

export function getAdvisory(
  advisoryId: number,
): Promise<Advisory> {
  return apiRequest<Advisory>(
    `/advisories/${advisoryId}`,
  );
}

export function getAdvisoriesCsvUrl(
  filters: AdvisoryFilters = {},
): string {
  const query = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (
      value !== undefined &&
      value !== null &&
      value !== ""
    ) {
      query.set(key, String(value));
    }
  });

  const queryString = query.toString();

  return queryString
    ? `/api/advisories/export/csv?${queryString}`
    : "/api/advisories/export/csv";
}
