import csv
import random
from datetime import datetime, timedelta

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

generate_bikes(100, "../data/generated/bikes.csv")