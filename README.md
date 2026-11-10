# Mini ETL Pipeline — Sales Data Quality & Warehouse Load

A portfolio-ready Python ETL project that extracts sales CSV data, validates and transforms records with pandas, and loads clean records into a relational database using SQLAlchemy. Invalid rows are written to a reject file; each run produces structured logs and a run summary.

## Architecture

```text
data/raw/sales.csv
      |
      v
 Extract (pandas)
      |
      v
 Validate + Transform -----> data/rejected/rejected_<run_id>.csv
      |
      v
 Load (SQLAlchemy transaction)
      |
      v
 SQLite (default) / PostgreSQL (optional)
      |
      v
 logs/etl.log + run summary
```

## Features

- Modular extract, transform, and load stages
- Required-column and row-level data-quality checks
- Type conversion, whitespace cleanup, email normalization, and duplicate removal
- Invalid records quarantined with a rejection reason
- Transactional, idempotent batch load (reprocessing an order_id replaces its prior row) with rollback on failure
- Python logging to console and rotating log file
- Configurable source, target table, and database URL
- Unit tests using temporary SQLite databases
- GitHub Actions CI workflow

## Quick start

Requires Python 3.10+.

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
python -m src.main --input data/raw/sales.csv
```

The default target is `sqlite:///warehouse.db`. The pipeline creates the `fact_sales` table automatically.

## Sample output

```text
ETL run completed | extracted=8 | loaded=6 | rejected=1 | duplicates=1
```

Counts depend on the supplied sample file and any changes you make.

## Optional PostgreSQL target

Install PostgreSQL and create a database, then set `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql+psycopg2://etl_user:your_password@localhost:5432/etl_warehouse
```

Install the PostgreSQL driver:

```bash
pip install psycopg2-binary
```

Do not commit `.env`, passwords, or production data. `.env` is ignored by Git.

## Run tests

```bash
pytest -v
```

## Run with another CSV

```bash
python -m src.main --input /absolute/path/to/sales.csv
```

Expected columns:

| Column | Rule |
|---|---|
| order_id | Required, non-empty, unique |
| order_date | Valid date, normalized to YYYY-MM-DD |
| customer_id | Required, non-empty |
| customer_email | Valid email format |
| product | Required, non-empty |
| quantity | Positive integer |
| unit_price | Non-negative decimal |

Rows with validation failures are quarantined rather than loaded.

## Database checks

For SQLite:

```bash
sqlite3 warehouse.db "SELECT COUNT(*) FROM fact_sales;"
sqlite3 warehouse.db "SELECT * FROM fact_sales LIMIT 10;"
```

For PostgreSQL:

```sql
SELECT COUNT(*) FROM fact_sales;
SELECT product, SUM(quantity * unit_price) AS revenue
FROM fact_sales
GROUP BY product
ORDER BY revenue DESC;
```

## Suggested interview walkthrough

1. **Business problem:** ingest inconsistent sales extracts into an analytics-ready fact table.
2. **Extract:** pandas reads the source CSV and checks the input schema.
3. **Transform:** normalize strings and dates, cast numeric fields, validate business rules, and deduplicate by `order_id`.
4. **Reject handling:** preserve bad rows with explicit reasons for remediation.
5. **Load:** use SQLAlchemy and a transaction so a failed load does not leave a partial batch.
6. **Observability:** log run ID, stage, row counts, and exceptions without logging sensitive row contents.
7. **Testing:** use isolated temporary SQLite databases to verify transformations and persistence.

## Repository structure

```text
mini-etl-pipeline/
├── .github/workflows/tests.yml
├── data/raw/sales.csv
├── logs/.gitkeep
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_transform.py
│   └── test_load.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Resume bullet

**Mini ETL Pipeline | Python, Pandas, SQLAlchemy, SQLite, PostgreSQL, Pytest, GitHub Actions**
- Developed a modular ETL pipeline to ingest sales CSV files, enforce schema and business-rule validations, standardize records, and load curated data into a relational warehouse.
- Implemented duplicate handling, rejected-record quarantine, transactional loading, structured logging, and automated unit tests.
- Added CI workflow with GitHub Actions to execute the test suite on every push and pull request.

> Be prepared to explain the design and run the project live. Do not claim production deployment or PostgreSQL execution unless you have actually configured and tested those environments.
