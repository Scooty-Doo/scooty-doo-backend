from datetime import datetime, timezone
from sqlalchemy import (
    CHAR, Boolean, CheckConstraint, DateTime, ForeignKey,
    Integer, Numeric, Text, Table, Column, func, BigInteger
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

class Base(DeclarativeBase):
    """Base database model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=func.now()
    )

class City(Base):
    """City database model."""
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_name: Mapped[str] = mapped_column(Text, nullable=False)
    country_code: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    c_location: Mapped[Geometry] = mapped_column(Geometry('POINT', srid=4326), nullable=False)

    # Relationships
    bikes: Mapped[list["Bike"]] = relationship(back_populates="city")
    map_zones: Mapped[list["MapZone"]] = relationship(back_populates="city")

class User(Base):
    """User database model."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00)
    use_prepay: Mapped[bool] = mapped_column(Boolean, default=False)
    meta_data: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Relationships
    payment_methods: Mapped[list["PaymentMethod"]] = relationship(back_populates="user")
    trips: Mapped[list["Trip"]] = relationship(back_populates="user")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")

class PaymentProvider(Base):
    """Payment provider database model."""
    __tablename__ = "payment_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    meta_data: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Relationships
    payment_methods: Mapped[list["PaymentMethod"]] = relationship(back_populates="provider")

class PaymentMethod(Base):
    """Payment method database model."""
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("payment_providers.id"),
        nullable=False
    )
    provider_specific_id: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    meta_data: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="payment_methods")
    provider: Mapped["PaymentProvider"] = relationship(back_populates="payment_methods")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="payment_method")

# class BikeStatus(Base):
#     """Bike status database model."""
#     __tablename__ = "bike_status"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     status_code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
#     meta_data: Mapped[dict] = mapped_column(JSONB, nullable=True)

#     # Relationships
#     bikes: Mapped[list["Bike"]] = relationship(
#         secondary="bike_2_bike_status",
#         back_populates="statuses"
#     )

class Bike(Base):
    """Bike database model."""
    __tablename__ = "bikes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    battery_lvl: Mapped[int] = mapped_column(Integer, nullable=False)
    last_position: Mapped[Geometry] = mapped_column(Geometry('POINT', srid=4326), nullable=True)
    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id"),
        nullable=False
    )
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    meta_data: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Relationships
    city: Mapped["City"] = relationship(back_populates="bikes")
    # statuses: Mapped[list["BikeStatus"]] = relationship(
    #     secondary="bike_2_bike_status",
    #     back_populates="bikes"
    # )
    trips: Mapped[list["Trip"]] = relationship(back_populates="bike")

    __table_args__ = (
        CheckConstraint('battery_lvl >= 0 AND battery_lvl <= 100', name='battery_level_check'),
    )

class Trip(Base):
    """Trip database model."""
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    bike_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("bikes.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    start_position: Mapped[Geometry] = mapped_column(Geometry('POINT', srid=4326), nullable=False)
    end_position: Mapped[Geometry] = mapped_column(Geometry('POINT', srid=4326), nullable=True)
    path_taken: Mapped[Geometry] = mapped_column(Geometry('LINESTRING', srid=4326), nullable=True)
    start_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    time_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    end_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    total_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)

    # Relationships
    bike: Mapped["Bike"] = relationship(back_populates="trips")
    user: Mapped["User"] = relationship(back_populates="trips")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="trip")

class ZoneType(Base):
    """Zone type database model."""
    __tablename__ = "zone_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    speed_limit: Mapped[int] = mapped_column(Integer, nullable=True)
    start_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    end_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    meta_data: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Relationships
    zones: Mapped[list["MapZone"]] = relationship(back_populates="zone_type")

class MapZone(Base):
    """Map zone database model."""
    __tablename__ = "map_zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    zone_name: Mapped[str] = mapped_column(Text, nullable=False)
    zone_type_id: Mapped[int] = mapped_column(
        ForeignKey("zone_types.id"),
        nullable=False
    )
    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id"),
        nullable=False
    )
    boundary: Mapped[Geometry] = mapped_column(Geometry('POLYGON', srid=4326), nullable=False)

    # Relationships
    zone_type: Mapped["ZoneType"] = relationship(back_populates="zones")
    city: Mapped["City"] = relationship(back_populates="map_zones")

class Transaction(Base):
    """Transaction database model."""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(
        Text,
        CheckConstraint("transaction_type IN ('trip', 'deposit', 'refund')"),
        nullable=False
    )
    transaction_description: Mapped[str] = mapped_column(Text, nullable=True)
    trip_id: Mapped[int] = mapped_column(
        ForeignKey("trips.id"),
        nullable=True
    )
    payment_method_id: Mapped[int] = mapped_column(
        ForeignKey("payment_methods.id"),
        nullable=True
    )
    meta_data: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="transactions")
    trip: Mapped["Trip"] = relationship(back_populates="transactions")
    payment_method: Mapped["PaymentMethod"] = relationship(back_populates="transactions")

# class Bike2BikeStatus(Base):
#     """Association table for Bike and BikeStatus."""
#     __tablename__ = "bike_2_bike_status"

#     bike_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("bikes.id"), primary_key=True
#     )
#     status_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("bike_status.id"), primary_key=True
#     )

class Admin(Base):
    """Admin database model."""
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    meta_data: Mapped[dict] = mapped_column(JSONB, nullable=True)

    roles: Mapped[list["AdminRole"]] = relationship(
        secondary="admin_2_admin_roles",
        back_populates="admins"
    )

class AdminRole(Base):
    """Admin role database model."""
    __tablename__ = "admin_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    admins: Mapped[list["Admin"]] = relationship(
        secondary="admin_2_admin_roles",
        back_populates="roles"
    )
class Admin2AdminRole(Base):
    """Association table for Admin and AdminRole."""
    __tablename__ = "admin_2_admin_roles"

    admin_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("admins.id"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("admin_roles.id"), primary_key=True
    )