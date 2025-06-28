# Project 1: Automated Weather Data Pipeline

This project is a complete, end-to-end ETL (Extract, Transform, Load) pipeline that automatically fetches daily weather forecast data from the OpenWeatherMap API, cleans and transforms it using Python and Pandas, and loads it into a PostgreSQL database.

The entire process is automated to run daily using Windows Task Scheduler.

## Core Skills Demonstrated
*   **Data Extraction:** Interacting with a REST API (`requests`).
*   **Data Transformation:** Data cleaning, shaping, and type conversion (`pandas`).
*   **Database Management (SQL):** Schema design (DDL), data loading (DML), and querying (`psycopg2`, PostgreSQL).
*   **Automation:** Scheduling tasks to run automatically (Windows Task Scheduler).
*   **Python Best Practices:** Using virtual environments (`venv`), managing secrets (`.env`), and dependency management (`requirements.txt`).
*   **System Design:** Building an idempotent pipeline that can be re-run without causing errors or duplicates.


## Database Schema

The PostgreSQL database uses a normalized schema with two tables to efficiently store the data.

```sql
-- This table stores the unique locations we are tracking.
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(5) NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    UNIQUE (city, country, latitude, longitude)
);
```

-- This table stores the weather forecast readings for each location.

```sql
CREATE TABLE weather_readings (
    reading_id SERIAL PRIMARY KEY,
    location_id INT NOT NULL,
    forecast_time TIMESTAMPTZ NOT NULL,
    temperature_celsius DECIMAL(5, 2),
    feels_like_celsius DECIMAL(5, 2),
    humidity_percent INT,
    wind_speed_ms DECIMAL(5, 2),
    description VARCHAR(255),
    weather_icon VARCHAR(10),
    FOREIGN KEY (location_id) REFERENCES locations (location_id),
    UNIQUE (location_id, forecast_time)
);
```

## Example Analytical Queries

Here are some example SQL queries that can be run on the final database to derive insights.

1. What is the average temperature for the next 5 days?
```sql
SELECT 
    locations.city,
    AVG(weather_readings.temperature_celsius) as avg_temp_celsius
FROM weather_readings
JOIN locations ON weather_readings.location_id = locations.location_id
WHERE locations.city = 'Tokyo'
GROUP BY locations.city;
```
2. When will it be the warmest in the next 24 hours?
```sql
SELECT 
    forecast_time, 
    temperature_celsius
FROM weather_readings
WHERE forecast_time BETWEEN NOW() AND NOW() + INTERVAL '24 hours'
ORDER BY temperature_celsius DESC
LIMIT 1;
```
3. Will I need an umbrella? (Find days with rain)
```sql
SELECT
    DISTINCT DATE(forecast_time) as rain_date,
    description
FROM weather_readings
WHERE description ILIKE '%rain%';
```
## How to Run This Project Locally

Follow these steps to set up and run the pipeline on your own machine.

1.  **Prerequisites:**
    *   Python 3.8+
    *   PostgreSQL installed and running.
    *   Git installed.

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
    *(Remember to replace `your-username` and `your-repo-name` with your actual GitHub details)*

3.  **Set up the Database:**
    *   Create a new database in PostgreSQL (e.g., `weather_db`).
    *   Connect to the database and run the script in `schema.sql` to create the tables.

4.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

5.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Create a `.env` file** in the root of the project and add your credentials:
    ```
    API_KEY=your_openweathermap_api_key
    DB_PASSWORD=your_database_password
    ```

7.  **Run the pipeline manually:**
    ```bash
    python pipeline.py
    ```

