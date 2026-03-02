from app.services.filtering import apply_filters


ROWS = [
    {"bin": "STORAGE", "movement_type": "RECEIVED", "item": "A"},
    {"bin": "FLOOR", "movement_type": "SHIPPED", "item": "B"},
]


def test_apply_filters_column_contains():
    out = apply_filters(ROWS, filters={"bin": "stor"})
    assert len(out) == 1
    assert out[0]["item"] == "A"


def test_apply_filters_global_query():
    out = apply_filters(ROWS, filters={}, global_query="shipped")
    assert len(out) == 1
    assert out[0]["bin"] == "FLOOR"
