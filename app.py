import streamlit as st
import pandas as pd
import numpy as np
from xlsxwriter import Workbook
from utils import process_data, process_ca_data, addTwoNullCols
import io, os

# Streamlit app
st.title("Data Processing and Transformation with Streamlit")
st.write("This web app aims to perform data processing and transformation to fit the database input format.")

# Sidebar options
servers = ["GS SPORE", "GS AUS Eclipse", "Metroplaza Ecobot GS Cloud", "GS HK", "GS CA"]
selected_server = st.sidebar.selectbox("Select Server", servers)

# Determine task type based on server
if selected_server in ["GS HK", "GS CA"]:
    task_type = "Weekly Task"
else:
    task_type = "Daily Task"

uploaded_file_label = f"Upload an Excel file for {task_type}"
task_function = process_ca_data if task_type == "Weekly Task" and selected_server == "GS CA" else process_data

uploaded_file = st.file_uploader(uploaded_file_label, type=["xlsx"])
if uploaded_file is not None:
    selected_datetime_str = st.text_input("Please Enter the [Receive Task Report Time]", value="", max_chars=19, key="selected_datetime")
    if st.button("Process"):
        df_processed = task_function(uploaded_file, selected_datetime_str)

        # Insert NaN columns for all servers except "GS SPORE"
        if selected_server != "GS SPORE":
            df_processed = addTwoNullCols(df_processed)

        st.write("Processed DataFrame:")
        st.dataframe(df_processed)
        
        # Display the number of rows and columns
        num_rows, num_cols = df_processed.shape
        st.write(f"Number of rows: {num_rows}")
        st.write(f"Number of columns: {num_cols}")

        # Download Processed Data
        with st.spinner("Generating download link..."):
            output = io.BytesIO()
            df_processed.to_excel(output, index=False, sheet_name='Sheet1')  # Save Excel using Pandas
            output.seek(0)

            # Get the uploaded filename and add '_transformed' suffix
            uploaded_filename = os.path.splitext(uploaded_file.name)[0]
            processed_filename = f"{selected_server}_{uploaded_filename}_transformed.xlsx"

            st.download_button(
                label="Download Processed Data",
                data=output,
                file_name=processed_filename,
                key="download_button"
            )