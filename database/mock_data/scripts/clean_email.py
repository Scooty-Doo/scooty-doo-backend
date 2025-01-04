import csv


def clean_email(email: str) -> str:
    """Clean email by replacing spaces and Swedish characters."""
    return email.lower().replace(" ", ".").replace("å", "a").replace("ä", "a").replace("ö", "o")

def extract_github_login(email: str) -> str:
    """Extract the part before @ as github login."""
    return email.split("@")[0].replace(".", "-")

def add_github_login():
    """Add github_login column based on email."""
    rows = []

    with open("../data/generated/users_cleaned.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames + ["github_login"]

        for row in reader:
            row["github_login"] = extract_github_login(row["email"])
            rows.append(row)

    with open("../data/generated/users_cleaned.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def dots_to_hyphen_login():
    """Update github_login column to use dashes instead of dots."""
    rows = []

    with open("../data/generated/users_cleaned.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames

        for row in reader:
            row["github_login"] = row["github_login"].replace(".", "-")
            rows.append(row)

    with open("../data/generated/users_cleaned.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def clean_csv():
    rows = []

    with open("../data/generated/users.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        # Store field names for writing
        fieldnames = reader.fieldnames

        for row in reader:
            # Clean email while preserving other fields
            row["email"] = clean_email(row["email"])
            rows.append(row)

    with open("../data/generated/users_cleaned.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    # clean_csv()
    # add_github_login()
    dots_to_hyphen_login()
