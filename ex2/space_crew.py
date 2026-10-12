from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    """Crew ranks, from lowest to highest."""

    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    """A single crew member (validated on its own, also when nested)."""

    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    """A mission containing a nested list of CrewMember models."""

    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def check_safety_rules(self) -> "SpaceMission":
        """Mission-level safety rules, run after all fields are valid."""
        if not self.mission_id.startswith("M"):
            raise ValueError('Mission ID must start with "M"')

        leaders = [
            member for member in self.crew
            if member.rank in (Rank.COMMANDER, Rank.CAPTAIN)
        ]
        if not leaders:
            raise ValueError("Mission must have at least one Commander "
                             "or Captain")

        if self.duration_days > 365:
            veterans = sum(
                1 for member in self.crew if member.years_experience >= 5
            )
            # veterans / total >= 0.5, written without float division
            if veterans * 2 < len(self.crew):
                raise ValueError("Long missions (> 365 days) need 50% "
                                 "experienced crew (5+ years)")

        if not all(member.is_active for member in self.crew):
            raise ValueError("All crew members must be active")

        return self


def clean_message(raw: str) -> str:
    """Strip Pydantic's 'Value error, ' prefix from custom errors."""
    return raw.removeprefix("Value error, ")


def main() -> None:
    print("Space Mission Crew Validation")
    print("=" * 41)

    try:
        mission = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date=datetime(2024, 6, 1),
            duration_days=900,
            budget_millions=2500.0,
            crew=[
                CrewMember(
                    member_id="C001", name="Sarah Connor",
                    rank=Rank.COMMANDER, age=45,
                    specialization="Mission Command", years_experience=20,
                ),
                CrewMember(
                    member_id="C002", name="John Smith",
                    rank=Rank.LIEUTENANT, age=35,
                    specialization="Navigation", years_experience=10,
                ),
                CrewMember(
                    member_id="C003", name="Alice Johnson",
                    rank=Rank.OFFICER, age=29,
                    specialization="Engineering", years_experience=3,
                ),
            ],
        )
        print("Valid mission created:")
        print(f"Mission: {mission.mission_name}")
        print(f"ID: {mission.mission_id}")
        print(f"Destination: {mission.destination}")
        print(f"Duration: {mission.duration_days} days")
        print(f"Budget: ${mission.budget_millions}M")
        print(f"Crew size: {len(mission.crew)}")
        print("Crew members:")
        for member in mission.crew:
            print(f"- {member.name} ({member.rank.value}) - "
                  f"{member.specialization}")
    except ValidationError as err:
        print(f"Unexpected validation error: {err}")

    print()
    print("=" * 41)

    try:
        SpaceMission(
            mission_id="M2024_MOON",
            mission_name="Lunar Survey",
            destination="Moon",
            launch_date=datetime(2024, 9, 1),
            duration_days=30,
            budget_millions=300.0,
            crew=[
                CrewMember(
                    member_id="C010", name="Bob Lee",
                    rank=Rank.OFFICER, age=31,
                    specialization="Geology", years_experience=6,
                ),
            ],  # invalid: no Commander or Captain
        )
    except ValidationError as err:
        print("Expected validation error:")
        for error in err.errors():
            print(clean_message(error["msg"]))


if __name__ == "__main__":
    main()
