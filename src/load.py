from sqlalchemy import create_engine, text, MetaData, Table, delete, inspect
from sqlalchemy.engine import Engine
import pandas as pd

def create_db_engine(database_url: str) -> Engine:
    kwargs = {"future": True}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(database_url, **kwargs)

def load_sales(clean: pd.DataFrame, engine: Engine, table_name: str = "fact_sales") -> int:
    """Load a batch atomically; SQLAlchemy rolls back the transaction on error."""
    if not table_name.replace("_", "").isalnum():
        raise ValueError("Invalid table name")
    if clean.empty:
        return 0
    with engine.begin() as connection:
        if inspect(connection).has_table(table_name):
            target = Table(table_name, MetaData(), autoload_with=connection)
            order_ids = clean["order_id"].dropna().astype(str).tolist()
            if order_ids:
                connection.execute(delete(target).where(target.c.order_id.in_(order_ids)))
            clean.to_sql(table_name, con=connection, if_exists="append", index=False, method="multi")
        else:
            clean.to_sql(table_name, con=connection, if_exists="fail", index=False, method="multi")
    return len(clean)

def count_rows(engine: Engine, table_name: str = "fact_sales") -> int:
    if not table_name.replace("_", "").isalnum():
        raise ValueError("Invalid table name")
    with engine.connect() as connection:
        exists = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name")
            if engine.dialect.name == "sqlite"
            else text("SELECT table_name FROM information_schema.tables WHERE table_name=:name"),
            {"name": table_name},
        ).scalar()
        if not exists:
            return 0
        return int(connection.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar_one())
