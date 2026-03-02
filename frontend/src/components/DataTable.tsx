import type { FC } from "react";
import { COLUMN_ORDER, toSpreadsheetLabel } from "../lib/columns";
import type { AssetRow } from "../lib/types";

interface DataTableProps {
  rows: AssetRow[];
  selectedRowKey: string | null;
  onRowSelect: (row: AssetRow) => void;
}

export const DataTable: FC<DataTableProps> = ({ rows, selectedRowKey, onRowSelect }) => {
  if (rows.length === 0) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-6 text-center text-slate-600 shadow-sm">
        No rows matched the current filters.
      </section>
    );
  }

  const availableColumns = Object.keys(rows[0]);
  const orderedColumns = COLUMN_ORDER.filter((col) => availableColumns.includes(col));

  return (
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="max-h-[60vh] overflow-auto">
        <table className="min-w-full border-collapse text-left text-sm">
          <thead className="sticky top-0 bg-slate-50">
            <tr>
              {orderedColumns.map((column) => (
                <th key={column} className="border-b border-slate-200 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-slate-700">
                  {toSpreadsheetLabel(column)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => {
              const rowKey = String(row._source_key ?? idx);
              const isSelected = selectedRowKey === rowKey;
              return (
                <tr
                  key={`${rowKey}-${idx}`}
                  className={`cursor-pointer odd:bg-slate-50 hover:bg-slate-100 ${isSelected ? "bg-blue-50" : ""}`}
                  onClick={() => onRowSelect(row)}
                >
                  {orderedColumns.map((column) => (
                    <td key={`${idx}-${column}`} className="border-b border-slate-200 px-3 py-2 text-slate-900">
                      {String(row[column] ?? "")}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
};
