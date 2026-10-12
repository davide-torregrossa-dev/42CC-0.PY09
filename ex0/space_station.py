from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, ValidationError


class SpaceStation(BaseModel):
    """Validated telemetry report of a single space station."""

    station_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=1, max_length=50)
    crew_size: int = Field(ge=1, le=20)
    power_level: float = Field(ge=0.0, le=100.0)
    oxygen_level: float = Field(ge=0.0, le=100.0)
    last_maintenance: datetime
    is_operational: bool = True
    notes: Optional[str] = Field(default=None, max_length=200)


def main() -> None:
    print("Space Station Data Validation")
    print("=" * 40)

    try:
        # Pydantic converts the ISO string into a datetime for us
        valid_data: dict[str, Any] = {
            "station_id": "ISS001",
            "name": "International Space Station",
            "crew_size": 6,
            "power_level": 85.5,
            "oxygen_level": 92.3,
            "last_maintenance": "2024-01-15T10:30:00",
        }
        station = SpaceStation.model_validate(valid_data)
        print("Valid station created:")
        print(f"ID: {station.station_id}")
        print(f"Name: {station.name}")
        print(f"Crew: {station.crew_size} people")
        print(f"Power: {station.power_level}%")
        print(f"Oxygen: {station.oxygen_level}%")
        status = "Operational" if station.is_operational else "Offline"
        print(f"Status: {status}")
    except ValidationError as err:
        print(f"Unexpected validation error: {err}")

    print()
    print("=" * 40)

    try:
        SpaceStation(
            station_id="BAD001",
            name="Overcrowded Station",
            crew_size=25,  # invalid: more than 20
            power_level=50.0,
            oxygen_level=50.0,
            last_maintenance=datetime(2024, 1, 15),
        )
    except ValidationError as err:
        print("Expected validation error:")
        for error in err.errors():
            print(error["msg"])


if __name__ == "__main__":
    main()
