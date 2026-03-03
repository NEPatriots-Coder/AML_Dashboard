import { useCallback, useEffect, useMemo, useState } from "react";
import type { FC } from "react";

import { DataTable } from "./components/DataTable";
import { FilterBar } from "./components/FilterBar";
import { SummaryCards } from "./components/SummaryCards";
import { COLUMN_ORDER, SORT_OPTIONS, toSpreadsheetLabel } from "./lib/columns";
import { fetchAssets, fetchSourceCheck } from "./lib/api";
import type { AssetRow, SourceCheckResponse } from "./lib/types";

type AppliedFilters = {
  query: string;
  bin: string;
  movementType: string;
  item: string;
  jiraTicket: string;
  owner: string;
  shippedTo: string;
  forceRefresh: boolean;
};

const EMPTY_FILTERS: AppliedFilters = {
  query: "",
  bin: "",
  movementType: "",
  item: "",
  jiraTicket: "",
  owner: "",
  shippedTo: "",
  forceRefresh: false,
};

export const App: FC = () => {
  const [rows, setRows] = useState<AssetRow[]>([]);
  const [selectedRow, setSelectedRow] = useState<AssetRow | null>(null);

  const [draftQuery, setDraftQuery] = useState(EMPTY_FILTERS.query);
  const [draftBinFilter, setDraftBinFilter] = useState(EMPTY_FILTERS.bin);
  const [draftMovementTypeFilter, setDraftMovementTypeFilter] = useState(EMPTY_FILTERS.movementType);
  const [draftItemFilter, setDraftItemFilter] = useState(EMPTY_FILTERS.item);
  const [draftJiraTicketFilter, setDraftJiraTicketFilter] = useState(EMPTY_FILTERS.jiraTicket);
  const [draftOwnerFilter, setDraftOwnerFilter] = useState(EMPTY_FILTERS.owner);
  const [draftShippedToFilter, setDraftShippedToFilter] = useState(EMPTY_FILTERS.shippedTo);
  const [draftForceRefresh, setDraftForceRefresh] = useState(EMPTY_FILTERS.forceRefresh);

  const [appliedFilters, setAppliedFilters] = useState<AppliedFilters>(EMPTY_FILTERS);

  const [sortBy, setSortBy] = useState("date");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [limit, setLimit] = useState(100);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sourceStatus, setSourceStatus] = useState<SourceCheckResponse | null>(null);

  const buildQueryParams = useCallback(
    (filters: AppliedFilters, includePagination: boolean) => {
      const params = new URLSearchParams();
      const appendMulti = (key: string, raw: string) => {
        raw
          .split(",")
          .map((value) => value.trim())
          .filter((value) => value.length > 0)
          .forEach((value) => params.append(key, value));
      };

      if (filters.query) params.set("q", filters.query.trim());
      appendMulti("bin", filters.bin);
      appendMulti("movement_type", filters.movementType);
      appendMulti("item", filters.item);
      appendMulti("jira_ticket", filters.jiraTicket);
      appendMulti("owner", filters.owner);
      appendMulti("shipped_to_received_from", filters.shippedTo);
      if (filters.forceRefresh) params.set("refresh", "true");

      params.set("sort_by", sortBy);
      params.set("sort_dir", sortDir);
      if (includePagination) {
        params.set("limit", String(limit));
        params.set("offset", String(offset));
      }
      return params;
    },
    [limit, offset, sortBy, sortDir],
  );

  const loadRows = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = buildQueryParams(appliedFilters, true);

      const [assetsResult, sourceResult] = await Promise.allSettled([
        fetchAssets(params),
        fetchSourceCheck(),
      ]);
      if (assetsResult.status !== "fulfilled") {
        throw assetsResult.reason;
      }
      const assets = assetsResult.value;
      setRows(assets.rows);
      setTotal(assets.total);

      if (sourceResult.status === "fulfilled") {
        setSourceStatus(sourceResult.value);
      } else {
        setSourceStatus({
          ok: false,
          source: "unknown",
          error: "Source check endpoint unavailable",
        });
      }

      if (assets.rows.length > 0) {
        const selectedKey = String(selectedRow?._source_key ?? "");
        const stillVisible = assets.rows.find((row) => String(row._source_key ?? "") === selectedKey);
        setSelectedRow(stillVisible ?? assets.rows[0]);
      } else {
        setSelectedRow(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown request error");
    } finally {
      setLoading(false);
    }
  }, [appliedFilters, buildQueryParams, selectedRow?._source_key]);

  const handleExport = useCallback(
    (format: "html" | "csv") => {
      const params = buildQueryParams(appliedFilters, false);
      const url = `/api/assets/live/export.${format}?${params.toString()}`;
      window.location.assign(url);
    },
    [appliedFilters, buildQueryParams],
  );

  useEffect(() => {
    void loadRows();
  }, [loadRows]);

  const binOptions = useMemo(() => {
    const values = new Set(
      rows
        .map((row) => String(row.bin ?? "").trim())
        .filter((value) => value.length > 0),
    );
    return Array.from(values).sort();
  }, [rows]);

  const movementTypeOptions = useMemo(() => {
    const values = new Set(
      rows.map((row) => String(row.movement_type ?? "").trim()).filter((value) => value.length > 0),
    );
    return Array.from(values).sort();
  }, [rows]);

  const itemOptions = useMemo(() => {
    const values = new Set(
      rows.map((row) => String(row.item ?? "").trim()).filter((value) => value.length > 0),
    );
    return Array.from(values).sort();
  }, [rows]);

  const jiraOptions = useMemo(() => {
    const values = new Set(
      rows.map((row) => String(row.jira_ticket ?? "").trim()).filter((value) => value.length > 0),
    );
    return Array.from(values).sort();
  }, [rows]);

  const ownerOptions = useMemo(() => {
    const values = new Set(
      rows.map((row) => String(row.owner ?? "").trim()).filter((value) => value.length > 0),
    );
    return Array.from(values).sort();
  }, [rows]);

  const shippedToOptions = useMemo(() => {
    const values = new Set(
      rows
        .map((row) => String(row.shipped_to_received_from ?? "").trim())
        .filter((value) => value.length > 0),
    );
    return Array.from(values).sort();
  }, [rows]);

  const activeFilterChips = useMemo(() => {
    const chips: Array<{ key: "query" | "bin" | "movementType" | "item" | "jiraTicket" | "owner" | "shippedTo"; label: string; value: string }> = [];
    if (appliedFilters.query) chips.push({ key: "query", label: "Query", value: appliedFilters.query });
    if (appliedFilters.bin) chips.push({ key: "bin", label: "BIN", value: appliedFilters.bin });
    if (appliedFilters.movementType) {
      chips.push({ key: "movementType", label: "Movement", value: appliedFilters.movementType });
    }
    if (appliedFilters.item) chips.push({ key: "item", label: "ITEM #", value: appliedFilters.item });
    if (appliedFilters.jiraTicket) chips.push({ key: "jiraTicket", label: "JIRA TICKET #", value: appliedFilters.jiraTicket });
    if (appliedFilters.owner) chips.push({ key: "owner", label: "OWNER", value: appliedFilters.owner });
    if (appliedFilters.shippedTo) {
      chips.push({ key: "shippedTo", label: "SHIPPED TO / RECEIVED FROM", value: appliedFilters.shippedTo });
    }
    return chips;
  }, [appliedFilters]);

  const applyDraftFilters = useCallback(() => {
    setOffset(0);
    setAppliedFilters({
      query: draftQuery.trim(),
      bin: draftBinFilter.trim(),
      movementType: draftMovementTypeFilter.trim(),
      item: draftItemFilter.trim(),
      jiraTicket: draftJiraTicketFilter.trim(),
      owner: draftOwnerFilter.trim(),
      shippedTo: draftShippedToFilter.trim(),
      forceRefresh: draftForceRefresh,
    });
  }, [draftBinFilter, draftForceRefresh, draftItemFilter, draftJiraTicketFilter, draftMovementTypeFilter, draftOwnerFilter, draftQuery, draftShippedToFilter]);

  const clearAllFilters = useCallback(() => {
    setDraftQuery(EMPTY_FILTERS.query);
    setDraftBinFilter(EMPTY_FILTERS.bin);
    setDraftMovementTypeFilter(EMPTY_FILTERS.movementType);
    setDraftItemFilter(EMPTY_FILTERS.item);
    setDraftJiraTicketFilter(EMPTY_FILTERS.jiraTicket);
    setDraftOwnerFilter(EMPTY_FILTERS.owner);
    setDraftShippedToFilter(EMPTY_FILTERS.shippedTo);
    setDraftForceRefresh(EMPTY_FILTERS.forceRefresh);
    setOffset(0);
    setAppliedFilters(EMPTY_FILTERS);
  }, []);

  const removeChip = useCallback(
    (key: "query" | "bin" | "movementType" | "item" | "jiraTicket" | "owner" | "shippedTo") => {
      const next = { ...appliedFilters };
      if (key === "query") {
        next.query = "";
        setDraftQuery("");
      }
      if (key === "bin") {
        next.bin = "";
        setDraftBinFilter("");
      }
      if (key === "movementType") {
        next.movementType = "";
        setDraftMovementTypeFilter("");
      }
      if (key === "item") {
        next.item = "";
        setDraftItemFilter("");
      }
      if (key === "jiraTicket") {
        next.jiraTicket = "";
        setDraftJiraTicketFilter("");
      }
      if (key === "owner") {
        next.owner = "";
        setDraftOwnerFilter("");
      }
      if (key === "shippedTo") {
        next.shippedTo = "";
        setDraftShippedToFilter("");
      }
      setOffset(0);
      setAppliedFilters(next);
    },
    [appliedFilters],
  );

  const headerSubtext = useMemo(() => {
    if (!sourceStatus) return "Awaiting source telemetry";
    if (!sourceStatus.ok) return `Source degraded: ${sourceStatus.error ?? "unknown"}`;
    const mode = sourceStatus.source_mode ? `(${sourceStatus.source_mode})` : "";
    const fallback = sourceStatus.using_fallback ? " · fallback active" : "";
    return `${sourceStatus.source.toUpperCase()} source ${mode} · ${sourceStatus.source_count ?? 0} rows available${fallback}`;
  }, [sourceStatus]);

  const sourceBadge = useMemo(() => {
    if (!sourceStatus) {
      return {
        label: "CHECKING SOURCE",
        className: "border-slate-300 bg-slate-100 text-slate-700",
      };
    }
    if (!sourceStatus.ok) {
      return {
        label: "SOURCE DEGRADED",
        className: "border-rose-300 bg-rose-50 text-rose-700",
      };
    }
    if (sourceStatus.using_fallback) {
      return {
        label: "CSV FALLBACK",
        className: "border-amber-300 bg-amber-50 text-amber-700",
      };
    }
    return {
      label: "LIVE GOOGLE",
      className: "border-emerald-300 bg-emerald-50 text-emerald-700",
    };
  }, [sourceStatus]);

  const page = Math.floor(offset / limit) + 1;
  const pageCount = Math.max(1, Math.ceil(total / limit));
  const selectedKey = selectedRow ? String(selectedRow._source_key ?? "") : null;

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-6 text-slate-900 sm:px-8">
      <div className="mx-auto flex max-w-[1600px] flex-col gap-5">
        <header className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <img
                src="/logos_print-07.png"
                alt="Corporate logo"
                className="h-14 w-14 rounded-md border border-slate-200 bg-white object-contain p-1"
              />
              <div>
                <h1 className="text-2xl font-semibold text-slate-900">Asset Movement Dashboard</h1>
                <span
                  className={`mt-2 inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold tracking-wide ${sourceBadge.className}`}
                >
                  {sourceBadge.label}
                </span>
                <p className="mt-1 text-sm text-slate-600">{headerSubtext}</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => void loadRows()}
              className="rounded-md border border-blue-300 bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100"
            >
              Refresh Data
            </button>
          </div>
        </header>

        <SummaryCards rows={rows} />

        <FilterBar
          query={draftQuery}
          binFilter={draftBinFilter}
          movementTypeFilter={draftMovementTypeFilter}
          itemFilter={draftItemFilter}
          jiraFilter={draftJiraTicketFilter}
          ownerFilter={draftOwnerFilter}
          shippedToFilter={draftShippedToFilter}
          refreshEnabled={draftForceRefresh}
          binOptions={binOptions}
          movementTypeOptions={movementTypeOptions}
          itemOptions={itemOptions}
          jiraOptions={jiraOptions}
          ownerOptions={ownerOptions}
          shippedToOptions={shippedToOptions}
          onQueryChange={setDraftQuery}
          onBinFilterChange={setDraftBinFilter}
          onMovementTypeChange={setDraftMovementTypeFilter}
          onItemFilterChange={setDraftItemFilter}
          onJiraFilterChange={setDraftJiraTicketFilter}
          onOwnerFilterChange={setDraftOwnerFilter}
          onShippedToFilterChange={setDraftShippedToFilter}
          onRefreshToggle={setDraftForceRefresh}
          onSearch={applyDraftFilters}
          onClear={clearAllFilters}
          onExportHtml={() => handleExport("html")}
          onExportCsv={() => handleExport("csv")}
        />

        {activeFilterChips.length > 0 && (
          <section className="flex flex-wrap gap-2 rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
            {activeFilterChips.map((chip) => (
              <button
                key={`${chip.key}:${chip.value}`}
                type="button"
                onClick={() => removeChip(chip.key)}
                className="rounded-full border border-slate-300 bg-slate-100 px-3 py-1 text-xs text-slate-700 hover:bg-slate-200"
                title="Remove filter"
              >
                {chip.label}: {chip.value} ×
              </button>
            ))}
          </section>
        )}

        <section className="grid grid-cols-1 gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm lg:grid-cols-[1fr_auto_auto_auto_auto_auto] lg:items-end">
          <label className="flex flex-col gap-1 text-slate-600">
            <span className="text-xs font-medium uppercase tracking-wide">Sort Field</span>
            <select
              value={sortBy}
              onChange={(event) => {
                setSortBy(event.target.value);
                setOffset(0);
              }}
              className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900"
            >
              {SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-1 text-slate-600">
            <span className="text-xs font-medium uppercase tracking-wide">Direction</span>
            <select
              value={sortDir}
              onChange={(event) => {
                const next = event.target.value === "asc" ? "asc" : "desc";
                setSortDir(next);
                setOffset(0);
              }}
              className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900"
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
          </label>

          <label className="flex flex-col gap-1 text-slate-600">
            <span className="text-xs font-medium uppercase tracking-wide">Rows / Page</span>
            <select
              value={limit}
              onChange={(event) => {
                setLimit(Number(event.target.value));
                setOffset(0);
              }}
              className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900"
            >
              {[25, 50, 100, 250].map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </label>

          <button
            type="button"
            onClick={() => {
              setOffset(Math.max(0, offset - limit));
            }}
            disabled={offset === 0}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-40"
          >
            Prev
          </button>

          <button
            type="button"
            onClick={() => {
              const nextOffset = offset + limit;
              if (nextOffset < total) setOffset(nextOffset);
            }}
            disabled={offset + limit >= total}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-40"
          >
            Next
          </button>

          <div className="text-xs font-medium uppercase tracking-wide text-slate-600">
            Page {page} / {pageCount} · {total} Total Rows
          </div>
        </section>

        {loading && (
          <section className="rounded-xl border border-slate-200 bg-white p-4 text-slate-600 shadow-sm">
            Loading asset movements...
          </section>
        )}

        {error && (
          <section className="rounded-xl border border-red-300 bg-red-50 p-4 text-red-700 shadow-sm">
            {error}
          </section>
        )}

        {!loading && !error && (
          <section className="grid grid-cols-1 gap-4 xl:grid-cols-[2.3fr_1fr]">
            <DataTable rows={rows} selectedRowKey={selectedKey} onRowSelect={setSelectedRow} />

            <aside className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-800">Row Inspector</h2>
              {!selectedRow && <p className="mt-3 text-slate-600">Select a row to inspect full values.</p>}

              {selectedRow && (
                <dl className="mt-3 grid gap-2 text-sm">
                  {COLUMN_ORDER.filter((key) => key in selectedRow).map((key) => (
                    <div key={key} className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
                      <dt className="text-[10px] font-semibold uppercase tracking-wide text-slate-600">
                        {toSpreadsheetLabel(key)}
                      </dt>
                      <dd className="mt-1 whitespace-pre-wrap text-slate-900">{String(selectedRow[key] ?? "")}</dd>
                    </div>
                  ))}
                </dl>
              )}
            </aside>
          </section>
        )}
      </div>
    </main>
  );
};
