"""Database script to load mock data into the database using SQLAlchemy."""

import asyncio
import csv
import json
from datetime import datetime
from decimal import Decimal as decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import settings
from api.db.database import sessionmanager
from api.models.db_models import (
    Admin,
    Admin2AdminRole,
    AdminRole,
    Bike,
    City,
    MapZone,
    PaymentProvider,
    Transaction,
    Trip,
    User,
    ZoneType,
)


async def load_mock_data():
    """Load all mock data into the database using SQLAlchemy."""

    # Initialize the database connection
    sessionmanager.init(settings.database_url)

    async with sessionmanager.session() as session:
        # First truncate all tables
        await truncate_tables(session)

        # Load data in order of dependencies
        await load_cities(session)
        await load_bikes(session)
        await load_users(session)
        await load_payment_providers(session)
        await load_trips(session)
        await load_zone_types(session)
        await load_map_zones(session)
        await load_admins_and_roles(session)
        await load_transactions(session)

        # Update all sequences to continue from the highest IDs
        await session.execute(text("SELECT setval('cities_id_seq', (SELECT MAX(id) FROM cities))"))
        await session.execute(text("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users))"))
        await session.execute(text("SELECT setval('bikes_id_seq', (SELECT MAX(id) FROM bikes))"))
        await session.execute(text("SELECT setval('trips_id_seq', (SELECT MAX(id) FROM trips))"))
        await session.execute(
            text("SELECT setval('zone_types_id_seq', (SELECT MAX(id) FROM zone_types))")
        )
        await session.execute(
            text("SELECT setval('admin_roles_id_seq', (SELECT MAX(id) FROM admin_roles))")
        )
        await session.execute(text("SELECT setval('admins_id_seq', (SELECT MAX(id) FROM admins))"))
        await session.execute(
            text("SELECT setval('transactions_id_seq', (SELECT MAX(id) FROM transactions))")
        )

        await session.commit()

    # Clean up database connection
    await sessionmanager.close()


async def truncate_tables(session: AsyncSession):
    """Truncate all tables in the correct order."""
    tables = [
        "cities",
        "users",
        "payment_providers",
        "bikes",
        "trips",
        "zone_types",
        "map_zones",
        "admins",
        "admin_roles",
        "admin_2_admin_roles",
        "transactions",
    ]

    for table in tables:
        await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))

    await session.commit()


async def load_cities(session: AsyncSession):
    """Load cities from CSV."""
    with open("database/mock_data/data/generated/cities.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            city = City(
                id=int(row["id"]),
                city_name=row["city_name"],
                country_code=row["country_code"],
                c_location=f"SRID=4326;{row['c_location']}",
            )
            session.add(city)
    await session.flush()


async def load_users(session: AsyncSession):
    """Load users from CSV."""
    with open("database/mock_data/data/generated/users_cleaned.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            user = User(
                id=int(row["id"]),
                full_name=row["full_name"],
                email=row["email"],
                balance=row["balance"],
                use_prepay=row["use_prepay"].lower() == "true",
                created_at=datetime.fromisoformat(row["created_at"]),
                github_login=row["github_login"],
            )
            session.add(user)
    await session.flush()


async def load_payment_providers(session: AsyncSession):
    """Load payment providers from JSON."""
    with open(
        "database/mock_data/data/generated/payment_providers.json", encoding="utf-8"
    ) as jsonfile:
        data = json.load(jsonfile)
        for provider in data["payment_providers"]:
            pp = PaymentProvider(
                provider_name=provider["provider_name"], metadata=provider["metadata"]
            )
            session.add(pp)
    await session.flush()


async def load_bikes(session: AsyncSession):
    """Load bikes from CSV."""
    with open(
        "database/mock_data/data/generated/bikes_with_updated_positions.csv", encoding="utf-8"
    ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            bike = Bike(
                id=int(row["id"]),
                battery_lvl=int(row["battery_lvl"]),
                last_position=f"SRID=4326;{row['last_position']}",
                city_id=int(row["city_id"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                is_available=row["is_available"].lower() == "true",
            )
            session.add(bike)
    await session.flush()

    # Update the bikes sequence to continue from the highest ID
    await session.execute(text("SELECT setval('bikes_id_seq', (SELECT MAX(id) FROM bikes))"))
    await session.flush()


async def load_trips(session: AsyncSession):
    """Load trips from CSV."""
    with open(
        "database/mock_data/data/generated/trip_data_with_ids.csv", encoding="utf-8"
    ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            trip = Trip(
                id=int(row["id"]),
                bike_id=int(row["bike_id"]),
                user_id=int(row["user_id"]),
                start_time=datetime.fromisoformat(row["start_time"]),
                end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
                start_position=f"SRID=4326;{row['start_position']}",
                end_position=f"SRID=4326;{row['end_position']}" if row["end_position"] else None,
                path_taken=f"SRID=4326;{row['path_taken']}" if row["path_taken"] else None,
                start_fee=float(row["start_fee"]),
                time_fee=float(row["time_fee"]),
                end_fee=float(row["end_fee"]),
                total_fee=float(row["total_fee"]),
            )
            session.add(trip)
    await session.flush()


async def load_zone_types(session: AsyncSession):
    """Load zone types from CSV."""
    with open("database/mock_data/data/generated/zone_types.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            zone_type = ZoneType(
                id=int(row["id"]),
                type_name=row["type_name"],
                speed_limit=int(row["speed_limit"]),
                start_fee=float(row["start_fee"]),
                end_fee=float(row["end_fee"]),
            )
            session.add(zone_type)
    await session.flush()


async def load_map_zones(session: AsyncSession):
    """Load map zones from CSV."""
    with open("database/mock_data/data/generated/map_zones.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            map_zone = MapZone(
                zone_name=row["zone_name"],
                zone_type_id=int(row["zone_type_id"]),
                city_id=int(row["city_id"]),
                boundary=f"SRID=4326;{row['boundary']}",
            )
            session.add(map_zone)
    await session.flush()


async def load_admins_and_roles(session: AsyncSession):
    """Load admins, roles and their relationships."""
    # Load roles first
    with open("database/mock_data/data/generated/admin_roles.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            role = AdminRole(id=int(row["id"]), role_name=row["role_name"])
            session.add(role)
    await session.flush()

    # Load admins
    with open("database/mock_data/data/generated/admins.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            admin = Admin(id=int(row["id"]), full_name=row["full_name"], email=row["email"], github_login=row['github_login'])
            session.add(admin)
    await session.flush()

    # Load admin-role relationships
    with open("database/mock_data/data/generated/admin_to_roles.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            admin_role = Admin2AdminRole(admin_id=int(row["admin_id"]), role_id=int(row["role_id"]))
            session.add(admin_role)
    await session.flush()


async def load_transactions(session: AsyncSession):
    """Load transactions from CSV."""
    with open("database/mock_data/data/generated/transactions.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, skipinitialspace=True)  # Skip spaces after commas
        for row in reader:
            transaction = Transaction(
                id=int(row["id"]),
                user_id=int(row["user_id"]),
                trip_id=int(row["trip_id"])
                if row["trip_id"] and row["trip_id"].lower() != "null"
                else None,
                amount=decimal(str(row["amount"])),  # Use Decimal for money
                transaction_type=row["transaction_type"],
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            )
            session.add(transaction)
        await session.flush()


if __name__ == "__main__":
    asyncio.run(load_mock_data())
