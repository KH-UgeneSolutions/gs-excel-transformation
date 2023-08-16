import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

# Constant unit
gallon = 3.785411784
feet_squared = 0.09290304

# Function to process data
def process_data(file, selected_datetime_str):
    df = pd.read_excel(file, skiprows=1)
    drop_columns = ['Total time', 'Task status', 'Plan running time (s)', 'Uncleaned area (㎡)', 'Task start mode', 'Remarks']
    df.drop(columns=drop_columns, inplace=True)
    df.insert(0, 'Id', np.nan)
    
    selected_datetime = datetime.strptime(selected_datetime_str, "%Y-%m-%d %H:%M:%S")
    selected_datetime_sg = pytz.timezone('Asia/Singapore').localize(selected_datetime)  # Convert to Singapore time
    
    current_datetime_sg = pytz.timezone('Asia/Singapore').localize(datetime.now())  # Convert to Singapore time
    new_datetime = current_datetime_sg + timedelta(minutes=15)
    formatted_datetime = new_datetime.strftime("%Y-%m-%d %H:%M:00")
    
    df['Receive task report time'] = pd.to_datetime(df['Receive task report time']).dt.tz_localize('UTC').dt.tz_convert('Asia/Singapore')  # Convert to Singapore time
    df_filtered = df[df['Receive task report time'] > selected_datetime_sg]
    df_filtered = df_filtered.sort_values(by='Receive task report time', ascending=False)
    df_filtered.reset_index(drop=True, inplace=True)
    
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
    columns_to_update = ['Planned crystallization area (㎡)', 'Actual crystallization area (㎡)']
    df_test.loc[:, columns_to_update] = formatted_datetime
    
    df_replaced = df_test.applymap(lambda cell: 0 if cell == '-' else cell)
    df_replaced = df_replaced.fillna("NULL")
    columns_with_comma = ['Work efficiency (㎡/h)', 'Actual cleaning area(㎡)', 'Cleaning plan area (㎡)']
    columns_with_pct = ['Brush (%)', 'Filter (%)', 'Squeegee(%)']
    df_replaced[columns_with_comma] = df_replaced[columns_with_comma].apply(lambda x: x.str.replace(',', ''))

    df_replaced[columns_with_comma] = df_replaced[columns_with_comma].replace('0.00', '0')
    df_replaced[columns_with_pct] = df_replaced[columns_with_pct].replace('100.00', '100')

    # Convert datetime columns to string without timezone information
    datetime_columns = ['Receive task report time']
    for col in datetime_columns:
        df_replaced[col] = df_replaced[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    return df_replaced

def process_ca_data(file, selected_datetime_str):
    df = pd.read_excel(file, skiprows=1)
    drop_columns = ['Total time', 'Task status', 'Plan running time (s)', 'Uncleaned area (ft²)', 'Task start mode', 'Remarks']
    df.drop(columns=drop_columns, inplace=True)
    df.insert(0, 'Id', np.nan)
    
    selected_datetime = datetime.strptime(selected_datetime_str, "%Y-%m-%d %H:%M:%S")
    selected_datetime_sg = pytz.timezone('Asia/Singapore').localize(selected_datetime)  # Convert to Singapore time
    
    current_datetime_sg = pytz.timezone('Asia/Singapore').localize(datetime.now())  # Convert to Singapore time
    new_datetime = current_datetime_sg + timedelta(minutes=15)
    formatted_datetime = new_datetime.strftime("%Y-%m-%d %H:%M:00")
    
    df['Receive task report time'] = pd.to_datetime(df['Receive task report time']).dt.tz_localize('UTC').dt.tz_convert('Asia/Singapore')  # Convert to Singapore time
    df_filtered = df[df['Receive task report time'] > selected_datetime_sg]
    df_filtered = df_filtered.sort_values(by='Receive task report time', ascending=False)
    df_filtered.reset_index(drop=True, inplace=True)
    
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
    columns_to_update = ['Planned crystallization area (ft²)', 'Actual crystallization area (ft²)']
    df_test.loc[:, columns_to_update] = formatted_datetime
    
    df_replaced = df_test.applymap(lambda cell: 0 if cell == '-' else cell)
    df_replaced = df_replaced.fillna("NULL")
    columns_with_comma = ['Work efficiency (ft²/h)', 'Actual cleaning area(ft²)', 'Cleaning plan area (ft²)']
    columns_with_pct = ['Brush (%)', 'Filter (%)', 'Squeegee(%)']
    df_replaced[columns_with_comma] = df_replaced[columns_with_comma].apply(lambda x: x.str.replace(',', ''))

    df_replaced['Water usage (gal)'] = df_replaced['Water usage (gal)'] * gallon
    df_replaced[columns_with_comma] = df_replaced[columns_with_comma].apply(pd.to_numeric) * feet_squared
    df_replaced[columns_with_comma] = df_replaced[columns_with_comma].applymap(lambda x: str(x).replace(',', ''))

    df_replaced[columns_with_comma] = df_replaced[columns_with_comma].replace('0.0', '0')
    df_replaced[columns_with_pct] = df_replaced[columns_with_pct].replace('100.00', '100')

    # Convert datetime columns to string without timezone information
    datetime_columns = ['Receive task report time']
    for col in datetime_columns:
        df_replaced[col] = df_replaced[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    return df_replaced

def addTwoNullCols(df):
    df['Job Id'] = np.nan
    df['Vendor'] = np.nan
    df.fillna("NULL", inplace=True)

    return df

# Convert UTC time to Singapore time
def convert_to_sg_time(utc_time):
    utc = pytz.utc.localize(utc_time)
    sg_time = utc.astimezone(pytz.timezone('Asia/Singapore'))
    return sg_time