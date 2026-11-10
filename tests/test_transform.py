from src.transform import transform_sales

def test_transform_validates_normalizes_and_deduplicates(sample_sales):
    clean, rejected, duplicates = transform_sales(sample_sales)
    assert len(clean) == 2
    assert len(rejected) == 1
    assert duplicates == 1
    assert clean.loc[0, "customer_email"] == "alice@example.com"
    assert clean.loc[0, "product"] == "Keyboard"
    assert clean.loc[0, "quantity"] == 2

def test_reject_reason_is_actionable(sample_sales):
    _, rejected, _ = transform_sales(sample_sales)
    reason = rejected.iloc[0]["rejection_reason"]
    assert "invalid order_date" in reason
    assert "invalid customer_email" in reason
    assert "quantity must be a positive integer" in reason
    assert "unit_price must be non-negative" in reason
