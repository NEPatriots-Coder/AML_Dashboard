def _normalize_filter_values(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item.strip() for item in value if item and item.strip()]
    if value.strip():
        return [value.strip()]
    return []


def apply_filters(
    rows: list[dict], filters: dict[str, str | list[str]], global_query: str | None = None
) -> list[dict]:
    def matches_row(row: dict) -> bool:
        for key, raw_value in filters.items():
            values = _normalize_filter_values(raw_value)
            if not values:
                continue
            row_value = str(row.get(key, ""))
            row_value_lower = row_value.lower()
            if not any(value.lower() in row_value_lower for value in values):
                return False

        if global_query:
            gq = global_query.lower()
            haystack = " ".join(str(v) for v in row.values()).lower()
            if gq not in haystack:
                return False

        return True

    return [row for row in rows if matches_row(row)]
