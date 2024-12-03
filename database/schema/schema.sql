-- Set encoding to UTF-8
SET
    client_encoding = 'UTF8';

-- Ensure standard conforming strings are enabled
SET
    standard_conforming_strings = 'on';

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "postgis";

-- Schema creation
CREATE SCHEMA IF NOT EXISTS scooty_doo;

-- Set the search path to the new schema
SET
    search_path TO scooty_doo, public;

-- Create cities table
CREATE TABLE
    IF NOT EXISTS cities (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        city_name TEXT NOT NULL,
        country_code CHAR(3) UNIQUE NOT NULL,
        c_location GEOMETRY (POINT, 4326) NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

-- Create users table
CREATE TABLE
    IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        balance NUMERIC(10, 2) DEFAULT 0.00,
        use_prepay BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

-- Create payment_providers table
CREATE TABLE
    IF NOT EXISTS payment_providers (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        provider_name TEXT NOT NULL UNIQUE,
        metadata JSONB,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

-- Create payment_methods table
CREATE TABLE
    IF NOT EXISTS payment_methods (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        user_id UUID NOT NULL REFERENCES users (id),
        provider_id INT NOT NULL REFERENCES payment_providers (id),
        provider_specific_id TEXT NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        is_default BOOLEAN DEFAULT FALSE,
        metadata JSONB,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

-- Create bike_status table
CREATE TABLE
    IF NOT EXISTS bike_status (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        status_code TEXT UNIQUE NOT NULL,
        status_description TEXT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

-- Create bikes table
CREATE TABLE
    IF NOT EXISTS bikes (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        model TEXT NOT NULL,
        firm_ware_version TEXT NOT NULL,
        battery_lvl INT NOT NULL CHECK (
            battery_lvl >= 0
            AND battery_lvl <= 100
        ),
        last_position GEOMETRY (POINT, 4326),
        city_id INT NOT NULL REFERENCES cities (id),
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

-- Create bike_2_bike_status table
CREATE TABLE
    IF NOT EXISTS bike_2_bike_status (
        bike_id INT NOT NULL REFERENCES bikes (id),
        status_id INT NOT NULL REFERENCES bike_status (id),
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (bike_id, status_id)
    );

-- Create trips table
CREATE TABLE
    IF NOT EXISTS trips (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        bike_id INT NOT NULL REFERENCES bikes (id),
        user_id UUID NOT NULL REFERENCES users (id),
        start_time TIMESTAMPTZ NOT NULL,
        end_time TIMESTAMPTZ,
        start_position GEOMETRY (POINT, 4326) NOT NULL,
        end_position GEOMETRY (POINT, 4326),
        path_taken GEOMETRY (LINESTRING, 4326),
        start_fee NUMERIC(10, 2),
        time_fee NUMERIC(10, 2),
        end_fee NUMERIC(10, 2),
        total_fee NUMERIC(10, 2),
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

-- Create zone_type table
CREATE TABLE
    IF NOT EXISTS zone_types (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        type_name TEXT UNIQUE NOT NULL,
        speed_limit INT,
        start_fee NUMERIC(10, 2) NOT NULL,
        end_fee NUMERIC(10, 2) NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

-- Create map_zone table
CREATE TABLE
    IF NOT EXISTS map_zones (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        zone_name TEXT NOT NULL,
        zone_type_id INT NOT NULL REFERENCES zone_types (id),
        city_id INT NOT NULL REFERENCES cities (id),
        boundary GEOMETRY (POLYGON, 4326) NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

-- Create admin table
CREATE TABLE
    IF NOT EXISTS admins (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

-- Create admin_roles table
CREATE TABLE
    IF NOT EXISTS admin_roles (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        role_name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

-- Create admin_2_admin_roles table
CREATE TABLE
    IF NOT EXISTS admin_2_admin_roles (
        admin_id UUID NOT NULL REFERENCES admins (id),
        role_id INT NOT NULL REFERENCES admin_roles (id),
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (admin_id, role_id)
    );

-- Create transactions table
CREATE TABLE
    IF NOT EXISTS transactions (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        user_id UUID NOT NULL REFERENCES users (id),
        amount DECIMAL(10, 2) NOT NULL CHECK (amount <> 0),
        transaction_type TEXT NOT NULL CHECK (transaction_type IN ('trip', 'deposit', 'refund')),
        transaction_description TEXT,
        trip_id INT REFERENCES trips (id),
        payment_method_id UUID REFERENCES payment_methods (id),
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        CHECK (
            (
                transaction_type = 'trip'
                AND trip_id IS NOT NULL
                AND payment_method_id IS NULL
            )
            OR (
                transaction_type = 'deposit'
                AND trip_id IS NULL
                AND payment_method_id IS NOT NULL
            )
            OR (
                transaction_type = 'refund'
                AND trip_id IS NULL
                AND payment_method_id IS NULL
            )
        )
    );