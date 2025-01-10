import csv
import os
import tempfile
import random
from shapely.wkt import loads

cities = {
    "malmo": {
        "bike_file": "../data/generated/bikes_malmo.csv",
        "trip_files": [
            "../data/generated/trips_malmo_1.csv",
            "../data/generated/trips_malmo_2.csv",
            "../data/generated/trips_malmo_3.csv",
            "../data/generated/trips_malmo_4.csv",
            "../data/generated/trips_malmo_5.csv",
        ]
    },
    "stockholm": {
        "bike_file": "../data/generated/bikes_stockholm.csv",
        "trip_files": [
            "../data/generated/trips_stockholm_1.csv",
        ]
    },
    "gothenburg": {
        "bike_file": "../data/generated/bikes_gothenburg.csv",
        "trip_files": [
            "../data/generated/trips_gothenburg_1.csv",
        ]
    },
}
def read_start_positions(trip_files):
    """Read start positions and paths from multiple trip files."""
    start_positions = []
    paths = []
    for trip_file in trip_files:
        with open(trip_file, encoding="utf-8") as trip_csv:
            trip_reader = csv.DictReader(trip_csv)
            for row in trip_reader:
                start_positions.append(row["start_position"])
                paths.append(row["path_taken"])
    return start_positions, paths

def update_bike_positions(bike_file, start_positions, paths):
    """Update bike positions based on start positions and paths."""
    with open(bike_file, encoding="utf-8") as bike_csv:
        bike_reader = csv.DictReader(bike_csv)
        bikes = list(bike_reader)
        fieldnames = bike_reader.fieldnames

    for i, row in enumerate(bikes):
        if i < len(start_positions):
            row["last_position"] = start_positions[i]
        else:
            path_wkt = random.choice(paths)
            path = loads(path_wkt)
            point = path.interpolate(random.uniform(0, path.length))
            row["last_position"] = point.wkt

    with tempfile.NamedTemporaryFile('w', delete=False, newline="", encoding="utf-8") as temp_csv:
        bike_writer = csv.DictWriter(temp_csv, fieldnames=fieldnames)
        bike_writer.writeheader()
        bike_writer.writerows(bikes)
        temp_file_name = temp_csv.name

    os.replace(temp_file_name, bike_file)

def process_city(city_name, bike_file, trip_files):
    """Process bike positions for a specific city."""
    print(f"Processing {city_name}...")
    start_positions, paths = read_start_positions(trip_files)
    update_bike_positions(bike_file, start_positions, paths)
    print(f"Finished processing {city_name}.")

for city_name, files in cities.items():
    process_city(city_name, files["bike_file"], files["trip_files"])