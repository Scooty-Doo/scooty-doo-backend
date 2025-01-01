import csv

bike_file = "../data/generated/bikes_with_availability.csv"
trip_file = "../data/generated/trip_data.csv"
output_file = "../data/generated/bikes_with_updated_positions.csv"

with open(trip_file) as trip_csv:
    trip_reader = csv.DictReader(trip_csv)
    start_positions = [row["start_position"] for row in trip_reader]

with open(bike_file) as bike_csv, open(output_file, "w", newline="") as output_csv:
    bike_reader = csv.DictReader(bike_csv)
    fieldnames = bike_reader.fieldnames
    bike_writer = csv.DictWriter(output_csv, fieldnames=fieldnames)

    bike_writer.writeheader()

    for i, row in enumerate(bike_reader):
        if i < len(start_positions):
            row["last_position"] = start_positions[i]
        bike_writer.writerow(row)
