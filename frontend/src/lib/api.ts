import type { AssetsResponse, SourceCheckResponse } from "./types";

export async function fetchSourceCheck(): Promise<SourceCheckResponse> {
  const res = await fetch("/api/source/check");
  if (!res.ok) {
    throw new Error(`Source check failed (${res.status})`);
  }
  return res.json();
}

export async function fetchAssets(params: URLSearchParams): Promise<AssetsResponse> {
  const url = `/api/assets/live?${params.toString()}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Asset fetch failed (${res.status})`);
  }
  return res.json();
}
