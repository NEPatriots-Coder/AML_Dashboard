import type { AssetsResponse, SourceCheckResponse } from "./types";

const RETRYABLE_STATUS = new Set([500, 502, 503, 504]);
const MAX_RETRIES = 4;
const RETRY_DELAYS_MS = [250, 500, 1000];

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchJsonWithRetry<T>(url: string, errorPrefix: string): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < MAX_RETRIES; attempt += 1) {
    try {
      const res = await fetch(url);
      if (res.ok) {
        return (await res.json()) as T;
      }

      if (!RETRYABLE_STATUS.has(res.status) || attempt === MAX_RETRIES - 1) {
        throw new Error(`${errorPrefix} (${res.status})`);
      }

      await sleep(RETRY_DELAYS_MS[Math.min(attempt, RETRY_DELAYS_MS.length - 1)]);
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (attempt === MAX_RETRIES - 1) {
        throw lastError;
      }
      await sleep(RETRY_DELAYS_MS[Math.min(attempt, RETRY_DELAYS_MS.length - 1)]);
    }
  }

  throw lastError ?? new Error(`${errorPrefix} (retry exhausted)`);
}

export async function fetchSourceCheck(): Promise<SourceCheckResponse> {
  return fetchJsonWithRetry<SourceCheckResponse>("/api/source/check", "Source check failed");
}

export async function fetchAssets(params: URLSearchParams): Promise<AssetsResponse> {
  const url = `/api/assets/live?${params.toString()}`;
  return fetchJsonWithRetry<AssetsResponse>(url, "Asset fetch failed");
}
