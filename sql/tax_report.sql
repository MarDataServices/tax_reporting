WITH eth_trades AS (
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
FROM eth_trades
GROUP BY "Instrument";

WITH usdc_trades AS (
    SELECT
        t."Instrument",
        DATE(t."Date") as trade_date,
        t."Change" * p.price AS value_sek
    FROM "trades_usdc" t
    JOIN "prices_usdc" p
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
FROM usdc_trades
GROUP BY "Instrument";