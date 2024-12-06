import csv
import random
from datetime import datetime, timedelta
import json
import requests
import time
from shapely.geometry import Point, LineString
from shapely.wkt import dumps
import polyline
from tsidpy import TSID

import csv

def generate_zone_types(output_file: str) -> None:
    """
    Generates a CSV file with zone type data.
    """
    zone_types = [
        {
            "id": 1,
            "type_name": "Parking",
            "speed_limit": 0,
            "start_fee": 5,
            "end_fee": 5,
        },
        {
            "id": 2,
            "type_name": "Charging",
            "speed_limit": 0,
            "start_fee": 0,
            "end_fee": 0,
        },
        {
            "id": 3,
            "type_name": "Forbidden",
            "speed_limit": 0,
            "start_fee": 5,
            "end_fee": 20,
        },
        {
            "id": 4,
            "type_name": "Slow",
            "speed_limit": 10,
            "start_fee": 10,
            "end_fee": 10,
        },
    ]

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["id", "type_name", "speed_limit", "start_fee", "end_fee"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for zone_type in zone_types:
            writer.writerow(zone_type)


def generate_zones(output_file: str) -> None:
    """
    Generate zones and save them to a CSV file.

    Parameters:
    output_file (str): The file path to save the generated CSV file.
    """
    zones = [
        {
            "zone_name": "Malmö C",
            "zone_type_id": 1,
            "city_id": 3,
            "boundary": "POLYGON((12.999047 55.60899, 12.999326 55.608445, 12.999219 55.608439, 12.99895 55.608984, 12.999047 55.60899))",
        },
        {
            "zone_name": "Möllevångstorget",
            "zone_type_id": 2,
            "city_id": 3,
            "boundary": "POLYGON((13.008059 55.59143, 13.008059 55.591518, 13.008478 55.591518, 13.008478 55.59143, 13.008059 55.59143))",
        },
        {
            "zone_name": "Triangeln Nord",
            "zone_type_id": 2,
            "city_id": 3,
            "boundary": "POLYGON((13.000329 55.594031, 13.000329 55.594225, 13.000581 55.594225, 13.000581 55.594031, 13.000329 55.594031))",
        },
        {
            "zone_name": "Stora pildammen",
            "zone_type_id": 3,
            "city_id": 3,
            "boundary": "POLYGON((12.998543 55.58732, 12.997727 55.589502, 12.996268 55.590036, 12.997084 55.591491, 12.994809 55.59183, 12.99232 55.590933, 12.994294 55.590206, 12.99365 55.589624, 12.996011 55.587756, 12.998114 55.587198, 12.998543 55.58732))",
        },
        {
            "zone_name": "Folkets park",
            "zone_type_id": 4,
            "city_id": 3,
            "boundary": "POLYGON((13.013241 55.595153, 13.013842 55.59525, 13.01573 55.594377, 13.014615 55.591733, 13.01204 55.592049, 13.011954 55.592364, 13.013241 55.595153))",
        },
    ]

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["zone_name", "zone_type_id", "city_id", "boundary"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for zone in zones:
            writer.writerow(zone)

def generate_users(
    num_users: int,
    output_file: str,
    female_first_names_file: str = "..../data/source/name_data/female-first-names.csv",
    male_first_names_file: str = "..../data/source/name_data/male-first-names.csv",
    last_names_file: str = "..../data/source/name_data/last-names.csv"
) -> None:
    """
    Generate a CSV file with random user data.

    Parameters:
    num_users (int): The number of users to generate.
    output_file (str): The file path to save the generated CSV file.
    female_first_names_file (str): The file path to the CSV file containing female first names.
    male_first_names_file (str): The file path to the CSV file containing male first names.
    last_names_file (str): The file path to the CSV file containing last names.

    The generated CSV file will have the following columns:
    - full_name: A randomly generated full name.
    - email: An email address based on the full name.
    - balance: A random balance, with one third of the accounts having 0.
    - use_prepay: A boolean indicating whether the user uses prepay.
    - created_at: A random timestamp from the last year.
    """
    # Read first names and last names from CSV files
    with open(female_first_names_file, "r") as f:
        female_first_names = [line.strip() for line in f]

    with open(male_first_names_file, "r") as f:
        male_first_names = [line.strip() for line in f]

    with open(last_names_file, "r") as f:
        last_names = [line.strip() for line in f]

    # Open the output CSV file
    with open(output_file, "w", newline="") as csvfile:
        fieldnames = [
            "id",
            "full_name",
            "email",
            "balance",
            "use_prepay",
            "created_at",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for _ in range(num_users):
            # Randomly choose either a female or male first name
            if random.choice([True, False]):
                first_name = random.choice(female_first_names)
            else:
                first_name = random.choice(male_first_names)

            last_name = random.choice(last_names)
            full_name = f"{first_name} {last_name}"
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"

            # Balance: one third of the accounts have 0, the rest random amount between 0 and 400
            balance = (
                0.00
                if random.random() < 0.33
                else round(random.uniform(0.01, 400.00), 2)
            )

            # Use prepay: half false, half true
            use_prepay = random.choice([True, False])

            # Created at: random timestamp from the last year
            now = datetime.now()
            past_year = now - timedelta(days=365)
            created_at = past_year + (now - past_year) * random.random()

            writer.writerow(
                {
                    "id": TSID.create().number,
                    "full_name": full_name,
                    "email": email,
                    "balance": balance,
                    "use_prepay": use_prepay,
                    "created_at": created_at.isoformat(),
                }
            )

def load_csv_data(file_path):
    """
    Load data from a CSV file and return it as a list of dictionaries.
    """
    with open(file_path, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]

def generate_trip_data(json_file, bikes_file, users_file, output_file: str) -> None:
    """
    Generate trip data based on the provided JSON data and save it to a CSV file.

    Parameters:
    json_file (str): The path to the JSON file containing route information.
    bikes_file (str): The path to the CSV file containing bike data.
    users_file (str): The path to the CSV file containing user data.
    output_file (str): The path to the output CSV file.
    """
    with open(json_file, "r") as jsonfile:
        data = json.load(jsonfile)

    bikes = load_csv_data(bikes_file)
    users = load_csv_data(users_file)

    fieldnames = [
        "bike_id",
        "user_id",
        "start_time",
        "end_time",
        "start_position",
        "end_position",
        "path_taken",
        "start_fee",
        "time_fee",
        "end_fee",
        "total_fee",
    ]

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for trip in data:
            # Randomm bike and user
            bike_id = random.choice(bikes)["id"]
            user_id = random.choice(users)["id"]

            # Extract route and 
            duration = trip["routes"][0]["duration"] / 2
            geometry = trip["routes"][0]["geometry"]
            waypoints = trip["waypoints"]

            # Generate random start_time within the last year
            now = datetime.now()
            past_year = now - timedelta(days=365)
            start_time = past_year + (now - past_year) * random.random()

            # Calculate end_time
            end_time = start_time + timedelta(seconds=duration)

            # Convert start_position and end_position to wkt
            start_position = Point(waypoints[0]["location"])
            end_position = Point(waypoints[1]["location"])
            start_position_wkt = dumps(start_position)
            end_position_wkt = dumps(end_position)

            # Convert path_taken to wkt
            coordinates = polyline.decode(geometry)
            path_taken = LineString([(coord[1], coord[0]) for coord in coordinates])
            path_taken_wkt = dumps(path_taken)

            # Generate fees
            start_fee = random.choice([5, 0])
            time_fee = (duration / 60) * 3
            end_fee = random.choice([10, 0])
            total_fee = start_fee + time_fee + end_fee

            # Write data to CSV
            writer.writerow(
                {
                    "bike_id": bike_id,
                    "user_id": user_id,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "start_position": start_position_wkt,
                    "end_position": end_position_wkt,
                    "path_taken": path_taken_wkt,
                    "start_fee": start_fee,
                    "time_fee": time_fee,
                    "end_fee": end_fee,
                    "total_fee": total_fee,
                }
            )

# Generates bike2bike status data

def generate_bike_2_bike_status(
    bike_ids: list[int],
    output_file: str
) -> None:
    """
    Generate a CSV file with semi random bike2bike status data.

    Parameters:
    bike_ids (list[int]): The list of bike IDs to generate statuses for.
    output_file (str): The file path to save the generated CSV file.
    """
    # Define the bike statuses with corresponding numbers
    bike_statuses = [
        (1, "AVAILABLE"),
        (2, "IN_USE"),
        (3, "CHARGING"),
        (4, "MAINTENANCE"),
        (5, "OUT_OF_SERVICE")
    ]

    # Open output CSV file
    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["bike_id", "status", "created_at", "updated_at"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for bike_id in bike_ids:
            # Randomize 60% to available, 0% to in use, 10% to charging, 5% to maintenance, 5% to out of service
            status = random.choices(
                bike_statuses,
                weights=[60, 0, 30, 5, 5],
                k=1
            )[0]

            # Generate random created_at timestamp from the last year
            now = datetime.now()
            past_year = now - timedelta(days=365)
            created_at = past_year + (now - past_year) * random.random()

            # Generate random updated_at from last 2 days
            updated_at = now - timedelta(days=random.uniform(0, 2))

            writer.writerow(
                {
                    "bike_id": bike_id,
                    "status": status[0],
                    "created_at": created_at,
                    "updated_at": updated_at
                }
            )

# Example usage
# So far only generates bikes without positions
# Will need to tie the bikes to bike routes and use last position of the route as last pos of bike

def generate_bikes(
    num_bikes: int,
    output_file: str,
) -> None:
    """
    Generate a CSV file with random bike data.

    Parameters:
    num_bikes (int): The number of bikes to generate.
    output_file (str): The file path to save the generated CSV file.
    """
    # open output CSV file
    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["id", "battery_lvl", "last_position", "city_id", "created_at"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(num_bikes):
            # Generate random bike ID
            bike_id = i + 1

            # Generate random battery level
            battery_lvl = random.randint(0, 100)

            # Leave last position empty
            last_position = "POINT(13.0038 55.6050)"

            # Generate random city ID
            city_id = 3

            # Generate random created_at timestamp from the last year
            now = datetime.now()
            past_year = now - timedelta(days=365)
            created_at = past_year + (now - past_year) * random.random()

            writer.writerow(
                {
                    "id": bike_id,
                    "battery_lvl": battery_lvl,
                    "last_position": last_position,
                    "city_id": city_id,
                    "created_at": created_at,
                }
            )

def generate_admins(output_file: str) -> None:
    """
    Generates a CSV file with admin data.

    Parameters:
    output_file (str): The file path to save the generated
    """
    admins = [
        {
            "id": 1,
            "full_name": "Johan Johansson",
            "email": "johan@Johansson.com"
        },
        {
            "id": 2,
            "full_name": "Anna Annasson",
            "email": "anna@annasson.com"
        },
        {
            "id": 3,
            "full_name": "Erik Eriksson",
            "email": "erik@eriksson.com"
        }
    ]

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["id", "full_name", "email"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for admin in admins:
            writer.writerow(admin)


def generate_admin_roles(output_file: str) -> None:
    """
    Generates a CSV file with admin role data.

    Parameters:
    output_file (str): The file path to save the generated
    """
    admin_roles = [
        {
            "id": 1,
            "role_name": "full_access",
        },
        {
            "id": 2,
            "role_name": "bike_maintenance",
        },
        {
            "id": 4,
            "role_name": "financial",
        },
        {
            "id": 5,
            "role_name": "marketing",
        },
        {
            "id": 6,
            "role_name": "customer_support",
        },
    ]

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["id", "role_name"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for admin_role in admin_roles:
            writer.writerow(admin_role)

def generate_admin_to_roles(output_file: str) -> None:
    """
    Generates a CSV file with admin to role data.

    Parameters:
    output_file (str): The file path to save the generated
    """
    admin_to_roles = [
        {
            "admin_id": 1,
            "role_id": 1,
        },
        {
            "admin_id": 2,
            "role_id": 2,
        },
        {
            "admin_id": 3,
            "role_id": 4,
        },
    ]

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["admin_id", "role_id"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for admin_to_role in admin_to_roles:
            writer.writerow(admin_to_role)

generate_users(100, '../data/generated/users.csv')

generate_bikes(100, "../data/generated/bikes.csv")

# bike_status generated manually
generate_bike_2_bike_status(list(range(1, 101)), "../data/generated/bike2bike_status.csv")

json_file_path = "../data/generated/bike_routes.json"
bikes_file_path = "../data/generated/bikes.csv"
users_file_path = "../data/generated/users.csv"
output_file_path = "../data/generated/trip_data.csv"
generate_trip_data(json_file_path, bikes_file_path, users_file_path, output_file_path)

generate_zone_types(output_file_path)
output_file_path = "../data/generated/zones.csv"
generate_zones(output_file_path)

generate_admins("../data/generated/admins.csv")
generate_admin_roles("../data/generated/admin_roles.csv")
generate_admin_to_roles("../data/generated/admin_to_roles.csv")
output_file_path = "../data/generated/zone_types.csv"
