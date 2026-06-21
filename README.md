# Crypto Tax Reporting Pipeline

A containerized data engineering pipeline for transforming raw crypto options trade data into tax reporting data denominated in SEK for Swedish K4 reporting.


## Features
The pipeline:
- extracts historical ETH and USDC trade data
- fetches historical SEK conversion rates from CoinGecko.
- stores raw and processed data
- loads normalized datasets into PostgreSQL
- performs SQL-based tax calculations and PnL aggregation


## Stack
Built using Python, pandas, PostgreSQL, Docker, and SQLAlchemy. Data from CoinGecko API.


## Setup
1. Configure environment variables 
Create a .env file from .env.example:
```bash
cp .env.example .env
```

Assign a password for PostgreSQL in .env:

```
POSTGRES_PASSWORD=your_password
```

2. Start your docker services.
```bash
docker compose up --build

```
This will:
- Start a PostgreSQL container
- Initialize the tax_reporting database
- Run the ETL pipeline, ingesting and transforming trade data

3. Query the data in the PostgreSQL database
```
docker exec -it tax_postgres psql -U postgres -d tax_reporting

# QUERY DB
# Example query(same as in tax_report.sql)
WITH trades AS (
    SELECT
        t."Instrument",
        DATE(t."Date") as trade_date,
        t."Change" * p.price AS value_sek
    FROM "trades_eth" t
    JOIN "prices_eth" p
      ON DATE(t."Date") = p.date::date
    WHERE t."Type" = 'trade'
      AND p.date::date < '2025-06-01'
)

SELECT
    "Instrument",
    MAX(trade_date) AS close_date,
    SUM(CASE WHEN value_sek > 0 THEN value_sek ELSE 0 END) AS proceeds_sek,
    SUM(CASE WHEN value_sek < 0 THEN -value_sek ELSE 0 END) AS cost_basis_sek,
    SUM(value_sek) AS pnl_sek
FROM trades
GROUP BY "Instrument";
```

## Future Development

Potential future improvements include:

- Airflow-based orchestration and scheduling
- Automated K4 export generation
- Azure Blob Storage and Azure SQL Database integration
- dbt-based SQL transformations
- Automated tax reporting pipelines