import pytest
import requests
import pandas as pd
from main import extract_data, transform_data
import os

@pytest.fixture
def sample_raw_data():
    """Fixture to provide sample raw data for tests"""
    return {
        "coord": {"lon": -0.13, "lat": 51.51},
        "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
        "main": {
            "temp": 280.32,
            "feels_like": 278.35,
            "temp_min": 279.15,
            "temp_max": 281.15,
            "pressure": 1012,
            "humidity": 81
        },
        "visibility": 10000,
        "wind": {"speed": 4.1, "deg": 80},
        "clouds": {"all": 0},
        "dt": 1485789600,
        "sys": {
            "type": 1,
            "id": 5091,
            "country": "GB",
            "sunrise": 1485762037,
            "sunset": 1485794875
        },
        "timezone": 0,
        "id": 2643743,
        "name": "London",
        "cod": 200,
        "base": "stations"
    }

def test_extract_data(requests_mock, sample_raw_data):
    """Test the data extraction from the Weather API"""
    city = "London"
    api_key = os.getenv('API_KEY', 'fake_api_key')  # Use the environment variable or a default value
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    requests_mock.get(url, json=sample_raw_data)

    request_data = {"city": city}

    class Request:
        def __init__(self, json):
            self._json = json

        def get_json(self):
            return self._json

    simulated_request = Request(request_data)

    data = extract_data(simulated_request)

    assert data["name"] == "London"
    assert data["weather"][0]["main"] == "Clear"

def test_transform_data(sample_raw_data):
    """Test the data transformation into a DataFrame"""
    df = transform_data(sample_raw_data)

    assert isinstance(df, pd.DataFrame)
    assert df.at[0, "lon"] == -0.13
    assert df.at[0, "lat"] == 51.51
    assert df.at[0, "weather_id"] == 800
    assert df.at[0, "weather_main"] == "Clear"
    assert df.at[0, "weather_description"] == "clear sky"
    assert df.at[0, "weather_icon"] == "01d"
    assert df.at[0, "base"] == "stations"
    assert df.at[0, "temp"] == 280.32
    assert df.at[0, "feels_like"] == 278.35
    assert df.at[0, "temp_min"] == 279.15
    assert df.at[0, "temp_max"] == 281.15
    assert df.at[0, "pressure"] == 1012
    assert df.at[0, "humidity"] == 81
    assert df.at[0, "visibility"] == 10000
    assert df.at[0, "wind_speed"] == 4.1
    assert df.at[0, "wind_deg"] == 80
    assert df.at[0, "clouds_all"] == 0
    assert df.at[0, "dt"] == 1485789600
    assert df.at[0, "sys_type"] == 1
    assert df.at[0, "sys_id"] == 5091
    assert df.at[0, "country"] == "GB"
    assert df.at[0, "sunrise"] == 1485762037
    assert df.at[0, "sunset"] == 1485794875
    assert df.at[0, "timezone"] == 0
    assert df.at[0, "id"] == 2643743
    assert df.at[0, "name"] == "London"
    assert df.at[0, "cod"] == 200

def test_transform_data_dtypes(sample_raw_data):
    """Test the data types of the transformed DataFrame"""
    df = transform_data(sample_raw_data)

    expected_dtypes = {
        "lon": "float64",
        "lat": "float64",
        "weather_id": "int64",
        "weather_main": "object",
        "weather_description": "object",
        "weather_icon": "object",
        "base": "object",
        "temp": "float64",
        "feels_like": "float64",
        "temp_min": "float64",
        "temp_max": "float64",
        "pressure": "int64",
        "humidity": "int64",
        "visibility": "int64",
        "wind_speed": "float64",
        "wind_deg": "int64",
        "clouds_all": "int64",
        "dt": "int64",
        "sys_type": "int64",
        "sys_id": "int64",
        "country": "object",
        "sunrise": "int64",
        "sunset": "int64",
        "timezone": "int64",
        "id": "int64",
        "name": "object",
        "cod": "int64"
    }

    for column, dtype in expected_dtypes.items():
        assert df[column].dtype == dtype, f"Expected {column} to be {dtype}, but got {df[column].dtype}"
