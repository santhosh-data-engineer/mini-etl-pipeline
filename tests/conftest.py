import pandas as pd
import pytest

@pytest.fixture
def sample_sales():
    return pd.DataFrame([
        {"order_id":"S001","order_date":"2026-10-01","customer_id":"C01","customer_email":" ALICE@example.com ","product":" Keyboard ","quantity":"2","unit_price":"1500.50"},
        {"order_id":"S002","order_date":"2026-10-02","customer_id":"C02","customer_email":"bob@example.com","product":"Mouse","quantity":"1","unit_price":"500"},
        {"order_id":"S003","order_date":"bad-date","customer_id":"C03","customer_email":"bad-email","product":"Monitor","quantity":"0","unit_price":"-10"},
        {"order_id":"S002","order_date":"2026-10-02","customer_id":"C02","customer_email":"bob@example.com","product":"Mouse","quantity":"1","unit_price":"500"},
    ])
