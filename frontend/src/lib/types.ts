export interface AssetRow {
  [key: string]: string | number | null | undefined;
}

export interface SourceCheckResponse {
  ok: boolean;
  source: string;
  source_count?: number;
  source_mode?: string;
  using_fallback?: boolean;
  fallback_reason?: string;
  error?: string;
}

export interface AssetsResponse {
  count: number;
  total: number;
  offset: number;
  limit: number;
  sort_by: string;
  sort_dir: "asc" | "desc";
  rows: AssetRow[];
}
