from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DeviationBase(BaseModel):
    site: str
    batch_number: str
    event_datetime: datetime | None = None
    description: str
    category: str | None = None
    impact: str | None = None
    severity: str | None = None
    severity_reason: str | None = None


class DeviationCreate(DeviationBase):
    pass


class DeviationResponse(DeviationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeviationAIResult(BaseModel):
    site: str | None = None
    batch_number: str
    event_datetime: datetime | None = None
    description: str
    category: str | None = None
    impact: str
    severity: str
    severity_reason: str

class DeviationAnalyzeRequest(BaseModel):
    input_text: str