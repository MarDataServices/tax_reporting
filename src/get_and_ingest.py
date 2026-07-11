import requests
from datetime import datetime, timezone 
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import logging
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR.parent / "output"
DATA_DIR = BASE_DIR.parent / "data"

password = os.getenv("POSTGRES_PASSWORD")

#Local no-container deployment, might want to change port to 5432
#engine = create_engine(f"postgresql://postgres:{password}@localhost:5433/tax_reporting")

#For containerized deployment
engine = create_engine(
    f"postgresql://postgres:{password}@postgres:5432/tax_reporting"
)

logging.basicConfig(level=logging.INFO)

def to_unix(date_str):
    return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())

def ts_to_date(ts_ms):
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).date()

def parse_prices(data, coin):
    rows = []
    
    for ts, price in data["prices"]:
        rows.append({
            "coin": coin,
            "date": str(ts_to_date(ts)),
            "price": price
        })
    
    return rows

def fetch_prices(coin_id, start_date, end_date):
    #Get coingecko crypto exhange rates
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
    
    #From date "from" to date "to", comparing the coin with "vs_currency"
    #As I did my tax reporting in Sweden, I used SEK.
    params = {
        "vs_currency": "sek",
        "from": to_unix(start_date),
        "to": to_unix(end_date)
    }
    
    #Try to get a response using the set url and parameters
    try:
        response = requests.get(url, params=params, timeout=30)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        raise

def load_to_db(df, table_name):
    df = df.drop_duplicates()
    df.to_sql(table_name, engine, if_exists="append", index=False)

def extract_eth_trade_data(date1: str, date2: str) -> tuple:
    logging.info("Fetching eth price data...")

    json_path = OUTPUT_DIR / "eth_sek.json"

    #If json file with price data already exists, only add new data
    if json_path.exists():
        existing_df = pd.read_json(json_path)
        latest_date = (
            pd.to_datetime(existing_df["date"]).max()
            + pd.Timedelta(days=1)
        ).strftime("%Y-%m-%d")
    else:
        existing_df = pd.DataFrame()
        latest_date = date1

    data = fetch_prices("ethereum", latest_date, date2)
    structured_data = parse_prices(data, "ETH")
    prices_df = pd.DataFrame(structured_data)
    if not prices_df.empty:
        prices_df["date"] = pd.to_datetime(
            prices_df["date"]
        ).dt.date
    
    combined_df = pd.concat([existing_df, prices_df])

    combined_df = combined_df.drop_duplicates(
        subset=["date"],
        keep="last"
    )

    combined_df["date"] = combined_df["date"].astype(str)

    combined_df.to_json(
        json_path,
        orient="records",
        indent=2
    )


    file_df = pd.read_excel(f"{DATA_DIR}/eth-deribit.xlsx")
    file_df["date"] = pd.to_datetime(file_df["Date"]).dt.date
    file_df.columns = file_df.columns.str.strip()

    return file_df, combined_df

def extract_usdc_trade_data(date1:str, date2:str) -> tuple:
    logging.info("Fetching usdc price data...")

    json_path = OUTPUT_DIR / "usdc_sek.json"

    #If json file with price data already exists, only add new data
    if json_path.exists():
        existing_df = pd.read_json(json_path)
        latest_date = (
            pd.to_datetime(existing_df["date"]).max()
            + pd.Timedelta(days=1)
        ).strftime("%Y-%m-%d")
    else:
        existing_df = pd.DataFrame()
        latest_date = date1

    data = fetch_prices("usd-coin", latest_date, date2)
    structured_data = parse_prices(data, "usdc")
    prices_df = pd.DataFrame(structured_data)
    if not prices_df.empty:
        prices_df["date"] = pd.to_datetime(
            prices_df["date"]
        ).dt.date


    combined_df = pd.concat([existing_df, prices_df])

    combined_df = combined_df.drop_duplicates(
        subset=["date"],
        keep="last"
    )

    combined_df["date"] = combined_df["date"].astype(str)

    combined_df.to_json(
        json_path,
        orient="records",
        indent=2
    )

    file_df = pd.read_excel(f"{DATA_DIR}/usdc-deribit.xlsx")
    file_df["date"] = pd.to_datetime(file_df["Date"]).dt.date
    file_df.columns = file_df.columns.str.strip()

    return file_df, combined_df