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


def test_apply_filters_multi_value_or_within_field():
    out = apply_filters(ROWS, filters={"movement_type": ["received", "transfer"]})
    assert len(out) == 1
    assert out[0]["item"] == "A"


def test_apply_filters_and_across_fields():
    out = apply_filters(
        ROWS,
        filters={
            "movement_type": ["received", "shipped"],
            "bin": ["stor"],
        },
    )
    assert len(out) == 1
    assert out[0]["item"] == "A"
