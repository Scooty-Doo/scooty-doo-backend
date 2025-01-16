import csv
import datetime
import random
import re

from tsidpy import TSID


def load_names(
    female_path: str, male_path: str, last_name_path: str
) -> tuple[list[str], list[str], list[str]]:
    """Load name data from CSV files."""

    def read_csv(path: str) -> list[str]:
        with open(path) as f:
            return [row[0] for row in csv.reader(f)]

    female_names = read_csv(female_path)
    male_names = read_csv(male_path)
    last_names = read_csv(last_name_path)
    return female_names, male_names, last_names


def clean_string(input_str: str) -> str:
    """Clean string by replacing special characters with their base letter and removing
    non-alphanumeric characters."""
    cleaned = input_str.lower()
    cleaned = re.sub(r"[åäáàâã]", "a", cleaned)
    cleaned = re.sub(r"[ëéèêẽ]", "e", cleaned)
    cleaned = re.sub(r"[ïíìîĩ]", "i", cleaned)
    cleaned = re.sub(r"[öóòôõ]", "o", cleaned)
    cleaned = re.sub(r"[üúùûũ]", "u", cleaned)
    return cleaned


def clean_email_name(name: str) -> str:
    """Clean name for email use."""
    cleaned = clean_string(name)
    cleaned = re.sub(r"[^a-z0-9]", "", cleaned)
    return cleaned


def clean_github_login(login: str) -> str:
    """Clean GitHub login to match requirements:
    - Only alphanumeric and single hyphens
    - Cannot start/end with hyphen
    - Length 1-39 chars
    """
    cleaned = clean_string(login)
    cleaned = re.sub(r"[^a-z0-9-]", "-", cleaned)
    cleaned = re.sub(r"-+", "-", cleaned)
    cleaned = cleaned.strip("-")
    cleaned = cleaned[:39]
    return cleaned


def generate_random_date(start_date: datetime.datetime) -> datetime.datetime:
    """Generate a random datetime within the last year."""
    end_date = datetime.datetime.now()
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    # Add random time
    random_time = datetime.timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
        microseconds=random.randint(0, 999999),
    )
    return random_date + random_time


def generate_user_data(
    female_names: list[str], male_names: list[str], last_names: list[str], user_id: int
) -> dict:
    """Generate a single user's data."""
    is_female = random.random() < 0.5
    first_name = random.choice(female_names if is_female else male_names)
    last_name = random.choice(last_names)
    full_name = f"{first_name} {last_name}"

    email_first = clean_email_name(first_name)
    email_last = clean_email_name(last_name)
    email = f"{email_first}.{email_last}.{user_id}@example.com"

    github_login = clean_github_login(f"{last_name}{user_id}")

    use_prepay = random.random() < 0.8
    balance = round(random.uniform(-30, 400) if use_prepay else random.uniform(-200, 10), 2)

    start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    created_at = generate_random_date(start_date)

    return {
        "id": str(user_id),
        "full_name": full_name,
        "email": email,
        "balance": balance,
        "use_prepay": use_prepay,
        "created_at": created_at.isoformat(),
        "github_login": github_login,
    }


def get_fixed_users() -> list[dict]:
    """Return the two fixed users with predefined values."""
    fixed_date = "2024-11-03T07:15:11.131054"
    return [
        {
            "id": "1",
            "full_name": "ScootyPrepaidson",
            "email": "scooty@prepay.com",
            "balance": 65.00,
            "use_prepay": True,
            "created_at": fixed_date,
            "github_login": "scooty",
        },
        {
            "id": "2",
            "full_name": "ScootySubscriptson",
            "email": "scootysubbidoo@subscript.com",
            "balance": -30.00,
            "use_prepay": False,
            "created_at": fixed_date,
            "github_login": "scootysubbidoo",
        },
        {
            "id": "3",
            "full_name": "ScootyPoorson",
            "email": "scootypoor@prepay.com",
            "balance": -200.00,
            "use_prepay": True,
            "created_at": fixed_date,
            "github_login": "scootypoor",
        },
    ]


def generate_users(
    num_users: int, output_path: str, female_path: str, male_path: str, last_name_path: str
):
    """Generate specified number of users and write to CSV."""
    # Load name data
    female_names, male_names, last_names = load_names(female_path, male_path, last_name_path)

    # Define CSV fields
    fields = ["id", "full_name", "email", "balance", "use_prepay", "created_at", "github_login"]

    # Generate and write user data
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        # Write the two fixed users first
        fixed_users = get_fixed_users()
        for user in fixed_users:
            writer.writerow(user)

        # Generate remaining users with sequential IDs starting from 3
        for _user in range(4, num_users + 1):
            tsid_number = TSID.create().number
            max_safe_integer = 9007199254740991
            user_id = tsid_number % max_safe_integer
            user_data = generate_user_data(female_names, male_names, last_names, user_id)
            writer.writerow(user_data)


# Example usage
if __name__ == "__main__":
    # Set paths
    female_path = "../data/source/name_data/female-first-names.csv"
    male_path = "../data/source/name_data/male-first-names.csv"
    last_name_path = "../data/source/name_data/last-names.csv"
    output_path = "../data/generated/users.csv"

    # Generate 10000 users
    generate_users(10000, output_path, female_path, male_path, last_name_path)
