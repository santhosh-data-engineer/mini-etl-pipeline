import re
import pandas as pd

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def transform_sales(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """
    Normalize and validate sales records.
    Returns (clean_records, rejected_records, duplicate_count).
    """
    df = raw.copy()
    df.columns = [str(column).strip().lower() for column in df.columns]
    for col in ("order_id", "customer_id", "customer_email", "product"):
        df[col] = df[col].astype("string").str.strip()

    df["customer_email"] = df["customer_email"].str.lower()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    reasons: list[list[str]] = [[] for _ in range(len(df))]
    checks = {
        "order_id is required": df["order_id"].isna() | df["order_id"].eq(""),
        "customer_id is required": df["customer_id"].isna() | df["customer_id"].eq(""),
        "product is required": df["product"].isna() | df["product"].eq(""),
        "invalid order_date": df["order_date"].isna(),
        "invalid customer_email": ~df["customer_email"].fillna("").map(lambda value: bool(EMAIL_PATTERN.match(value))),
        "quantity must be a positive integer": df["quantity"].isna() | (df["quantity"] <= 0) | (df["quantity"] % 1 != 0),
        "unit_price must be non-negative": df["unit_price"].isna() | (df["unit_price"] < 0),
    }
    for reason, mask in checks.items():
        for position in range(len(df)):
            if bool(mask.iloc[position]):
                reasons[position].append(reason)

    df["rejection_reason"] = ["; ".join(items) for items in reasons]
    rejected = df[df["rejection_reason"].ne("")].copy()
    candidates = df[df["rejection_reason"].eq("")].drop(columns=["rejection_reason"]).copy()

    before = len(candidates)
    candidates = candidates.drop_duplicates(subset=["order_id"], keep="last")
    duplicate_count = before - len(candidates)

    candidates["quantity"] = candidates["quantity"].astype("int64")
    candidates["unit_price"] = candidates["unit_price"].astype(float)
    return candidates.reset_index(drop=True), rejected.reset_index(drop=True), duplicate_count
