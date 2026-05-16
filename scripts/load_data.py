from sqlalchemy import create_engine
import pandas as pd
import json
import glob
import os


def read_csv_files(data_path="./data"):
    """Read all CSV files from a directory and return a single concatenated DataFrame.

    Args:
        data_path (str): Path to the directory containing CSV files. Defaults to './data'.

    Returns:
        pandas.DataFrame: Concatenated DataFrame containing rows from all CSV files.

    Notes:
        - Files are read in chunks (chunksize=10000) to avoid high memory usage.
        - If no CSV files are found, an empty DataFrame is returned.
    """
    files = glob.glob(os.path.join(data_path, "*.csv"))
    if not files:
        # return empty DataFrame with no rows if there are no CSV files
        return pd.DataFrame()

    all_csv = []
    for file in files:
        # read large CSVs in chunks to reduce memory footprint
        df_reader = pd.read_csv(file, iterator=True, chunksize=10000)
        for df in df_reader:
            all_csv.append(df)
    data = pd.concat(all_csv, ignore_index=True)
    return data


def read_json_files(data_path="./data"):
    """Read all JSON files from a directory and return a concatenated DataFrame.

    Args:
        data_path (str): Path to the directory containing JSON files. Defaults to './data'.

    Returns:
        pandas.DataFrame: Concatenated DataFrame containing rows from all JSON files.

    Notes:
        - Each JSON file is loaded and converted to a DataFrame.
        - If no JSON files are present, an empty DataFrame is returned.
    """
    files = glob.glob(os.path.join(data_path, "*.json"))
    if not files:
        return pd.DataFrame()

    all_json = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        all_json.append(df)
    all_json_data = pd.concat(all_json, ignore_index=True)
    return all_json_data


def concat_all_data(csv_data, json_data):
    """Concatenate CSV and JSON DataFrames into a single DataFrame.

    Args:
        csv_data (pandas.DataFrame): Data loaded from CSV files.
        json_data (pandas.DataFrame): Data loaded from JSON files.

    Returns:
        pandas.DataFrame: Combined DataFrame containing rows from both sources.
    """
    # Combine the CSV and JSON data into one unified DataFrame
    df = pd.concat([csv_data, json_data], ignore_index=True)
    return df


def data_transformation(all_data):
    # Make a copy of the data to avoid mutating the original DataFrame
    new_data = all_data.copy()

    # Convert order_date to datetime for consistent date handling
    new_data['order_date'] = pd.to_datetime(new_data['order_date'])

    # Ensure numeric columns have the correct data types
    new_data['price'] = new_data['price'].astype(float)
    new_data['quantity'] = new_data['quantity'].astype(int)
    new_data['total_amount'] = new_data['total_amount'].astype(float)
    new_data['discount'] = new_data['discount'].astype(float)

    # Convert is_weekend to boolean for logical filtering and analysis
    new_data['is_weekend'] = new_data['is_weekend'].astype(bool)

    return new_data


def load_data(all_data):
    # Create a SQLAlchemy engine for the target Postgres data warehouse
    engin = create_engine(
        "postgresql://postgres:postgres@localhost:5432/restaurant_dw")

    try:
        # Read existing order IDs from the raw.orders table to avoid duplicates
        existing_ids = pd.read_sql("SELECT order_id FROM raw.orders", con=engin)[
            'order_id'].tolist()

        # Filter incoming data to only include new records not already in the DB
        new_data = all_data[~all_data['order_id'].isin(existing_ids)]

        # If there are no new rows, exit early
        if len(new_data) == 0:
            print("No new data to load.")
            return

        # Append new rows to the existing table in batches to improve performance
        new_data.to_sql(
            name='orders',
            con=engin,
            schema='raw',
            if_exists='append',
            chunksize=100000,
            method='multi',
            index=False
        )
        print(f"Loaded {len(new_data)} new records into the database.")
    except Exception:
        # If reading existing IDs or appending fails (e.g., table doesn't exist),
        # create/replace the table with the full dataset
        all_data.to_sql(
            name="orders",
            con=engin,
            schema="raw",
            if_exists="replace",
            chunksize=100000,
            method='multi',
            index=False
        )
        print(f"Created table and loaded {len(all_data)} rows.")


if __name__ == "__main__":
    # Define the directory where CSV and JSON files are stored.
    data_path = "./data"

    # Load raw data from CSV files in the data directory.
    csv_data = read_csv_files(data_path)

    # Load raw data from JSON files in the data directory.
    json_data = read_json_files(data_path)

    # Combine data from both sources into a single DataFrame.
    all_data = concat_all_data(csv_data, json_data)

    # Apply transformations to normalize data types and formats.
    updated_data = data_transformation(all_data)

    # Load the transformed data into the Postgres data warehouse.
    load_data(updated_data)
