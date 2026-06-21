SELECT
    t.instrument,
    t.trade_date,
    t.trade_type,
    t.change_eth,
    p.eth_sek_price
    
    t.change_eth * p.eth_sek_price AS value_sek

FROM {{ REF('stg_trades_eth') }} t
JOIN {{ REF('stg_prices_eth') }} p
    ON t.trade_date = p.price_date