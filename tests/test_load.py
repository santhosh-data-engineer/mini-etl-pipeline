import pandas as pd
from src.load import create_db_engine, load_sales, count_rows

def test_loads_records_to_sqlite():
    engine = create_db_engine("sqlite:///:memory:")
    frame = pd.DataFrame([{
        "order_id":"S100","order_date":"2026-10-10","customer_id":"C10",
        "customer_email":"test@example.com","product":"Dock","quantity":1,"unit_price":2000.0
    }])
    try:
        assert load_sales(frame, engine) == 1
        assert count_rows(engine) == 1
    finally:
        engine.dispose()

def test_empty_batch_does_not_create_table():
    engine = create_db_engine("sqlite:///:memory:")
    try:
        assert load_sales(pd.DataFrame(), engine) == 0
        assert count_rows(engine) == 0
    finally:
        engine.dispose()


def test_reloading_same_order_is_idempotent():
    engine = create_db_engine("sqlite:///:memory:")
    frame = pd.DataFrame([{
        "order_id":"S200","order_date":"2026-10-10","customer_id":"C20",
        "customer_email":"same@example.com","product":"Keyboard","quantity":1,"unit_price":1000.0
    }])
    try:
        load_sales(frame, engine)
        load_sales(frame, engine)
        assert count_rows(engine) == 1
    finally:
        engine.dispose()
