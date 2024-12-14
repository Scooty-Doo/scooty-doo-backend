"""Module for pydantic models"""

# pylint: disable=too-few-public-methods
import datetime

from pydantic import BaseModel, Field


class Bike(BaseModel):
    """Model for bike table in database"""

    id: int
    battery_level: int
    metadata: str  # JSON == string?
    position: str = Field(pattern=r"POINT\(\d{2}\.\d{4}\s\d{2}\.\d{4}\)")  # import some type?
    city: "City"
    status: str  # JSON == string?
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class PaymentProvider(BaseModel):
    """Model for payment provider table in database"""

    id: int
    provider_name: str
    metadata: str  # JSON
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class PaymentMethod(BaseModel):
    """Model for payment method table in database"""

    id: int
    user: "User"
    provider: PaymentProvider
    provider_specific_id: str
    is_active: bool
    is_default: bool
    metadata: str  # JSON
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class Trip(BaseModel):
    """Model for trip table in database"""

    id: int
    bike_id: int
    user_id: int
    start_time: datetime.datetime  # timestamp?
    end_time: datetime.datetime  # timestamp?
    start_position: list[float]  # import some type?
    end_position: list[float]  # import some type?
    path_taken: str  # Linestring - import some type?
    start_fee: float
    time_fee: float
    end_fee: float
    total_fee: float
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class Transaction(BaseModel):
    """Model for transaction table in database"""

    id: int
    user: "User"
    amount: float
    transtion_type: str
    transaction_description: str
    trip: Trip
    metadata: str  # JSON
    payment_method: PaymentMethod
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class User(BaseModel):
    """Model for user table in database"""

    id: int
    full_name: str
    email: str
    balance: float
    use_prepay: bool
    metadata: str
    payment_methods: list[PaymentMethod]  # Should work?
    trips: list[Trip]
    transactions: list[Transaction]
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class City(BaseModel):
    """Model for city table in database"""

    id: int
    city_name: str
    country_code: str
    c_location: str  # position
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class Zone(BaseModel):
    """Model for zone table in database"""

    id: int
    zone_name: str
    zone_type: "ZoneType"
    city: City
    boundary: str
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class ZoneType(BaseModel):
    """Model for zone type table in database"""

    id: int
    type_name: str
    speed_limit: int
    start_fee: float
    end_fee: float
    metadata: str  # JSON
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class AdminRoles(BaseModel):
    """Model for admin roles table in database"""

    id: int
    role_name: str
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class Admin:
    """Model for admin table in database"""

    id: int
    full_name: str
    email: str
    metadata: str  # JSON
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?
    roles: list[AdminRoles]
