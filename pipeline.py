import requests
import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# --- SETUP ---
load_dotenv()

# --- DATABASE CREDENTIALS ---
# Get these from your PostgreSQL setup
DB_NAME = "weather_db"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("DB_PASSWORD") # We'll add this to the .env file
DB_HOST = "localhost"
DB_PORT = "5432"

# --- EXTRACT ---
def get_weather_data(api_key, city, country_code):
    """Fetches 5-day/3-hour forecast data from the OpenWeatherMap API."""
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},{country_code}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("API request successful!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

# --- TRANSFORM ---
def transform_data(raw_data):
    """Transforms raw JSON data into two clean Pandas DataFrames."""
    location_data = {
        "city": raw_data["city"]["name"],
        "country": raw_data["city"]["country"],
        "latitude": raw_data["city"]["coord"]["lat"],
        "longitude": raw_data["city"]["coord"]["lon"]
    }
    df_location = pd.DataFrame([location_data])

    forecast_list = raw_data["list"]
    weather_data = []
    for entry in forecast_list:
        weather_data.append({
            "forecast_time": entry["dt_txt"],
            "temperature_celsius": entry["main"]["temp"],
            "feels_like_celsius": entry["main"]["feels_like"],
            "humidity_percent": entry["main"]["humidity"],
            "wind_speed_ms": entry["wind"]["speed"],
            "description": entry["weather"][0]["description"],
            "weather_icon": entry["weather"][0]["icon"]
        })
    df_weather = pd.DataFrame(weather_data)
    df_weather["forecast_time"] = pd.to_datetime(df_weather["forecast_time"], utc=True)
    print("Data transformed successfully.")
    return df_location, df_weather

# --- LOAD ---
def load_to_db(df_loc, df_weath):
    """Connects to PostgreSQL and loads the dataframes into the database."""
    conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}' port='{DB_PORT}'"
    
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("Database connection established.")
                
                # --- Load Location Data ---
                loc_city, loc_country, loc_lat, loc_lon = df_loc.iloc[0]
                sql_insert_location = """
                    INSERT INTO locations (city, country, latitude, longitude)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (city, country, latitude, longitude) DO NOTHING;
                """
                # THE FIX: Convert NumPy types to standard Python types before inserting
                cur.execute(sql_insert_location, (loc_city, loc_country, float(loc_lat), float(loc_lon)))

                # Get the location_id of the city (either the one just inserted or the existing one)
                cur.execute("SELECT location_id FROM locations WHERE city = %s AND country = %s;", (loc_city, loc_country))
                location_id = cur.fetchone()[0]
                
                # --- Load Weather Data ---
                print(f"Loading weather data for location_id: {location_id}")
                for index, row in df_weath.iterrows():
                    sql_insert_weather = """
                        INSERT INTO weather_readings (location_id, forecast_time, temperature_celsius, feels_like_celsius, humidity_percent, wind_speed_ms, description, weather_icon)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (location_id, forecast_time) DO NOTHING;
                    """
                    # THE FIX: Convert all numeric types from the row to standard Python types
                    cur.execute(sql_insert_weather, (
                        location_id,
                        row['forecast_time'],
                        float(row['temperature_celsius']),
                        float(row['feels_like_celsius']),
                        int(row['humidity_percent']),
                        float(row['wind_speed_ms']),
                        row['description'],
                        row['weather_icon']
                    ))
                
                conn.commit()
                print("Data loaded successfully to the database.")
    except Exception as e:
        print(f"Database operation failed: {e}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("Starting the weather data pipeline...")
    API_KEY = os.getenv("API_KEY")
    CITY_NAME = "Tokyo"
    COUNTRY_CODE = "JP"
    
    # --- EXTRACT ---
    raw_data = get_weather_data(API_KEY, CITY_NAME, COUNTRY_CODE)

    if raw_data:
        # --- TRANSFORM ---
        df_location, df_weather = transform_data(raw_data)
        
        # --- LOAD ---
        load_to_db(df_location, df_weather)
    else:
        print("Pipeline failed: Could not extract data.")

    print("Pipeline finished.")