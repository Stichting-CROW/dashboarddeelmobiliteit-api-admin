from datetime import datetime
from pydantic import BaseModel


class MailingFilters(BaseModel):
    organisation_id: int | None = None
    core_group_only: bool = False
    microhub_edit_only: bool = False


class MailingRequest(BaseModel):
    subject: str
    body_markdown: str
    filters: MailingFilters = MailingFilters()


class MailingPreviewRequest(BaseModel):
    subject: str
    body_markdown: str


class MailingPreview(BaseModel):
    subject: str
    html: str


class RecipientsResponse(BaseModel):
    count: int
    recipients: list[str]


class MailingResult(BaseModel):
    mailing_id: int | None
    sent_count: int
    failed: list[str]


class LastMailing(BaseModel):
    mailing_id: int
    subject: str
    body_markdown: str
    filters: MailingFilters
    is_test: bool
    recipient_count: int
    sent_by: str
    sent_at: datetime
