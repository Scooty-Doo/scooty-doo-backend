from pydantic import BaseModel, ConfigDict
class BikeTest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    battery_level: int
    position: str
