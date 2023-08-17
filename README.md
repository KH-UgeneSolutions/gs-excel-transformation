# gs-excel-transformation

Access the Streamlit web app here: https://gs-excel-transformation.streamlit.app/

## Important Notes
1. The time differences on this repo are meant for the Singapore time zone on the Streamlit server due to their time zone (UTC+0)
2. To test it locally, kindly ignore or adjust the `time_difference = timedelta(hours=9)` on the `utils.py` file

## How to use this Repository

1. At your project directory, clone this repo
```
git clone https://github.com/KH-UgeneSolutions/gs-excel-transformation.git
```
2. Activate your venv (Windows)
```
python -m venv venv & venv\Scripts\activate
```
3. Install the python dependencies for this project
```
pip install -r requirements.txt
```

## Deploying to Browser
1. Run the streamlit command (note that `app.py` must be in same directory before running the command)
```
streamlit run app.py
```
