import csv
import random
from datetime import datetime, timedelta
from tsidpy import TSID

def generate_users(
    num_users: int,
    output_file: str,
    female_first_names_file: str = "../data/source/name_data/female-first-names.csv",
    male_first_names_file: str = "../data/source/name_data/male-first-names.csv",
    last_names_file: str = "../data/source/name_data/last-names.csv"
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

generate_users(100, '../data/generated/users.csv')