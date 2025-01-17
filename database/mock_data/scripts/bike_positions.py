import csv
import os
import random
import tempfile

from shapely import Point
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
        ],
    },
    "stockholm": {
        "bike_file": "../data/generated/bikes_stockholm.csv",
        "trip_files": [
            "../data/generated/trips_stockholm_1.csv",
        ],
    },
    "gothenburg": {
        "bike_file": "../data/generated/bikes_gothenburg.csv",
        "trip_files": [
            "../data/generated/trips_gothenburg_1.csv",
        ],
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

    with tempfile.NamedTemporaryFile("w", delete=False, newline="", encoding="utf-8") as temp_csv:
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


def move_bikes_to_zone(zone_type_id: int, bikes_per_zone: int):
    """Move bikes to a specific zone."""
    
    # Read map_zones and identify all zones of the specified zone_type_id
    with open("../data/generated/map_zones.csv", encoding="utf-8") as map_zones_csv:
        map_zones_reader = csv.DictReader(map_zones_csv)
        map_zones = [row for row in map_zones_reader if int(row['zone_type_id']) == zone_type_id]

    # Read bikes
    with open("../data/generated/bikes_malmo.csv", encoding="utf-8") as bikes_csv:
        bikes_reader = csv.DictReader(bikes_csv)
        bikes = list(bikes_reader)

    moved_bikes = set()  # Track moved bikes

    # Move bikes to zones
    for zone in map_zones:
        boundary = loads(zone['boundary'])
        bike_count = 0  # Reset bike count for each zone
        for i in range(10, len(bikes), 5):
            if bike_count >= bikes_per_zone:
                break
            bike = bikes[i]
            if bike['id'] in moved_bikes:
                continue  # Skip bikes that have already been moved
            minx, miny, maxx, maxy = boundary.bounds
            while True:
                pnt = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
                if boundary.contains(pnt):
                    break
            bike['last_position'] = f"POINT ({pnt.x} {pnt.y})"
            moved_bikes.add(bike['id'])  # Mark bike as moved
            bike_count += 1
            print(f"Moved bike {bike['id']} to {bike['last_position']} in zone {zone['zone_name']}")

    # Write updated positions to the file
    with open("../data/generated/bikes_malmo.csv", mode="w", encoding="utf-8", newline="") as bikes_csv:
        fieldnames = bikes_reader.fieldnames
        writer = csv.DictWriter(bikes_csv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bikes)

# Move bikes to parking and charging (20 bikes each)
# move_bikes_to_zone(1, 20)
# move_bikes_to_zone(2, 20)

# Set bike positions according to trip data
# for city_name, files in cities.items():
#     process_city(city_name, files["bike_file"], files["trip_files"])
