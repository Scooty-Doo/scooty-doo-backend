import csv

def generate_admins(output_file: str) -> None:
    """
    Generates a CSV file with admin data.

    Parameters:
    output_file (str): The file path to save the generated
    """
    admins = [
        {
            "id": 1,
            "full_name": "Johan Johansson",
            "email": "johan@Johansson.com"
        },
        {
            "id": 2,
            "full_name": "Anna Annasson",
            "email": "anna@annasson.com"
        },
        {
            "id": 3,
            "full_name": "Erik Eriksson",
            "email": "erik@eriksson.com"
        }
    ]

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["id", "full_name", "email"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for admin in admins:
            writer.writerow(admin)


def generate_admin_roles(output_file: str) -> None:
    """
    Generates a CSV file with admin role data.

    Parameters:
    output_file (str): The file path to save the generated
    """
    admin_roles = [
        {
            "id": 1,
            "role_name": "full_access",
        },
        {
            "id": 2,
            "role_name": "bike_maintenance",
        },
        {
            "id": 4,
            "role_name": "financial",
        },
        {
            "id": 5,
            "role_name": "marketing",
        },
        {
            "id": 6,
            "role_name": "customer_support",
        },
    ]

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["id", "role_name"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for admin_role in admin_roles:
            writer.writerow(admin_role)

def generate_admin_to_roles(output_file: str) -> None:
    """
    Generates a CSV file with admin to role data.

    Parameters:
    output_file (str): The file path to save the generated
    """
    admin_to_roles = [
        {
            "admin_id": 1,
            "role_id": 1,
        },
        {
            "admin_id": 2,
            "role_id": 2,
        },
        {
            "admin_id": 3,
            "role_id": 4,
        },
    ]

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["admin_id", "role_id"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for admin_to_role in admin_to_roles:
            writer.writerow(admin_to_role)

generate_admins("../generated_data/admins.csv")
generate_admin_roles("../generated_data/admin_roles.csv")
generate_admin_to_roles("../generated_data/admin_to_roles.csv")