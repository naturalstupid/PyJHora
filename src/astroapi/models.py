from datetime import date, time
from pydantic import BaseModel

class ChartRequest(BaseModel):
    """Parameters required to compute a horoscope chart."""
    name: str
    gender: str
    birth_date: date
    birth_time: time
    place: str
    latitude: float
    longitude: float
    timezone: float

