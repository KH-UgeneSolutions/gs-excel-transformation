import os
import io
import base64
import pandas as pd
import json
import streamlit.components.v1 as components


def copy_content_to_clipboard(df_processed: pd.DataFrame) -> None:
    """
    Generates a custom copy button for the processed DataFrame content.

    Args:
        df_processed (pd.DataFrame): The processed DataFrame.
    """
    # Convert DataFrame to CSV format without headers
    copy_text = df_processed.to_csv(index=False, header=False)

    # Escape the text for JavaScript
    copy_text_json = json.dumps(copy_text)  # Properly escape the content for JavaScript

    # Create a custom HTML button for copying
    copy_button_html = f"""
        <div>
            <button id="copyButton" style="padding: 10px 20px; font-size: 16px; color: white;
                    background-color: #4CAF50; border: none;
                    border-radius: 5px; cursor: pointer;">
                Copy Content
            </button>
            <p id="copyFeedback" style="color: green; display: none; margin-top: 10px;">
                Content copied to clipboard!
            </p>
        </div>
        <script>
            const copyButton = document.getElementById('copyButton');
            const feedback = document.getElementById('copyFeedback');
            copyButton.addEventListener('click', () => {{
                navigator.clipboard.writeText({copy_text_json}).then(() => {{
                    feedback.style.display = 'block';
                    setTimeout(() => {{
                        feedback.style.display = 'none';
                    }}, 2000);
                }}).catch(err => {{
                    alert('Failed to copy content.');
                }});
            }});
        </script>
    """

    # Use components.html to render the button
    components.html(copy_button_html, height=100)


def download_processed_data(df_processed: pd.DataFrame, uploaded_file_name: str, selected_server: str) -> None:
    """
    Generates a custom download button for the processed DataFrame.

    Args:
        df_processed (pd.DataFrame): The processed DataFrame.
        uploaded_file_name (str): The name of the uploaded file.
        selected_server (str): The selected server.
    """
    # Create a BytesIO object for the Excel file
    output = io.BytesIO()
    df_processed.to_excel(output, index=False, sheet_name="Sheet1")
    output.seek(0)

    # Generate the file name
    processed_filename = f"{selected_server}_{os.path.splitext(uploaded_file_name)[0]}_transformed.xlsx"

    # Encode the Excel file to base64
    b64 = base64.b64encode(output.read()).decode()

    # Create a custom HTML button for downloading with right alignment
    download_button_html = f"""
        <div style="text-align: right;">
            <a href="data:application/octet-stream;base64,{b64}" download="{processed_filename}">
                <button style="
                    padding: 10px 20px; font-size: 16px; color: white;
                    background-color: #007BFF; border: none;
                    border-radius: 5px; cursor: pointer;">
                    Download Processed Data
                </button>
            </a>
        </div>
    """

    # Use components.html to render the button
    components.html(download_button_html, height=70)
