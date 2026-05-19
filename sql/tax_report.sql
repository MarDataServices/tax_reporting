WITH trades AS (
    SELECT
        t."Instrument" as instrument,
        DATE(t."Date") as trade_date,
        t."Cash Flow" * p.price AS value_sek
    FROM trades_eth t
    JOIN prices_eth p
      ON DATE(t."Date") = p.date
    WHERE t."Type" = 'trade'
      AND p.date < '2025-06-01'
)

SELECT
    instrument,
    trade_date,
    SUM(CASE WHEN value_sek > 0 THEN value_sek ELSE 0 END) AS proceeds_sek,
    SUM(CASE WHEN value_sek < 0 THEN -value_sek ELSE 0 END) AS cost_basis_sek,
    SUM(value_sek) AS pnl_sek
FROM trades
GROUP BY instrument, trade_date;