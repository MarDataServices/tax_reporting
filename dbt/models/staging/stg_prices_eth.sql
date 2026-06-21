SELECT
    date::DATE AS price_date,
    price AS eth_sek_price
FROM {{ SOURCE('tax_reporting', 'prices_eth') }}