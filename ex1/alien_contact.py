from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, ValidationError, model_validator


class ContactType(str, Enum):
    """Ways an alien contact can be perceived."""

    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    """Alien contact report with cross-field business rules."""

    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)
    witness_count: int = Field(ge=1, le=100)
    message_received: Optional[str] = Field(default=None, max_length=500)
    is_verified: bool = False

    @model_validator(mode="after")
    def check_business_rules(self) -> "AlienContact":
        """Run after every field is valid: rules that span several fields."""
        if not self.contact_id.startswith("AC"):
            raise ValueError('Contact ID must start with "AC"')
        if self.contact_type == ContactType.PHYSICAL and not self.is_verified:
            raise ValueError("Physical contact reports must be verified")
        if (
            self.contact_type == ContactType.TELEPATHIC
            and self.witness_count < 3
        ):
            raise ValueError("Telepathic contact requires at least "
                             "3 witnesses")
        if self.signal_strength > 7.0 and not self.message_received:
            raise ValueError("Strong signals (> 7.0) should include "
                             "received messages")
        return self


def clean_message(raw: str) -> str:
    """Strip Pydantic's 'Value error, ' prefix from custom errors."""
    return raw.removeprefix("Value error, ")


def main() -> None:
    print("Alien Contact Log Validation")
    print("=" * 38)

    try:
        valid_data: dict[str, Any] = {
            "contact_id": "AC_2024_001",
            "timestamp": "2024-03-10T22:15:00",
            "location": "Area 51, Nevada",
            "contact_type": "radio",
            "signal_strength": 8.5,
            "duration_minutes": 45,
            "witness_count": 5,
            "message_received": "Greetings from Zeta Reticuli",
        }
        contact = AlienContact.model_validate(valid_data)
        print("Valid contact report:")
        print(f"ID: {contact.contact_id}")
        print(f"Type: {contact.contact_type.value}")
        print(f"Location: {contact.location}")
        print(f"Signal: {contact.signal_strength}/10")
        print(f"Duration: {contact.duration_minutes} minutes")
        print(f"Witnesses: {contact.witness_count}")
        print(f"Message: '{contact.message_received}'")
    except ValidationError as err:
        print(f"Unexpected validation error: {err}")

    print()
    print("=" * 38)

    try:
        AlienContact(
            contact_id="AC_2024_002",
            timestamp=datetime(2024, 3, 11, 3, 0),
            location="Roswell, New Mexico",
            contact_type=ContactType.TELEPATHIC,
            signal_strength=4.0,
            duration_minutes=10,
            witness_count=2,  # invalid: telepathic needs >= 3
        )
    except ValidationError as err:
        print("Expected validation error:")
        for error in err.errors():
            print(clean_message(error["msg"]))


if __name__ == "__main__":
    main()
