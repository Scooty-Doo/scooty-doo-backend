import psycopg
import csv
import json

# Database connection details
db_params = {
    "dbname": "sddb",
    "user": "user",
    "password": "pass",
    "host": "localhost",
    "port": 5432,
}

# path to the CSV file
cities_file_path = "../mock_data/generated_data/cities.csv"
users_file_path = "../mock_data/generated_data/users.csv"
payment_providers_file_path = "../mock_data/generated_data/payment_providers.json"
bike_status_file_path = "../mock_data/generated_data/bike_status.json"
bike_file_path = "../mock_data/generated_data/bikes.csv"
bike_2_status_file_path = "../mock_data/generated_data/bike2bike_status.csv"
trip_file_path = "../mock_data/generated_data/trip_data.csv"
zone_types_file_path = "../mock_data/generated_data/zone_types.csv"
map_zones_file_path = "../mock_data/generated_data/map_zones.csv"
admin_file_path = "../mock_data/generated_data/admins.csv"
admin_roles_file_path = "../mock_data/generated_data/admin_roles.csv"
admin_to_roles_file_path = "../mock_data/generated_data/admin_to_roles.csv"


# Psycogs to empty all tables in scooby_doo schema
with psycopg.connect(**db_params) as conn:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE scooty_doo.cities CASCADE")
        cur.execute("TRUNCATE TABLE scooty_doo.users CASCADE")
        cur.execute("TRUNCATE TABLE scooty_doo.payment_providers CASCADE")
        cur.execute("TRUNCATE TABLE scooty_doo.bike_status CASCADE")
        cur.execute("TRUNCATE TABLE scooty_doo.bikes CASCADE")
        cur.execute("TRUNCATE TABLE scooty_doo.bike_2_bike_status CASCADE")
        cur.execute("TRUNCATE TABLE scooty_doo.trips CASCADE")
        cur.execute("TRUNCATE TABLE scooty_doo.zone_types CASCADE")
        cur.execute("TRUNCATE TABLE scooty_doo.map_zones CASCADE")
        cur.execute("TRUNCATE TABLE scooty_doo.admins CASCADE")
        cur.execute("TRUNCATE TABLE scooty_doo.admin_roles CASCADE")
        cur.execute("TRUNCATE TABLE scooty_doo.admin_2_admin_roles CASCADE")
        conn.commit()

with psycopg.connect(**db_params) as conn:
    with conn.cursor() as cur:
        # Insert into cities table
        with open(cities_file_path, "r") as csvfile:
            cities_reader = csv.DictReader(csvfile)
            cities_data = [
                (row["id"], row["city_name"], row["country_code"], row["c_location"])
                for row in cities_reader
            ]

        cur.executemany(
            """
            INSERT INTO scooty_doo.cities (id, city_name, country_code, c_location)
            VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326))
            """,
            cities_data,
        )

        # Insert users
        with open(users_file_path, "r") as csvfile:
            users_reader = csv.DictReader(csvfile)
            users_data = [
                (
                    row["id"],
                    row["full_name"],
                    row["email"],
                    row["balance"],
                    row["use_prepay"],
                    row["created_at"],
                )
                for row in users_reader
            ]

        cur.executemany(
            """
            INSERT INTO scooty_doo.users (id, full_name, email, balance, use_prepay, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            users_data,
        )

        # Insert payment providers from JSON file
        with open(payment_providers_file_path, "r") as jsonfile:
            payment_providers_data = json.load(jsonfile)["payment_providers"]
            payment_providers_data = [
                (provider["provider_name"], json.dumps(provider["metadata"]))
                for provider in payment_providers_data
            ]

        cur.executemany(
            """
            INSERT INTO scooty_doo.payment_providers(provider_name, metadata)
            VALUES (%s, %s::jsonb)
            """,
            payment_providers_data,
        )

        # Insert bike status from JSON file
        with open(bike_status_file_path, "r") as jsonfile:
            bike_status_data = json.load(jsonfile)["bike_status"]
            bike_status_data = [
                (status["id"], status["status_code"], json.dumps(status["metadata"]))
                for status in bike_status_data
            ]

        cur.executemany(
            """
            INSERT INTO scooty_doo.bike_status(id, status_code, metadata)
            VALUES (%s, %s, %s::jsonb)
            """,
            bike_status_data,
        )

        # Insert bikes
        with open(bike_file_path, "r") as csvfile:
            bikes_reader = csv.DictReader(csvfile)
            bikes_data = [
                (
                    row["id"],
                    row["battery_lvl"],
                    row["last_position"],
                    row["city_id"],
                    row["created_at"],
                )
                for row in bikes_reader
            ]

        cur.executemany(
            """
            INSERT INTO scooty_doo.bikes(id, battery_lvl, last_position, city_id, created_at)
            VALUES (%s, %s, ST_GeomFromText(%s, 4326), %s, %s)
            """,
            bikes_data,
        )


        # Insert bike 2 bike status from csv file
        with open(bike_2_status_file_path, "r") as csvfile:
            bike_2_status_reader = csv.DictReader(csvfile)
            bike_2_status_data = [
                (row["bike_id"], row["status"], row["created_at"], row["updated_at"])
                for row in bike_2_status_reader
            ]

        cur.executemany(
            """
            INSERT INTO scooty_doo.bike_2_bike_status(bike_id, status_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            """,
            bike_2_status_data,
        )

        # Insert trips from CSV file
        with open(trip_file_path, "r") as csvfile:
            trips_reader = csv.DictReader(csvfile)
            trips_data = [
                (
                    row["bike_id"],
                    row["user_id"],
                    row["start_time"],
                    row["end_time"],
                    row["start_position"],
                    row["end_position"],
                    row["path_taken"],
                    row["start_fee"],
                    row["time_fee"],
                    row["end_fee"],
                    row["total_fee"],
                )
                for row in trips_reader
            ]

        cur.executemany(
            """
            INSERT INTO scooty_doo.trips(
                bike_id,
                user_id,
                start_time,
                end_time,
                start_position,
                end_position,
                path_taken,
                start_fee,
                time_fee,
                end_fee,
                total_fee
            )
            VALUES (%s, %s, %s, %s, ST_GeomFromText(%s, 4326), ST_GeomFromText(%s, 4326), ST_GeomFromText(%s, 4326), %s, %s, %s, %s)
            """,
            trips_data,
        )

        # Insert zone types from CSV file
        with open(zone_types_file_path, "r") as csvfile:
            zone_types_reader = csv.DictReader(csvfile)
            zone_types_data = [
                (
                    row["id"],
                    row["type_name"],
                    row["speed_limit"],
                    row["start_fee"],
                    row["end_fee"],
                )
                for row in zone_types_reader
            ]

        cur.executemany(
            """
            INSERT INTO scooty_doo.zone_types(id, type_name, speed_limit, start_fee, end_fee)
            VALUES (%s, %s, %s, %s, %s)
            """,
            zone_types_data,
        )

        # Insert map zones from CSV file
        with open(map_zones_file_path, "r") as csvfile:
            map_zones_reader = csv.DictReader(csvfile)
            map_zones_data = [
                (
                    row["zone_name"],
                    row["zone_type_id"],
                    row["city_id"],
                    row["boundary"],
                )
                for row in map_zones_reader
            ]

        cur.executemany(
            """
            INSERT INTO scooty_doo.map_zones(zone_name, zone_type_id, city_id, boundary)
            VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326))
            """,
            map_zones_data,
        )
        
        # Insert admins from CSV file
        with open(admin_file_path, "r") as csvfile:
            admin_reader = csv.DictReader(csvfile)
            admin_data = [
                (row["id"], row["full_name"], row["email"])
                for row in admin_reader
            ]

        cur.executemany(
            """
            INSERT INTO scooty_doo.admins(id, full_name, email)
            VALUES (%s, %s, %s)
            """,
            admin_data,
        )

        # Insert admin roles from CSV file
        with open(admin_roles_file_path, "r") as csvfile:
            admin_roles_reader = csv.DictReader(csvfile)
            admin_roles_data = [
                (row["id"], row["role_name"])
                for row in admin_roles_reader
            ]

        cur.executemany(
            """
            INSERT INTO scooty_doo.admin_roles(id, role_name)
            VALUES (%s, %s)
            """,
            admin_roles_data,
        )

        # Insert admin to roles from CSV file
        with open(admin_to_roles_file_path, "r") as csvfile:
            admin_to_roles_reader = csv.DictReader(csvfile)
            admin_to_roles_data = [
                (row["admin_id"], row["role_id"])
                for row in admin_to_roles_reader
            ]

        cur.executemany(
            """
            INSERT INTO scooty_doo.admin_2_admin_roles(admin_id, role_id)
            VALUES (%s, %s)
            """,
            admin_to_roles_data,
        )

        conn.commit()
