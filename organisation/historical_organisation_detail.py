from pydantic import BaseModel
from enum import Enum
import datetime

class HistoricalOrganisationDetail(BaseModel):
    organisation_history_id: int
    organisation_id: int
    organisation_details: dict = None
    timetstamp: datetime.datetime
