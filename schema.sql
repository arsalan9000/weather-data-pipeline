-- Drop tables if they exist to start fresh
DROP TABLE IF EXISTS weather_readings;
DROP TABLE IF EXISTS locations;

-- This table stores the unique locations we are tracking.
-- We use latitude and longitude as part of the unique key to differentiate
-- between cities with the same name in different places.
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY, -- A unique, auto-incrementing ID for each location
    city VARCHAR(100) NOT NULL,
    country VARCHAR(5) NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    UNIQUE (city, country, latitude, longitude) -- This combination must be unique
);

-- This table stores the weather forecast readings for each location.
-- Each reading is linked to a location via the `location_id`.
CREATE TABLE weather_readings (
    reading_id SERIAL PRIMARY KEY,
    location_id INT NOT NULL,
    forecast_time TIMESTAMPTZ NOT NULL, -- TIMESTAMPTZ is crucial for handling timezones correctly
    temperature_celsius DECIMAL(5, 2),
    feels_like_celsius DECIMAL(5, 2),
    humidity_percent INT,
    wind_speed_ms DECIMAL(5, 2),
    description VARCHAR(255),
    weather_icon VARCHAR(10),
    
    -- This creates the relationship between weather_readings and locations
    FOREIGN KEY (location_id) REFERENCES locations (location_id),
    
    -- A location can only have one forecast for a specific point in time.
    -- This prevents duplicate entries for the same forecast.
    UNIQUE (location_id, forecast_time)
);

-- Optional: Create an index for faster lookups on forecast_time
CREATE INDEX idx_forecast_time ON weather_readings(forecast_time);