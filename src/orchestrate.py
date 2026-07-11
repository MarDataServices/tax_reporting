from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from dbt_run import run_dbt
from get_and_ingest import (
    extract_eth_trade_data,
    extract_usdc_trade_data,
    load_to_db
)

START_DATE = "2025-03-05"
END_DATE = datetime.today().strftime("%Y-%m-%d")


def load_eth():
    trades_df, prices_df = extract_eth_trade_data(
        START_DATE,
        END_DATE
    )

    load_to_db(trades_df, "trades_eth")
    load_to_db(prices_df, "prices_eth")


def load_usdc():
    trades_df, prices_df = extract_usdc_trade_data(
        START_DATE,
        END_DATE
    )

    load_to_db(trades_df, "trades_usdc")
    load_to_db(prices_df, "prices_usdc")


with DAG(
    dag_id="crypto_tax_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["crypto", "etl"],
) as dag:

    load_eth_task = PythonOperator(
        task_id="load_eth_data",
        python_callable=load_eth,
    )

    load_usdc_task = PythonOperator(
        task_id="load_usdc_data",
        python_callable=load_usdc,
    )
    
    dbt_models = PythonOperator(
        task_id="dbt_models",
        python_callable=run_dbt,
    )

    (
        [load_eth_task, load_usdc_task] >> dbt_models
    )