from pydantic import BaseModel
import datetime

class Bike(BaseModel):
    id: int
    battery_level: int
    metadata: str # JSON == string?
    position: list[float] # import some type?
    city: "City"
    status: str # JSON == string?
    created_at: datetime.datetime # timestamp?
    updated_at: datetime.datetime # timestamp?

class PaymentProvider(BaseModel):
    id: int
    provider_name: str
    metadata: str # JSON
    created_at: datetime.datetime # timestamp?
    updated_at: datetime.datetime # timestamp?

class PaymentMethod:
    id: int
    user: "User"
    provider: PaymentProvider
    provider_specific_id: str
    is_active: bool
    is_default: bool
    metadata: str # JSON
    created_at: datetime.datetime # timestamp?
    updated_at: datetime.datetime # timestamp?

class Trip(BaseModel):
    id: int
    bike_id: int
    user_id: int
    start_time: datetime.datetime # timestamp?
    end_time: datetime.datetime # timestamp?
    start_position: list[float] # import some type?
    end_position: list[float] # import some type?
    path_taken: str # Linestring - import some type?
    start_fee: float
    time_fee: float
    end_fee: float
    total_fee: float
    created_at: datetime.datetime # timestamp?
    updated_at: datetime.datetime # timestamp?

class Transaction(BaseModel):
    id: int
    user: "User"
    amount: float
    transtion_type: str
    transaction_description: str
    trip: Trip
    metadata: str # JSON
    payment_method: PaymentMethod
    created_at: datetime.datetime # timestamp?
    updated_at: datetime.datetime # timestamp?

class User(BaseModel):
    id: int
    full_name: str
    email: str
    balance: float
    use_prepay: bool
    metadata: str
    payment_methods: list[PaymentMethod] # Should work?
    trips: list[Trip]
    transactions: list[Transaction]
    created_at: datetime.datetime # timestamp?
    updated_at: datetime.datetime # timestamp?

class City(BaseModel):
    id: int
    city_name: str
    country_code: str
    c_location: str # position
    created_at: datetime.datetime # timestamp?
    updated_at: datetime.datetime # timestamp?
