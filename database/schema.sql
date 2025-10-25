-- Phoenix Air Database Schema

-- Airports
CREATE TABLE IF NOT EXISTS airports (
    airport_code VARCHAR(3) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    timezone VARCHAR(50) NOT NULL
);

-- Customers (users)
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    frequent_flyer_number VARCHAR(20) UNIQUE,
    membership_tier VARCHAR(20) DEFAULT 'silver',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aircraft
CREATE TABLE IF NOT EXISTS aircraft (
    aircraft_id SERIAL PRIMARY KEY,
    registration VARCHAR(10) UNIQUE NOT NULL,
    model VARCHAR(50) NOT NULL,
    total_seats INT NOT NULL,
    economy_seats INT NOT NULL,
    business_seats INT NOT NULL,
    first_class_seats INT NOT NULL
);

-- Flights
CREATE TABLE IF NOT EXISTS flights (
    flight_id SERIAL PRIMARY KEY,
    flight_number VARCHAR(10) NOT NULL,
    origin_airport VARCHAR(3) REFERENCES airports(airport_code),
    destination_airport VARCHAR(3) REFERENCES airports(airport_code),
    aircraft_id INT REFERENCES aircraft(aircraft_id),
    scheduled_departure TIMESTAMP NOT NULL,
    scheduled_arrival TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    gate VARCHAR(10),
    price_economy DECIMAL(10,2) NOT NULL,
    price_business DECIMAL(10,2) NOT NULL,
    price_first DECIMAL(10,2) NOT NULL,
    available_economy INT NOT NULL,
    available_business INT NOT NULL,
    available_first INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample airports
INSERT INTO airports (airport_code, name, city, country, timezone) VALUES
('JFK', 'John F Kennedy International', 'New York', 'USA', 'America/New_York'),
('LAX', 'Los Angeles International', 'Los Angeles', 'USA', 'America/Los_Angeles'),
('ORD', 'O''Hare International', 'Chicago', 'USA', 'America/Chicago'),
('ATL', 'Hartsfield-Jackson Atlanta', 'Atlanta', 'USA', 'America/New_York'),
('SFO', 'San Francisco International', 'San Francisco', 'USA', 'America/Los_Angeles')
ON CONFLICT (airport_code) DO NOTHING;

-- Insert sample aircraft
INSERT INTO aircraft (registration, model, total_seats, economy_seats, business_seats, first_class_seats) VALUES
('N12345', 'Boeing 737-800', 175, 150, 20, 5),
('N23456', 'Airbus A320', 180, 156, 20, 4)
ON CONFLICT (registration) DO NOTHING;
