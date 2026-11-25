from db_helper import db_helper
from mailing.mailing import MailingFilters


def list_recipients(filters: MailingFilters):
    """Return a list of e-mail addresses (user_id) matching the filters."""
    stmt = """
        SELECT user_id
        FROM user_account
        WHERE (%(organisation_id)s::int IS NULL OR organisation_id = %(organisation_id)s)
        AND (NOT %(core_group_only)s OR 'CORE_GROUP' = ANY(privileges))
        AND (NOT %(microhub_edit_only)s OR 'MICROHUB_EDIT' = ANY(privileges))
        ORDER BY user_id;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {
                "organisation_id": filters.organisation_id,
                "core_group_only": filters.core_group_only,
                "microhub_edit_only": filters.microhub_edit_only
            })
            return [row["user_id"] for row in cur.fetchall()]
        except Exception as e:
            print(e)
            conn.rollback()
            return []


def save_mailing(subject: str, body_markdown: str, filters: MailingFilters,
                 is_test: bool, recipient_count: int, sent_by: str):
    stmt = """
        INSERT INTO mailing (
            subject, body_markdown, filter_organisation_id, filter_core_group_only,
            filter_microhub_edit_only, is_test, recipient_count, sent_by
        )
        VALUES (
            %(subject)s, %(body_markdown)s, %(filter_organisation_id)s, %(filter_core_group_only)s,
            %(filter_microhub_edit_only)s, %(is_test)s, %(recipient_count)s, %(sent_by)s
        )
        RETURNING mailing_id;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {
                "subject": subject,
                "body_markdown": body_markdown,
                "filter_organisation_id": filters.organisation_id,
                "filter_core_group_only": filters.core_group_only,
                "filter_microhub_edit_only": filters.microhub_edit_only,
                "is_test": is_test,
                "recipient_count": recipient_count,
                "sent_by": sent_by
            })
            conn.commit()
            return cur.fetchone()["mailing_id"]
        except Exception as e:
            print(e)
            conn.rollback()
            return None


def get_last_mailing():
    stmt = """
        SELECT mailing_id, subject, body_markdown, filter_organisation_id,
        filter_core_group_only, filter_microhub_edit_only, is_test,
        recipient_count, sent_by, sent_at
        FROM mailing
        ORDER BY sent_at DESC, mailing_id DESC
        LIMIT 1;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt)
            return cur.fetchone()
        except Exception as e:
            print(e)
            conn.rollback()
            return None
