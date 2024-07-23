import requests
import pandas as pd
from google.cloud import bigquery
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

def is_running_in_gcp():
    return os.getenv('K_SERVICE', False)

def extract_data(request):
    # Get parameters from the request
    request_json = request.get_json()
    api_key = os.getenv('API_KEY')
    city = request_json['city']

    # Fetch data from OpenWeatherMap API
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    return data

def transform_data(data):
    # Transform data
    # Unnest the JSON data
    transformed_data = {
        "lon": data['coord']['lon'],
        "lat": data['coord']['lat'],
        "weather_id": data['weather'][0]['id'],
        "weather_main": data['weather'][0]['main'],
        "weather_description": data['weather'][0]['description'],
        "weather_icon": data['weather'][0]['icon'],
        "base": data['base'],
        "temp": data['main']['temp'],
        "feels_like": data['main']['feels_like'],
        "temp_min": data['main']['temp_min'],
        "temp_max": data['main']['temp_max'],
        "pressure": data['main']['pressure'],
        "humidity": data['main']['humidity'],
        "visibility": data['visibility'],
        "wind_speed": data['wind']['speed'],
        "wind_deg": data['wind']['deg'],
        "clouds_all": data['clouds']['all'],
        "dt": data['dt'],
        "sys_type": data['sys']['type'],
        "sys_id": data['sys']['id'],
        "country": data['sys']['country'],
        "sunrise": data['sys']['sunrise'],
        "sunset": data['sys']['sunset'],
        "timezone": data['timezone'],
        "id": data['id'],
        "name": data['name'],
        "cod": data['cod']
    }

    df = pd.DataFrame([transformed_data])

    return df

def upload_df_to_bigquery(dataframe: pd.DataFrame, project_id: str, dataset_id: str, table_name: str):
    """Uploads a pandas DataFrame to a BigQuery table."""

    # Construct a BigQuery client object.
    client = bigquery.Client() if is_running_in_gcp() else bigquery.Client.from_service_account_json('bigquery.json')
    dataset_id = f"{project_id}.{dataset_id}"

    # Construct a full Dataset object to send to the API.
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "us-central1"  # Replace with your preferred location
    try:
       dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
       print("Created dataset {}.{}".format(client.project, dataset.dataset_id))
    except:
        print("Dataset already exists")

    table_id = f"{dataset_id}.{table_name}"

    # Modify job_config for partitioning and truncating
    job_config = bigquery.LoadJobConfig(
          autodetect=True,
          write_disposition='WRITE_APPEND',
          create_disposition='CREATE_IF_NEEDED'
    )

    print("Created a BigQuery job_config variable")

    # Make an API request to store the data into BigQuery
    try:
        job = client.load_table_from_dataframe(dataframe, table_id, job_config=job_config)
        job.result()  # Wait for the job to complete.
        print("Saved data into BigQuery")
    except Exception as e:
        print(dataframe.dtypes)
        print(table_id)
        print(job_config)
        print(e)
        raise e

def main(request):

    # Extract data from weather API
    data = extract_data(request)

    # Transform data using Pandas
    df = transform_data(data)

    # Load data into BigQuery
    gcp_project_id = os.getenv('GCP_PROJECT_ID')
    gcp_dataset_name = os.getenv('GCP_DATASET_NAME')
    gcp_table_name = os.getenv('GCP_TABLE_NAME')
    upload_df_to_bigquery(df, gcp_project_id, gcp_dataset_name, gcp_table_name)

    return {"status": "success"}

if __name__ == "__main__":
    # For local testing
    city = "Thessaloniki"

    # Simulate request data
    request_data = {
        "city": city,
    }

    # Convert to a request-like object
    class Request:
        def __init__(self, json):
            self._json = json

        def get_json(self):
            return self._json

    simulated_request = Request(request_data)

    # Call main with simulated request
    print(main(simulated_request))