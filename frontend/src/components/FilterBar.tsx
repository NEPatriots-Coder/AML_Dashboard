import type { FC } from "react";

interface FilterBarProps {
  query: string;
  binFilter: string;
  movementTypeFilter: string;
  itemFilter: string;
  jiraFilter: string;
  ownerFilter: string;
  shippedToFilter: string;
  refreshEnabled: boolean;
  binOptions: string[];
  movementTypeOptions: string[];
  itemOptions: string[];
  jiraOptions: string[];
  ownerOptions: string[];
  shippedToOptions: string[];
  onQueryChange: (value: string) => void;
  onBinFilterChange: (value: string) => void;
  onMovementTypeChange: (value: string) => void;
  onItemFilterChange: (value: string) => void;
  onJiraFilterChange: (value: string) => void;
  onOwnerFilterChange: (value: string) => void;
  onShippedToFilterChange: (value: string) => void;
  onRefreshToggle: (enabled: boolean) => void;
  onSearch: () => void;
  onClear: () => void;
  onExportHtml: () => void;
  onExportCsv: () => void;
}

export const FilterBar: FC<FilterBarProps> = ({
  query,
  binFilter,
  movementTypeFilter,
  itemFilter,
  jiraFilter,
  ownerFilter,
  shippedToFilter,
  refreshEnabled,
  binOptions,
  movementTypeOptions,
  itemOptions,
  jiraOptions,
  ownerOptions,
  shippedToOptions,
  onQueryChange,
  onBinFilterChange,
  onMovementTypeChange,
  onItemFilterChange,
  onJiraFilterChange,
  onOwnerFilterChange,
  onShippedToFilterChange,
  onRefreshToggle,
  onSearch,
  onClear,
  onExportHtml,
  onExportCsv,
}) => {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        <label className="flex flex-col gap-1 text-slate-600">
          <span className="text-xs font-medium uppercase tracking-wide">Global Query</span>
          <input
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") onSearch();
            }}
            placeholder="Search any field..."
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none ring-blue-300 focus:ring"
          />
          <span className="text-[11px] text-slate-500">Use commas for multiple values (OR search)</span>
        </label>

        <label className="flex flex-col gap-1 text-slate-600">
          <span className="text-xs font-medium uppercase tracking-wide">Bin Contains</span>
          <input
            list="bin-options"
            value={binFilter}
            onChange={(event) => onBinFilterChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") onSearch();
            }}
            placeholder="STORAGE"
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none ring-blue-300 focus:ring"
          />
          <datalist id="bin-options">
            {binOptions.map((bin) => (
              <option key={bin} value={bin} />
            ))}
          </datalist>
        </label>

        <label className="flex flex-col gap-1 text-slate-600">
          <span className="text-xs font-medium uppercase tracking-wide">Movement Type</span>
          <input
            list="movement-type-options"
            value={movementTypeFilter}
            onChange={(event) => onMovementTypeChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") onSearch();
            }}
            placeholder="RECEIVED"
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none ring-blue-300 focus:ring"
          />
          <datalist id="movement-type-options">
            {movementTypeOptions.map((value) => (
              <option key={value} value={value} />
            ))}
          </datalist>
        </label>

        <label className="flex flex-col gap-1 text-slate-600">
          <span className="text-xs font-medium uppercase tracking-wide">Item #</span>
          <input
            list="item-options"
            value={itemFilter}
            onChange={(event) => onItemFilterChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") onSearch();
            }}
            placeholder="Item number"
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none ring-blue-300 focus:ring"
          />
          <datalist id="item-options">
            {itemOptions.map((value) => (
              <option key={value} value={value} />
            ))}
          </datalist>
        </label>

        <label className="flex flex-col gap-1 text-slate-600">
          <span className="text-xs font-medium uppercase tracking-wide">Jira Ticket #</span>
          <input
            list="jira-options"
            value={jiraFilter}
            onChange={(event) => onJiraFilterChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") onSearch();
            }}
            placeholder="PROC-####"
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none ring-blue-300 focus:ring"
          />
          <datalist id="jira-options">
            {jiraOptions.map((value) => (
              <option key={value} value={value} />
            ))}
          </datalist>
        </label>

        <label className="flex flex-col gap-1 text-slate-600">
          <span className="text-xs font-medium uppercase tracking-wide">Owner</span>
          <input
            list="owner-options"
            value={ownerFilter}
            onChange={(event) => onOwnerFilterChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") onSearch();
            }}
            placeholder="CW"
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none ring-blue-300 focus:ring"
          />
          <datalist id="owner-options">
            {ownerOptions.map((value) => (
              <option key={value} value={value} />
            ))}
          </datalist>
        </label>

        <label className="flex flex-col gap-1 text-slate-600">
          <span className="text-xs font-medium uppercase tracking-wide">Shipped To / Received From</span>
          <input
            list="shipped-to-options"
            value={shippedToFilter}
            onChange={(event) => onShippedToFilterChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") onSearch();
            }}
            placeholder="Supplier / Site"
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none ring-blue-300 focus:ring"
          />
          <datalist id="shipped-to-options">
            {shippedToOptions.map((value) => (
              <option key={value} value={value} />
            ))}
          </datalist>
        </label>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={onSearch}
          className="h-[42px] rounded-md border border-blue-300 bg-blue-50 px-4 text-sm font-medium text-blue-700 hover:bg-blue-100"
        >
          Search
        </button>
        <button
          type="button"
          onClick={onClear}
          className="h-[42px] rounded-md border border-slate-300 bg-slate-100 px-4 text-sm font-medium text-slate-700 hover:bg-slate-200"
        >
          Clear
        </button>
        <button
          type="button"
          onClick={onExportHtml}
          className="h-[42px] rounded-md border border-emerald-300 bg-emerald-50 px-4 text-sm font-medium text-emerald-700 hover:bg-emerald-100"
        >
          Export HTML
        </button>
        <button
          type="button"
          onClick={onExportCsv}
          className="h-[42px] rounded-md border border-emerald-300 bg-emerald-50 px-4 text-sm font-medium text-emerald-700 hover:bg-emerald-100"
        >
          Export CSV
        </button>
        <label className="flex h-[42px] items-center gap-2 rounded-md border border-slate-300 px-3 text-slate-700">
          <input
            type="checkbox"
            checked={refreshEnabled}
            onChange={(event) => onRefreshToggle(event.target.checked)}
            className="accent-blue-600"
          />
          <span className="text-xs font-medium uppercase tracking-wide">Force Refresh</span>
        </label>
      </div>
    </section>
  );
};
