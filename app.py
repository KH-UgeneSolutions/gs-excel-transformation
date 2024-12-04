import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import display_time, get_task_type, calculate_adjusted_datetime, process_uploaded_file, download_processed_data



# Streamlit App Setup
st.title("Data Processing and Transformation with Streamlit")
st.markdown("#### This web app performs data processing and transformation to fit the database input format.")

# Display times
sg_time = display_time()

# Sidebar options
servers = ["GS SPORE", "GS AUS Eclipse", "GS QA", "GS Metroplaza", "GS MSIA", "GS CA"]
selected_server = st.sidebar.selectbox("Select Server", servers)

# Determine task type and adjusted datetime
task_type = get_task_type(selected_server)
adjusted_datetime = calculate_adjusted_datetime(selected_server)

# File upload section
uploaded_file_label = f" ##### Upload a CSV or XLSX file for {task_type}"
# st.markdown(uploaded_file_label)
uploaded_file = st.file_uploader(uploaded_file_label, type=["csv","xlsx"])

# Input for dynamic exclusion of 'S/N' values
exclude_values = None
if selected_server == "GS AUS Eclipse":
    st.markdown("#### Exclude S/N Values")
    exclude_values_input = st.text_area(
        "Enter S/N values to exclude (comma-separated):",
        value="",
        placeholder="e.g., 123, 456, 789"
    )
    if exclude_values_input:
        exclude_values = [value.strip() for value in exclude_values_input.split(",")]

if uploaded_file:
    selected_datetime_str = st.text_input(
        "Please Enter the [Receive Task Report Time]",
        value="",
        max_chars=19,
        key="selected_datetime"
    )

    if st.button("Process"):
        try:
            # Parse the input datetime
            selected_datetime = datetime.strptime(selected_datetime_str, "%Y-%m-%d %H:%M:%S")

            # # Process the uploaded file
            # df_processed = process_uploaded_file(
            #     uploaded_file,
            #     task_type,
            #     selected_datetime_str,
            #     adjusted_datetime,
            #     selected_server,
            #     exclude_values=exclude_values 
            # )
            
            # Prepare arguments for process_uploaded_file
            process_args = {
                "uploaded_file": uploaded_file,
                "task_type": task_type,
                "selected_datetime": selected_datetime_str,
                "adjusted_datetime": adjusted_datetime,
                "selected_server": selected_server,
            }

            # Add 'exclude_values' to arguments only if server is 'GS AUS Eclipse'
            if selected_server == "GS AUS Eclipse" and exclude_values:
                process_args["exclude_values"] = exclude_values

            # Process the uploaded file
            df_processed = process_uploaded_file(**process_args)

            # Display processed data and metadata
            st.markdown("### Processed DataFrame:")
            st.dataframe(df_processed)

            num_rows, num_cols = df_processed.shape
            st.markdown(f"**Number of rows:** {num_rows}")
            st.markdown(f"**Number of columns:** {num_cols}")

            # Download processed data
            download_processed_data(df_processed, uploaded_file.name, selected_server)

        except ValueError:
            st.error("Invalid datetime format.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
