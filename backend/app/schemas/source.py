from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

class SourceBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=200,
    )
    base_url: str = Field(
        min_length=8,
        max_length=2048,
    )
    enabled_status: bool = True
    request_delay: int = Field(
        default=2,
        ge=1,
        le=60,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Source name cannot be empty"
            )

        return value

class SourceCreate(SourceBase):
    pass

class SourceResponse(SourceBase):
    id: int
    created_date: datetime
    updated_date: datetime | None = None
    last_crawl_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
