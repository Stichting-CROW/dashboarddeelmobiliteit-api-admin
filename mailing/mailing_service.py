from fastapi import HTTPException

from acl import acl
from mailing import db, render, send
from mailing.mailing import (
    MailingFilters, MailingRequest, MailingPreviewRequest, MailingPreview,
    RecipientsResponse, MailingResult, LastMailing
)


def ensure_admin(acl: acl.ACL):
    if not acl.is_admin:
        raise HTTPException(status_code=403, detail="only admins are allowed to send mailings")


def validate_content(subject: str, body_markdown: str):
    if not subject or not subject.strip():
        raise HTTPException(status_code=400, detail="subject is required")
    if not body_markdown or not body_markdown.strip():
        raise HTTPException(status_code=400, detail="body_markdown is required")


def list_recipients(acl: acl.ACL, filters: MailingFilters) -> RecipientsResponse:
    ensure_admin(acl)
    recipients = db.list_recipients(filters)
    return RecipientsResponse(count=len(recipients), recipients=recipients)


def preview(acl: acl.ACL, request: MailingPreviewRequest) -> MailingPreview:
    ensure_admin(acl)
    return MailingPreview(
        subject=request.subject,
        html=render.render_html(request.subject, request.body_markdown)
    )


def _send(acl: acl.ACL, request: MailingRequest, recipients: list[str], is_test: bool) -> MailingResult:
    validate_content(request.subject, request.body_markdown)
    try:
        sent_count, failed = send.send_mailing(recipients, request.subject, request.body_markdown)
    except send.SmtpNotConfigured as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print("SMTP error while sending mailing:", e)
        raise HTTPException(status_code=502, detail="could not connect to the mail server")

    mailing_id = db.save_mailing(
        subject=request.subject,
        body_markdown=request.body_markdown,
        filters=request.filters,
        is_test=is_test,
        recipient_count=sent_count,
        sent_by=acl.user_id
    )
    return MailingResult(mailing_id=mailing_id, sent_count=sent_count, failed=failed)


def send_test(acl: acl.ACL, request: MailingRequest) -> MailingResult:
    """Send the mailing only to the admin who is logged in."""
    ensure_admin(acl)
    return _send(acl, request, [acl.user_id], is_test=True)


def send_to_recipients(acl: acl.ACL, request: MailingRequest) -> MailingResult:
    """Send the mailing to all users matching the filters."""
    ensure_admin(acl)
    validate_content(request.subject, request.body_markdown)
    recipients = db.list_recipients(request.filters)
    if len(recipients) == 0:
        raise HTTPException(status_code=400, detail="no recipients match the given filters")
    return _send(acl, request, recipients, is_test=False)


def get_last(acl: acl.ACL) -> LastMailing | None:
    ensure_admin(acl)
    row = db.get_last_mailing()
    if not row:
        return None
    return LastMailing(
        mailing_id=row["mailing_id"],
        subject=row["subject"],
        body_markdown=row["body_markdown"],
        filters=MailingFilters(
            organisation_id=row["filter_organisation_id"],
            core_group_only=row["filter_core_group_only"],
            microhub_edit_only=row["filter_microhub_edit_only"]
        ),
        is_test=row["is_test"],
        recipient_count=row["recipient_count"],
        sent_by=row["sent_by"],
        sent_at=row["sent_at"]
    )
