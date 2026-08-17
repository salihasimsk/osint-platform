import { apiRequest } from "./client";
import type { Source } from "../types";

export function getSources(): Promise<Source[]> {
  return apiRequest<Source[]>("/sources");
}
