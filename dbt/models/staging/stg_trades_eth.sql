SELECT
    "ID" AS trade_id,
    DATE("date") AS trade_date,
    "Instrument" AS instrument,
    "Type" AS trade_type,
    "Change" AS change_eth
FROM {{ SOURCE('tax_reporting', 'trades_eth') }}