def apply_filters(rows: list[dict], filters: dict[str, str], global_query: str | None = None) -> list[dict]:
    def matches_row(row: dict) -> bool:
        for key, value in filters.items():
            if value is None or value == "":
                continue
            row_value = str(row.get(key, ""))
            if value.lower() not in row_value.lower():
                return False

        if global_query:
            gq = global_query.lower()
            haystack = " ".join(str(v) for v in row.values()).lower()
            if gq not in haystack:
                return False

        return True

    return [row for row in rows if matches_row(row)]
