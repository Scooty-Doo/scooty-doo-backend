import csv
import random
from datetime import datetime, timedelta

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
generate_bike_2_bike_status(list(range(1, 101)), "../data/generated/bike2bike_status.csv")