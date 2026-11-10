from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {
    "order_id", "order_date", "customer_id", "customer_email",
    "product", "quantity", "unit_price",
}

def extract_csv(path: str | Path) -> pd.DataFrame:
    """Read a CSV and fail fast if its required schema is missing."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Input CSV not found: {source}")
    frame = pd.read_csv(source, dtype={"order_id": "string", "customer_id": "string"})
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Input schema is missing required columns: {sorted(missing)}")
    return frame
