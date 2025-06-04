"""Utility functions for computing horoscope information."""
from datetime import datetime
from typing import Dict, Any

from jhora.horoscope import main
from jhora.panchanga import drik

from .models import ChartRequest


def compute_chart(request: ChartRequest) -> Dict[str, Any]:
    """Generate horoscope data using existing jhora classes."""
    dob = drik.Date(request.birth_date.year, request.birth_date.month, request.birth_date.day)
    tob = (request.birth_time.hour, request.birth_time.minute, request.birth_time.second)
    place = drik.Place(request.place, request.latitude, request.longitude, request.timezone)

    horo = main.Horoscope(
        place_with_country_code=request.place,
        latitude=request.latitude,
        longitude=request.longitude,
        timezone_offset=request.timezone,
        date_in=dob,
        birth_time=request.birth_time.strftime("%H:%M:%S"),
    )

    info, charts, houses = horo.get_horoscope_information()
    vimsottari = horo._get_vimsottari_dhasa_bhukthi(dob, tob, place)

    return {
        "name": request.name,
        "gender": request.gender,
        "info": info,
        "charts": charts,
        "ascendant_houses": houses,
        "vimsottari_dhasa": vimsottari,
    }

