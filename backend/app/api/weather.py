from fastapi import APIRouter

from app.schemas.weather import WeatherTipOut
from app.services import weather_tip_service

router = APIRouter(prefix="/api/v1/weather-tip", tags=["weather"])


@router.get("", response_model=WeatherTipOut)
def get_weather_tip():
    """Consejo de cuidado del dia segun el clima actual. Publico (sin
    autenticacion): se muestra en la portada a cualquier visitante."""
    return weather_tip_service.get_weather_tip()
