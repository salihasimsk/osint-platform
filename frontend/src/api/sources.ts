import { apiRequest } from "./client";

import type {
  Source,
  SourceCreateRequest,
} from "../types";


export function getSources(): Promise<Source[]> {
  return apiRequest<Source[]>("/sources");
}


export function createSource(
  source: SourceCreateRequest,
): Promise<Source> {
  return apiRequest<Source>(
    "/sources",
    {
      method: "POST",
      body: JSON.stringify(source),
    },
  );
}


export function updateSourceStatus(
  sourceId: number,
  enabled: boolean,
): Promise<Source> {
  return apiRequest<Source>(
    `/sources/${sourceId}/status?enabled=${enabled}`,
    {
      method: "PATCH",
    },
  );
}


export function updateSource(
  sourceId: number,
  source: {
    name: string;
    base_url: string;
    enabled_status: boolean;
    request_delay: number;
  },
): Promise<Source> {
  return apiRequest<Source>(
    `/sources/${sourceId}`,
    {
      method: "PUT",
      body: JSON.stringify(source),
    },
  );
}


export interface SourceRobotsStatus {
  source_id: number;
  allowed: boolean;
}


export function getSourceRobotsStatus(
  sourceId: number,
): Promise<SourceRobotsStatus> {
  return apiRequest<SourceRobotsStatus>(
    `/sources/${sourceId}/robots`,
  );
}