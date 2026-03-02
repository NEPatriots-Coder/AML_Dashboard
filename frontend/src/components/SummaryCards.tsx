import type { FC } from "react";
import type { AssetRow } from "../lib/types";

interface SummaryCardsProps {
  rows: AssetRow[];
}

function countBy(rows: AssetRow[], key: string): number {
  const values = new Set(
    rows
      .map((row) => String(row[key] ?? "").trim())
      .filter((value) => value.length > 0),
  );
  return values.size;
}

export const SummaryCards: FC<SummaryCardsProps> = ({ rows }) => {
  const storageCount = rows.filter((row) =>
    String(row.bin ?? "")
      .toLowerCase()
      .includes("storage"),
  ).length;

  const cards = [
    { label: "Visible Rows", value: rows.length, tone: "text-slate-900" },
    { label: "Unique Asset Types", value: countBy(rows, "asset_type"), tone: "text-slate-900" },
    { label: "Unique Items", value: countBy(rows, "item"), tone: "text-slate-900" },
    { label: "Rows in STORAGE", value: storageCount, tone: "text-slate-900" },
  ];

  return (
    <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <article
          key={card.label}
          className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
        >
          <p className="text-xs font-medium uppercase tracking-wide text-slate-600">{card.label}</p>
          <p className={`mt-2 text-3xl font-semibold ${card.tone}`}>{card.value}</p>
        </article>
      ))}
    </section>
  );
};
