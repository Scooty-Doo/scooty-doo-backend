import csv
import json
import asyncio
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..api.db.database import sessionmanager
from ..api.models.db_models import (
    City, User, PaymentProvider, Bike, Trip, ZoneType, MapZone,
    Admin, AdminRole, Admin2AdminRole
)
from config import settings

async def load_mock_data():
    """Load all mock data into the database using SQLAlchemy."""
    
    # Initialize the database connection
    sessionmanager.init(settings.database_url)
    
    async with sessionmanager.session() as session:
        # First truncate all tables
        await truncate_tables(session)
        
        # Load data in order of dependencies
        await load_cities(session)
        await load_users(session)
        await load_payment_providers(session)
        # await load_bike_status(session)
        await load_bikes(session)
        # await load_bike2bike_status(session)
        await load_trips(session)
        await load_zone_types(session)
        await load_map_zones(session)
        await load_admins_and_roles(session)
        
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
        "admin_2_admin_roles"
    ]
    
    for table in tables:
        await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
    
    await session.commit()

async def load_cities(session: AsyncSession):
    """Load cities from CSV."""
    with open('app/database/mock_data/data/generated/cities.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            city = City(
                id=int(row['id']),
                city_name=row['city_name'],
                country_code=row['country_code'],
                c_location=f"SRID=4326;{row['c_location']}"
            )
            session.add(city)
    await session.flush()

async def load_users(session: AsyncSession):
    """Load users from CSV."""
    with open('app/database/mock_data/data/generated/users.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            user = User(
                id=int(row['id']),
                full_name=row['full_name'],
                email=row['email'],
                balance=row['balance'],
                use_prepay=row['use_prepay'].lower() == 'true',
                created_at=datetime.fromisoformat(row['created_at'])
            )
            session.add(user)
    await session.flush()

async def load_payment_providers(session: AsyncSession):
    """Load payment providers from JSON."""
    with open('app/database/mock_data/data/generated/payment_providers.json', 'r') as jsonfile:
        data = json.load(jsonfile)
        for provider in data['payment_providers']:
            pp = PaymentProvider(
                provider_name=provider['provider_name'],
                metadata=provider['metadata']
            )
            session.add(pp)
    await session.flush()

# async def load_bike_status(session: AsyncSession):
#     """Load bike status from JSON."""
#     with open('app/database/mock_data/data/generated/bike_status.json', 'r') as jsonfile:
#         data = json.load(jsonfile)
#         for status in data['bike_status']:
#             bs = BikeStatus(
#                 id=status['id'],
#                 status_code=status['status_code'],
#                 metadata=status['metadata']
#             )
#             session.add(bs)
#     await session.flush()

async def load_bikes(session: AsyncSession):
    """Load bikes from CSV."""
    with open('app/database/mock_data/data/generated/bikes_with_availability.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            bike = Bike(
                id=int(row['id']),
                battery_lvl=int(row['battery_lvl']),
                last_position=f"SRID=4326;{row['last_position']}",
                city_id=int(row['city_id']),
                created_at=datetime.fromisoformat(row['created_at']),
                is_available=row['is_available'].lower() == 'true'
            )
            session.add(bike)
    await session.flush()

# async def load_bike2bike_status(session: AsyncSession):
#     """Load bike to bike status mappings from CSV."""
#     with open('app/database/mock_data/data/generated/bike2bike_status.csv', 'r') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             b2bs = Bike2BikeStatus(
#                 bike_id=int(row['bike_id']),
#                 status_id=int(row['status']),
#                 created_at=datetime.fromisoformat(row['created_at']),
#                 updated_at=datetime.fromisoformat(row['updated_at'])
#             )
#             session.add(b2bs)
#     await session.flush()

async def load_trips(session: AsyncSession):
    """Load trips from CSV."""
    with open('app/database/mock_data/data/generated/trip_data.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            trip = Trip(
                bike_id=int(row['bike_id']),
                user_id=int(row['user_id']),
                start_time=datetime.fromisoformat(row['start_time']),
                end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                start_position=f"SRID=4326;{row['start_position']}",
                end_position=f"SRID=4326;{row['end_position']}" if row['end_position'] else None,
                path_taken=f"SRID=4326;{row['path_taken']}" if row['path_taken'] else None,
                start_fee=float(row['start_fee']),
                time_fee=float(row['time_fee']),
                end_fee=float(row['end_fee']),
                total_fee=float(row['total_fee'])
            )
            session.add(trip)
    await session.flush()

async def load_zone_types(session: AsyncSession):
    """Load zone types from CSV."""
    with open('app/database/mock_data/data/generated/zone_types.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            zone_type = ZoneType(
                id=int(row['id']),
                type_name=row['type_name'],
                speed_limit=int(row['speed_limit']),
                start_fee=float(row['start_fee']),
                end_fee=float(row['end_fee'])
            )
            session.add(zone_type)
    await session.flush()

async def load_map_zones(session: AsyncSession):
    """Load map zones from CSV."""
    with open('app/database/mock_data/data/generated/map_zones.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            map_zone = MapZone(
                zone_name=row['zone_name'],
                zone_type_id=int(row['zone_type_id']),
                city_id=int(row['city_id']),
                boundary=f"SRID=4326;{row['boundary']}"
            )
            session.add(map_zone)
    await session.flush()

async def load_admins_and_roles(session: AsyncSession):
    """Load admins, roles and their relationships."""
    # Load roles first
    with open('app/database/mock_data/data/generated/admin_roles.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            role = AdminRole(
                id=int(row['id']),
                role_name=row['role_name']
            )
            session.add(role)
    await session.flush()
    
    # Load admins
    with open('app/database/mock_data/data/generated/admins.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            admin = Admin(
                id=int(row['id']),
                full_name=row['full_name'],
                email=row['email']
            )
            session.add(admin)
    await session.flush()
    
    # Load admin-role relationships
    with open('app/database/mock_data/data/generated/admin_to_roles.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            admin_role = Admin2AdminRole(
                admin_id=int(row['admin_id']),
                role_id=int(row['role_id'])
            )
            session.add(admin_role)
    await session.flush()

if __name__ == "__main__":
    asyncio.run(load_mock_data()) 