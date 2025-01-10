import csv
import json
import random
from datetime import datetime, timedelta
from shapely.geometry import Point, LineString
from shapely.wkt import dumps
import polyline
from tsidpy import TSID

trip_packages = [ 
{
"json_file_path" : "../data/source/routes/malmo_routes_1.json",
"bikes_file_path" : "../data/generated/bikes_malmo.csv",
"users_file_path" : "../data/generated/users.csv",
"output_file_path" : "../data/generated/trips_malmo_1.csv",
}, {
"json_file_path" : "../data/source/routes/malmo_routes_2.json",
"bikes_file_path" : "../data/generated/bikes_malmo.csv",
"users_file_path" : "../data/generated/users.csv",
"output_file_path" : "../data/generated/trips_malmo_2.csv",
},
{
"json_file_path" : "../data/source/routes/malmo_routes_3.json",
"bikes_file_path" : "../data/generated/bikes_malmo.csv",
"users_file_path" : "../data/generated/users.csv",
"output_file_path" : "../data/generated/trips_malmo_3.csv",
},
{
"json_file_path" : "../data/source/routes/malmo_routes_4.json",
"bikes_file_path" : "../data/generated/bikes_malmo.csv",
"users_file_path" : "../data/generated/users.csv",
"output_file_path" : "../data/generated/trips_malmo_4.csv",
},
{
"json_file_path" : "../data/source/routes/malmo_routes_5.json",
"bikes_file_path" : "../data/generated/bikes_malmo.csv",
"users_file_path" : "../data/generated/users.csv",
"output_file_path" : "../data/generated/trips_malmo_5.csv",
},
{
"json_file_path" : "../data/source/routes/stockholm_routes_1.json",
"bikes_file_path" : "../data/generated/bikes_stockholm.csv",
"users_file_path" : "../data/generated/users.csv",
"output_file_path" : "../data/generated/trips_stockholm_1.csv",
},]

def load_csv_data(file_path):
    """
    Load data from a CSV file and return it as a list of dictionaries.
    """
    with open(file_path, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]
def generate_trip_data(json_file_path: str, bikes_file_path: str, users_file_path: str, output_file_path: str) -> None:
    """
    Generate trip data based on the provided JSON data and save it to a CSV file.

    Parameters:
    json_file_path (str): The path to the JSON file containing route information.
    bikes_file_path (str): The path to the CSV file containing bike data.
    users_file_path (str): The path to the CSV file containing user data.
    output_file_path (str): The path to the output CSV file.
    """
    with open(json_file_path, "r") as jsonfile:
        data = json.load(jsonfile)

    bikes = load_csv_data(bikes_file_path)
    users = load_csv_data(users_file_path)

    fieldnames = [
        "id",
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

    with open(output_file_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for trip in data:
            # Random bike and user
            trip_id = TSID.create().number
            bike_id = random.choice(bikes)["id"]
            user_id = random.choice(users)["id"]

            # Extract route and duration
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
                    "id": trip_id,
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


for trip_package in trip_packages:
    generate_trip_data(**trip_package)