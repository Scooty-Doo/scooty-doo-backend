import csv
import os
import tempfile

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
}

def read_start_positions(trip_files):
    """Read start positions from multiple trip files."""
    start_positions = []
    for trip_file in trip_files:
        with open(trip_file, encoding="utf-8") as trip_csv:
            trip_reader = csv.DictReader(trip_csv)
            start_positions.extend([row["start_position"] for row in trip_reader])
    return start_positions

def update_bike_positions(bike_file, start_positions):
    """Update bike positions based on start positions."""
    # Read bike data into memory
    with open(bike_file, encoding="utf-8") as bike_csv:
        bike_reader = csv.DictReader(bike_csv)
        bikes = list(bike_reader)
        fieldnames = bike_reader.fieldnames

    # Update bike positions
    for i, row in enumerate(bikes):
        if i < len(start_positions):
            row["last_position"] = start_positions[i]

    with open(bike_file, "w", newline="", encoding="utf-8") as output_csv:
        bike_writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
        bike_writer.writeheader()
        bike_writer.writerows(bikes)

def process_city(city_name, bike_file, trip_files):
    """Process bike positions for a specific city."""
    print(f"Processing {city_name}...")
    start_positions = read_start_positions(trip_files)
    update_bike_positions(bike_file, start_positions)
    print(f"Finished processing {city_name}.")

# Process each city
for city_name, files in cities.items():
    process_city(city_name, files["bike_file"], files["trip_files"])