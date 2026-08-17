from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

class CrawlJobCreate(BaseModel):
    source_ids: list[int] = Field(
        min_length=1,
        max_length=5,
    )
    maximum_pages: int = Field(
        default=100,
        ge=1,
        le=100,
    )
    date_from: date | None = None
    keywords: list[str] | None = Field(
        default=None,
        max_length=20,
    )

    @field_validator("source_ids")
    @classmethod
    def validate_source_ids(
        cls,
        value: list[int],
    ) -> list[int]:
        if any(source_id <= 0 for source_id in value):
            raise ValueError(
                "Source IDs must be positive"
            )

        if len(value) != len(set(value)):
            raise ValueError(
                "Source IDs must be unique"
            )

        return value

class CrawlJobResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    pages_visited: int
    records_extracted: int
    error_count: int
    started_date: datetime | None = None
    completed_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
