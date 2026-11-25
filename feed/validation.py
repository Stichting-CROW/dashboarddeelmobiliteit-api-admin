"""Input checks for feed configurations. They mirror what the importer reads
(dd-importer-v2 feed/authentication.go), so a saved feed cannot crash it."""
import re
from urllib.parse import urlsplit, urlunsplit, unquote

from fastapi import HTTPException

from feed.feed import FEED_TYPES_BY_DATA_TYPE, IMPORT_STRATEGIES, DataTypeEnum

SYSTEM_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
HEADER_NAME_PATTERN = re.compile(r"^[A-Za-z0-9!#$%&'*+.^_`|~-]+$")
MAX_URL_LENGTH = 2000
MAX_REMARKS_LENGTH = 2000
MASK = "•••"
# Query parameters whose values are not secret (same list as validator.MaskURL).
SAFE_QUERY_PARAMS = {"end_time", "size", "page[offset]", "page[limit]"}

# Required string fields per authentication_type: (top-level keys, OAuth2Credentials keys).
AUTHENTICATION_FIELDS = {
    "token": (["ApiKeyName", "ApiKey"], None),
    "oauth2": (["TokenURL"], ["client_id", "client_secret", "grant_type", "scope"]),
    "oauth2-bolt": (["TokenURL"], ["client_id", "client_secret"]),
    "oauth2-basic-auth": (["TokenURL"], ["client_id", "client_secret"]),
    "oauth2-moveyou": (["TokenURL"], ["client_id", "client_secret", "grant_type"]),
    "oauth2-dott": ([], ["keyId", "organizationId", "privateKey"]),
}


def bad_request(detail: str):
    raise HTTPException(status_code=400, detail=detail)


def check_system_id(system_id: str):
    if not system_id or not SYSTEM_ID_PATTERN.match(system_id):
        bad_request("system_id must be lowercase letters, digits, '-' or '_' (max 64 characters)")


def check_feed_type(data_type: DataTypeEnum, feed_type: str):
    allowed = FEED_TYPES_BY_DATA_TYPE[DataTypeEnum(data_type)]
    if feed_type not in allowed:
        bad_request(f"feed_type '{feed_type}' is not supported for data_type '{data_type.value}', "
                    f"choose one of: {', '.join(allowed)}")


def check_import_strategy(import_strategy: str):
    if import_strategy not in IMPORT_STRATEGIES:
        bad_request(f"import_strategy must be one of: {', '.join(IMPORT_STRATEGIES)}")


def check_feed_url(feed_url: str):
    if not feed_url or len(feed_url) > MAX_URL_LENGTH:
        bad_request(f"feed_url is required and at most {MAX_URL_LENGTH} characters")
    try:
        parts = urlsplit(feed_url)
    except ValueError:
        bad_request("feed_url is not a valid URL")
    if parts.scheme not in ("http", "https") or not parts.netloc or any(c.isspace() for c in feed_url):
        bad_request("feed_url must be a complete http(s) URL without spaces")


def check_remarks(remarks: str | None):
    if remarks is not None and len(remarks) > MAX_REMARKS_LENGTH:
        bad_request(f"remarks are at most {MAX_REMARKS_LENGTH} characters")


def check_request_headers(request_headers: dict | None):
    if request_headers is None:
        return
    for name, value in request_headers.items():
        if not HEADER_NAME_PATTERN.match(name):
            bad_request(f"request header name '{name}' is not valid")
        if not isinstance(value, str) or "\n" in value or "\r" in value:
            bad_request(f"request header '{name}' must have a single-line text value")


def check_authentication(authentication: dict | None):
    """An empty value or one without authentication_type means no authentication."""
    if not authentication or "authentication_type" not in authentication:
        return
    authentication_type = authentication["authentication_type"]
    if authentication_type not in AUTHENTICATION_FIELDS:
        bad_request(f"authentication_type must be one of: {', '.join(AUTHENTICATION_FIELDS)}")

    top_level, credential_fields = AUTHENTICATION_FIELDS[authentication_type]
    for key in top_level:
        if not isinstance(authentication.get(key), str) or not authentication[key]:
            bad_request(f"authentication.{key} is required for {authentication_type}")
    if credential_fields is None:
        return

    credentials = authentication.get("OAuth2Credentials")
    if not isinstance(credentials, dict):
        bad_request(f"authentication.OAuth2Credentials must be an object for {authentication_type}")
    for key in credential_fields:
        if not isinstance(credentials.get(key), str) or not credentials[key]:
            bad_request(f"authentication.OAuth2Credentials.{key} is required for {authentication_type}")
    if authentication_type in ("oauth2-bolt", "oauth2-basic-auth") and \
            credentials.get("scope") is not None and not isinstance(credentials["scope"], str):
        bad_request("authentication.OAuth2Credentials.scope must be text")
    if authentication_type == "oauth2-dott":
        audience = credentials.get("audience")
        if not isinstance(audience, list) or not audience or not all(isinstance(a, str) and a for a in audience):
            bad_request("authentication.OAuth2Credentials.audience must be a non-empty list of text values")
        if "PRIVATE KEY-----" not in credentials["privateKey"]:
            bad_request("authentication.OAuth2Credentials.privateKey must be a PEM encoded EC private key")


def mask_url(feed_url: str) -> tuple[str, bool]:
    """Returns the URL with user info and query values masked, and whether
    anything was masked."""
    try:
        parts = urlsplit(feed_url)
    except ValueError:
        return "(ongeldige URL)", True

    masked = False
    netloc = parts.netloc
    if "@" in netloc:
        netloc = MASK + "@" + netloc.rsplit("@", 1)[1]
        masked = True

    query_parts = []
    for part in parts.query.split("&") if parts.query else []:
        key, has_value, _ = part.partition("=")
        if has_value and unquote(key) not in SAFE_QUERY_PARAMS:
            query_parts.append(f"{key}={MASK}")
            masked = True
        else:
            query_parts.append(part)
    return urlunsplit((parts.scheme, netloc, parts.path, "&".join(query_parts), parts.fragment)), masked
