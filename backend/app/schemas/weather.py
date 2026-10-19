from pydantic import BaseModel


class WeatherTipOut(BaseModel):
    available: bool
    city: str
    temperature: float | None
    condition: str | None
    tip: str
    source: str | None
