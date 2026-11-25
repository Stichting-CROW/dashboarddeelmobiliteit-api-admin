import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid

from mailing import render


class SmtpNotConfigured(Exception):
    pass


def get_smtp_config():
    host = os.getenv("SMTP_HOST")
    sender = os.getenv("SMTP_FROM")
    if not host or not sender:
        raise SmtpNotConfigured("SMTP_HOST and SMTP_FROM environment variables must be set")

    return {
        "host": host,
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER"),
        "password": os.getenv("SMTP_PASSWORD"),
        "from_address": sender,
        "from_name": os.getenv("SMTP_FROM_NAME", render.PROJECT_NAME),
        # "starttls" (default, port 587), "ssl" (port 465) or "none" (plain, e.g. local mail-catcher)
        "security": os.getenv("SMTP_SECURITY", "starttls").lower(),
        "timeout": int(os.getenv("SMTP_TIMEOUT", "30")),
    }


def build_message(config, recipient: str, subject: str, body_markdown: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((config["from_name"], config["from_address"]))
    msg["To"] = recipient
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=config["from_address"].split("@")[-1])
    msg.set_content(render.render_text(subject, body_markdown))
    msg.add_alternative(render.render_html(subject, body_markdown), subtype="html")
    return msg


def connect(config) -> smtplib.SMTP:
    if config["security"] == "ssl":
        server = smtplib.SMTP_SSL(config["host"], config["port"], timeout=config["timeout"])
    else:
        server = smtplib.SMTP(config["host"], config["port"], timeout=config["timeout"])
        server.ehlo()
        if config["security"] == "starttls":
            server.starttls()
            server.ehlo()
    if config["user"] and config["password"]:
        server.login(config["user"], config["password"])
    return server


def send_mailing(recipients: list[str], subject: str, body_markdown: str):
    """Send one e-mail per recipient over a single SMTP connection.

    Returns (sent_count, failed_recipients).
    """
    config = get_smtp_config()
    sent_count = 0
    failed = []

    if not recipients:
        return sent_count, failed

    server = connect(config)
    try:
        for recipient in recipients:
            try:
                msg = build_message(config, recipient, subject, body_markdown)
                server.send_message(msg)
                sent_count += 1
            except smtplib.SMTPServerDisconnected:
                # Reconnect once and retry this recipient
                try:
                    server = connect(config)
                    server.send_message(build_message(config, recipient, subject, body_markdown))
                    sent_count += 1
                except Exception as e:
                    print(f"Failed to send mailing to {recipient}: {e}")
                    failed.append(recipient)
            except Exception as e:
                print(f"Failed to send mailing to {recipient}: {e}")
                failed.append(recipient)
    finally:
        try:
            server.quit()
        except Exception:
            pass

    return sent_count, failed
