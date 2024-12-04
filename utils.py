import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import streamlit as st
import io, os

# Constant unit
gallon = 3.785411784
feet_squared = 0.09290304

# Function to read files dynamically based on file type
def read_file(file):
    """
    Reads a file and returns a pandas DataFrame.
    Supports CSV and Excel (.xlsx) files.

    Args:
        file (file-like object): The uploaded file.

    Returns:
        pd.DataFrame: DataFrame containing the file's data.

    Raises:
        ValueError: If the file extension is not supported.
    """
    try:
        # Check the file extension
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        elif file.name.endswith(".xls") or file.name.endswith(".xlsx"):
            return pd.read_excel(file)
        else:
            raise ValueError(f"Unsupported file type: {file.name}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the file: {e}")

# Function to process data
def process_data(file, selected_datetime_str, adjusted_datetime, exclude_values=None):
    """
    Process data from an Excel file for the selected datetime.

    Parameters:
        file (file-like object): The uploaded Excel file containing the data.
        selected_datetime_str (str): The selected datetime in the format "YYYY-MM-DD HH:MM:SS".
        adjusted_datetime (datetime.datetime): The adjusted datetime to be used for updates.

    Returns:
        pandas.DataFrame: Processed DataFrame with cleaned and transformed data.

    Notes:
        This function performs the following steps:
        1. Reads data from the Excel file, dropping unnecessary columns.
        2. Filters and sorts the DataFrame based on the selected datetime.
        3. Reorders columns in the desired order.
        4. Updates specified columns with the adjusted_datetime.
        5. Cleans and transforms data, handling commas and percentage values.
        6. Returns the processed DataFrame.

    Example:
        df_processed = process_data(uploaded_file, "2023-08-25 14:00:00", datetime.now())
    """
    df = read_file(file)

    # Drop unnecessary columns
    drop_columns = ['Total time', 'Task status', 'Plan running time (s)', 'Uncleaned area (㎡)', 'Task start mode', 'Remarks']
    df.drop(columns=drop_columns, inplace=True)
    df.insert(0, 'Id', np.nan)
    
    selected_datetime = datetime.strptime(selected_datetime_str, "%Y-%m-%d %H:%M:%S")

    # Filter and sort DataFrame
    df['Receive task report time'] = pd.to_datetime(df['Receive task report time'])
    df_filtered = df[df['Receive task report time'] > selected_datetime]

    # Exclude values from 'S/N' if exclude_values is provided
    if exclude_values:
        df_filtered = df_filtered[~df_filtered['S/N'].isin(exclude_values)]

    df_filtered = df_filtered.sort_values(by='Receive task report time', ascending=False)
    df_filtered.reset_index(drop=True, inplace=True)

    # Create column order
    column_order = ['Id', 'Robot name', 'S/N', 'Map name', 'Cleaning plan', 'User',
        'Task start time', 'End time', 'Task completion (%)',
        'Actual cleaning area(㎡)', 'Total time (h)', 'Water usage (L)',
        'Brush (%)', 'Filter (%)', 'Squeegee(%)',
        'Planned crystallization area (㎡)', 'Actual crystallization area (㎡)',
        'Cleaning plan area (㎡)', 'Start battery level (%)',
        'End battery level (%)', 'Receive task report time', 'Task type',
        'Download link', 'Work efficiency (㎡/h)']
    df_reorder = df_filtered[column_order]
    
    df_test = df_reorder.copy()

    # Update columns with adjusted_datetime 
    columns_to_update = ['Planned crystallization area (㎡)', 'Actual crystallization area (㎡)']
    df_test.loc[:, columns_to_update] = adjusted_datetime

    df_replaced = df_test.applymap(lambda cell: 0 if cell == '-' else cell)
    df_replaced = df_replaced.fillna("NULL")

    # Remove commas and replace values in specified columns
    columns_with_comma = ['Work efficiency (㎡/h)', 'Actual cleaning area(㎡)', 'Cleaning plan area (㎡)']
    columns_with_pct = ['Brush (%)', 'Filter (%)', 'Squeegee(%)']

    print(df_replaced[columns_with_comma])
    print(df_replaced[columns_with_comma].dtypes)

    # For loop to handle multiple dtypes
    for column in columns_with_comma:
        if df_replaced[column].dtype in ['object', 'float64']:
            df_replaced[column] = df_replaced[column].astype(str).str.replace(',', '')
            df_replaced[column] = df_replaced[column].replace('0.00', '0')

    df_replaced[columns_with_pct] = df_replaced[columns_with_pct].replace('100.00', '100')

    return df_replaced

def process_ca_data(file, selected_datetime_str, adjusted_datetime, exclude_values=None):
    """
    Process data from an Excel file (Canada data) for the selected datetime.

    Parameters:
        file (file-like object): The uploaded Excel file containing the data.
        selected_datetime_str (str): The selected datetime in the format "YYYY-MM-DD HH:MM:SS".
        adjusted_datetime (datetime.datetime): The adjusted datetime to be used for updates.

    Returns:
        pandas.DataFrame: Processed DataFrame with cleaned and transformed data.

    Notes:
        This function performs the following steps:
        1. Reads data from the Excel file, dropping unnecessary columns.
        2. Filters and sorts the DataFrame based on the selected datetime.
        3. Reorders columns in the desired order.
        4. Updates specified columns with the adjusted_datetime.
        5. Cleans and transforms data, handling commas and percentage values.
        6. Returns the processed DataFrame.

    Example:
        df_processed = process_ca_data(uploaded_file, "2023-08-25 14:00:00", datetime.now())
    """
    df = read_file(file)

    # Drop unnecessary columns
    drop_columns = ['Total time', 'Task status', 'Plan running time (s)', 'Uncleaned area (ft²)', 'Task start mode', 'Remarks']
    df.drop(columns=drop_columns, inplace=True)
    df.insert(0, 'Id', np.nan)
    
    selected_datetime = datetime.strptime(selected_datetime_str, "%Y-%m-%d %H:%M:%S")

    # Filter and sort DataFrame
    df['Receive task report time'] = pd.to_datetime(df['Receive task report time'])
    df_filtered = df[df['Receive task report time'] > selected_datetime]
    
    # Exclude values from 'S/N' if exclude_values is provided
    if exclude_values:
        df_filtered = df_filtered[~df_filtered['S/N'].isin(exclude_values)]

    df_filtered = df_filtered.sort_values(by='Receive task report time', ascending=False)
    df_filtered.reset_index(drop=True, inplace=True)

    # Create column order
    column_order = ['Id', 'Robot name', 'S/N', 'Map name', 'Cleaning plan', 'User',
        'Task start time', 'End time', 'Task completion (%)',
        'Actual cleaning area(ft²)', 'Total time (h)', 'Water usage (gal)',
        'Brush (%)', 'Filter (%)', 'Squeegee(%)',
        'Planned crystallization area (ft²)', 'Actual crystallization area (ft²)',
        'Cleaning plan area (ft²)', 'Start battery level (%)',
        'End battery level (%)', 'Receive task report time', 'Task type',
        'Download link', 'Work efficiency (ft²/h)']
    df_reorder = df_filtered[column_order]

    df_test = df_reorder.copy()

    # Update columns with adjusted_datetime
    columns_to_update = ['Planned crystallization area (ft²)', 'Actual crystallization area (ft²)']
    df_test.loc[:, columns_to_update] = adjusted_datetime

    df_replaced = df_test.applymap(lambda cell: 0 if cell == '-' else cell)
    df_replaced = df_replaced.fillna("NULL")


    columns_with_comma = ['Work efficiency (ft²/h)', 'Actual cleaning area(ft²)', 'Cleaning plan area (ft²)']
    columns_with_pct = ['Brush (%)', 'Filter (%)', 'Squeegee(%)']
    df_replaced[columns_with_comma] = df_replaced[columns_with_comma].apply(lambda x: x.str.replace(',', ''))

    # Convert gallon and feet_squared to appropriate values
    df_replaced['Water usage (gal)'] = df_replaced['Water usage (gal)'] * gallon
    df_replaced[columns_with_comma] = df_replaced[columns_with_comma].apply(pd.to_numeric) * feet_squared
    df_replaced[columns_with_comma] = df_replaced[columns_with_comma].applymap(lambda x: str(x).replace(',', ''))
    df_replaced[columns_with_comma] = df_replaced[columns_with_comma].apply(pd.to_numeric).round(4)
    df_replaced['Water usage (gal)'] = df_replaced['Water usage (gal)'].apply(pd.to_numeric).round(4)

    df_replaced[columns_with_comma] = df_replaced[columns_with_comma].replace('0.0', '0')
    df_replaced[columns_with_pct] = df_replaced[columns_with_pct].replace('100.00', '100')

    return df_replaced

def addTwoNullCols(df):
    """
    Add two new columns 'Job Id' and 'Vendor' with NaN values to the DataFrame.

    Parameters:
        df (pandas.DataFrame): The DataFrame to which the new columns will be added.

    Returns:
        pandas.DataFrame: DataFrame with the two new columns added and NaN values filled with 'NULL'.
    """
    df['Job Id'] = np.nan
    df['Vendor'] = np.nan
    df.fillna("NULL", inplace=True)

    return df

# Convert UTC time to Singapore time
def convert_to_sg_time(utc_time):
    utc = pytz.utc.localize(utc_time)
    sg_time = utc.astimezone(pytz.timezone('Asia/Singapore'))
    return sg_time

def display_time() -> str:
    """Displays current UTC and Singapore times."""
    utc_time = datetime.utcnow()
    sg_time = convert_to_sg_time(utc_time).strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"##### Singapore Time: {sg_time}")
    # st.markdown(f"<p style='font-size:20px; font-weight:bold;'>{sg_time}</p>", unsafe_allow_html=True)
    return sg_time


def get_task_type(server: str) -> str:
    """Returns the task type based on the selected server."""
    return "Weekly Task" if server in ["GS QA", "GS CA"] else "Daily Task"


def calculate_adjusted_datetime(server: str) -> str:
    """Calculates adjusted datetime based on the server."""
    time_diff = timedelta(hours=9) if server == "GS SPORE" else timedelta(hours=8)
    # time_diff = timedelta(hours=9) if server == "GS SPORE" else timedelta(hours=8) # uncomment if env on local streamlit
    adjusted_datetime = (datetime.now() + time_diff).strftime("%Y-%m-%d %H:%M:%S")
    return adjusted_datetime


def process_uploaded_file(
    uploaded_file: io.BytesIO,
    task_type: str,
    selected_datetime: str,
    adjusted_datetime: str,
    selected_server: str,
    exclude_values=None
) -> pd.DataFrame:
    """
    Processes the uploaded file based on the task type, datetime, and server.
    
    Args:
        uploaded_file: The file uploaded by the user.
        task_type: The type of task (Daily/Weekly).
        selected_datetime: The user-selected datetime.
        adjusted_datetime: The adjusted datetime based on the server.
        selected_server: The selected server.

    Returns:
        A processed DataFrame.
    """
    # Select the appropriate processing function
    task_function = process_ca_data if task_type == "Weekly Task" and selected_server == "GS CA" else process_data
    df_processed = task_function(uploaded_file, selected_datetime, adjusted_datetime, exclude_values=exclude_values)

    # Add null columns for servers other than "GS SPORE"
    if selected_server != "GS SPORE":
        df_processed = addTwoNullCols(df_processed)

    return df_processed


def download_processed_data(df_processed: pd.DataFrame, uploaded_file_name: str, selected_server: str):
    """
    Generates a download button for the processed DataFrame.
    
    Args:
        df_processed: The processed DataFrame.
        uploaded_file_name: The name of the uploaded file.
        selected_server: The selected server.
    """
    with st.spinner("Generating download link..."):
        output = io.BytesIO()
        df_processed.to_excel(output, index=False, sheet_name='Sheet1')
        output.seek(0)

        processed_filename = f"{selected_server}_{os.path.splitext(uploaded_file_name)[0]}_transformed.xlsx"
        st.download_button(
            label="Download Processed Data",
            data=output,
            file_name=processed_filename,
            key="download_button"
        )