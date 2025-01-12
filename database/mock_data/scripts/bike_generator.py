import csv
import random
from datetime import datetime, timedelta

from tsidpy import TSID

NUM_BIKES = 3000
OUTPUT_FILE = "../data/generated/bikes_gbg.csv"
NUM_LOW_ID = 0
RANDOM_AVAILABLE = True
IS_AVAILABLE = True
RANDOM_BATTERY_LVL = True
LAST_POSITION = "POINT(13.0038 55.6050)"
BATTERY_LVL = 100
CITY_ID = 1


def generate_bikes(
    output_file: str,
    num_bikes: int,
    random_available: bool = True,
    is_available: bool = True,
    random_battery_lvl: bool = True,
    battery_lvl: int = 100,
    last_position: str = "POINT(13.0038 55.6050)",
    city_id: int = 3,
) -> None:
    """
    Generate a CSV file with random bike data.

    Parameters:
    num_bikes (int): The number of bikes to generate.
    output_file (str): The file path to save the generated CSV file.
    """
    # open output CSV file
    with open(output_file, "a", newline="") as csvfile:
        fieldnames = [
            "id",
            "battery_lvl",
            "last_position",
            "city_id",
            "created_at",
            "is_available",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(num_bikes):
            # Generate random bike ID
            bike_id = TSID.create().number
            # if NUM_LOW_ID is over 0, generate low IDs first
            if NUM_LOW_ID > 0 and i < NUM_LOW_ID:
                bike_id = i + 1

            if random_battery_lvl:
                battery_lvl = random.randint(0, 100)

            if random_available:
                # 90% chance of bike being available
                is_available = random.choices([True, False], weights=[9, 1])[0]

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
                    "is_available": is_available,
                }
            )


generate_bikes(
    output_file=OUTPUT_FILE,
    num_bikes=NUM_BIKES,
    random_available=RANDOM_AVAILABLE,
    is_available=IS_AVAILABLE,
    random_battery_lvl=RANDOM_BATTERY_LVL,
    battery_lvl=BATTERY_LVL,
    last_position=LAST_POSITION,
    city_id=CITY_ID,
)
