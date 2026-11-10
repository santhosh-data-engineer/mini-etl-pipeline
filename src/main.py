import argparse
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from pathlib import Path

from src.config import DATABASE_URL, LOG_DIR, LOG_LEVEL, REJECT_DIR
from src.extract import extract_csv
from src.transform import transform_sales
from src.load import create_db_engine, load_sales

def configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    root = logging.getLogger()
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    root.handlers.clear()
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    file_handler = RotatingFileHandler(LOG_DIR / "etl.log", maxBytes=1_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    root.addHandler(console)
    root.addHandler(file_handler)

def run_pipeline(input_path: str, database_url: str = DATABASE_URL) -> dict[str, int | str]:
    logger = logging.getLogger("etl")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logger.info("run_id=%s stage=extract started input=%s", run_id, input_path)
    raw = extract_csv(input_path)
    logger.info("run_id=%s stage=extract completed rows=%d", run_id, len(raw))

    clean, rejected, duplicates = transform_sales(raw)
    logger.info(
        "run_id=%s stage=transform completed clean=%d rejected=%d duplicates=%d",
        run_id, len(clean), len(rejected), duplicates
    )

    if not rejected.empty:
        REJECT_DIR.mkdir(parents=True, exist_ok=True)
        reject_path = REJECT_DIR / f"rejected_{run_id}.csv"
        rejected.to_csv(reject_path, index=False)
        logger.warning("run_id=%s rejected_file=%s", run_id, reject_path)

    engine = create_db_engine(database_url)
    try:
        loaded = load_sales(clean, engine)
    finally:
        engine.dispose()

    summary = {
        "run_id": run_id,
        "extracted": len(raw),
        "loaded": loaded,
        "rejected": len(rejected),
        "duplicates": duplicates,
    }
    logger.info("run_id=%s stage=load completed loaded=%d", run_id, loaded)
    logger.info("ETL run completed | extracted=%d | loaded=%d | rejected=%d | duplicates=%d",
                len(raw), loaded, len(rejected), duplicates)
    return summary

def main() -> None:
    parser = argparse.ArgumentParser(description="Run the sales CSV ETL pipeline.")
    parser.add_argument("--input", default="data/raw/sales.csv", help="Path to source CSV")
    parser.add_argument("--database-url", default=DATABASE_URL, help="SQLAlchemy database URL")
    args = parser.parse_args()
    configure_logging()
    try:
        run_pipeline(args.input, args.database_url)
    except Exception:
        logging.getLogger("etl").exception("ETL run failed")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
