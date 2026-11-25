"""Run with: pip install pytest && python -m pytest feed"""
from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from feed import feed_service
from feed.feed import DataTypeEnum, FeedCreate, FeedUpdate, FeedValidateRequest
from feed.validation import (
    check_authentication, check_feed_type, check_feed_url, check_request_headers,
    check_system_id, mask_url
)

ADMIN = SimpleNamespace(user_id="admin@example.com", is_admin=True)
NON_ADMIN = SimpleNamespace(user_id="user@example.com", is_admin=False)

STORED_ROW = {
    "feed_id": 7,
    "system_id": "check",
    "feed_url": "https://api.example.com/gbfs.json?apikey=secret",
    "feed_type": "gbfs",
    "data_type": "vehicles",
    "import_strategy": "clean",
    "is_active": True,
    "default_vehicle_type": None,
    "trip_import_start_date": None,
    "remarks": None,
    "authentication": {"authentication_type": "token", "ApiKeyName": "X-Key", "ApiKey": "secret"},
    "request_headers": {"X-Secret": "secret"},
    "last_time_updated": datetime(2026, 1, 1),
    "last_time_succesfully_imported": None,
    "ignore_disruptions_in_feed_until": None,
    "down_since": None,
}


def assert_bad_request(fn, *args):
    with pytest.raises(HTTPException) as error:
        fn(*args)
    assert error.value.status_code == 400


@pytest.mark.parametrize("system_id", ["check", "dott-nl", "bolt_2"])
def test_valid_system_ids(system_id):
    check_system_id(system_id)


@pytest.mark.parametrize("system_id", ["", "Check", "-dott", "a b", "x" * 65, "a;drop"])
def test_invalid_system_ids(system_id):
    assert_bad_request(check_system_id, system_id)


def test_feed_type_must_match_data_type():
    check_feed_type(DataTypeEnum.trips, "mds-trips-v2")
    assert_bad_request(check_feed_type, DataTypeEnum.trips, "gbfs")
    assert_bad_request(check_feed_type, DataTypeEnum.service_areas, "mds")


@pytest.mark.parametrize("url", ["", "ftp://example.com", "example.com/gbfs.json", "https://ex ample.com"])
def test_invalid_urls(url):
    assert_bad_request(check_feed_url, url)


def test_request_headers():
    check_request_headers({"X-Api-Key": "abc"})
    assert_bad_request(check_request_headers, {"Bad Header": "abc"})
    assert_bad_request(check_request_headers, {"X-Key": "a\nb"})
    assert_bad_request(check_request_headers, {"X-Key": 3})


def test_authentication():
    check_authentication(None)
    check_authentication({})
    check_authentication({"authentication_type": "token", "ApiKeyName": "X-Key", "ApiKey": "abc"})
    check_authentication({
        "authentication_type": "oauth2-bolt",
        "TokenURL": "https://auth.example.com/token",
        "OAuth2Credentials": {"client_id": "id", "client_secret": "secret"},
    })
    assert_bad_request(check_authentication, {"authentication_type": "magic"})
    assert_bad_request(check_authentication, {"authentication_type": "token", "ApiKeyName": "X-Key"})
    assert_bad_request(check_authentication, {"authentication_type": "oauth2", "TokenURL": "https://a/b"})
    assert_bad_request(check_authentication, {
        "authentication_type": "oauth2-dott",
        "OAuth2Credentials": {"keyId": "k", "organizationId": "o", "privateKey": "nope", "audience": ["a"]},
    })


def test_mask_url():
    assert mask_url("https://example.com/gbfs.json") == ("https://example.com/gbfs.json", False)
    assert mask_url("https://user:pw@example.com/v?key=abc&size=10") == \
        ("https://•••@example.com/v?key=•••&size=10", True)


def test_non_admins_are_refused():
    with pytest.raises(HTTPException) as error:
        feed_service.list_feeds(NON_ADMIN)
    assert error.value.status_code == 403


def test_summary_hides_credentials(monkeypatch):
    monkeypatch.setattr(feed_service.db, "list_feeds", lambda: [STORED_ROW])
    summary = feed_service.list_feeds(ADMIN)[0]
    assert "secret" not in summary.json()
    assert summary.authentication_type == "token"
    assert summary.request_header_names == ["X-Secret"]
    assert summary.feed_url_has_hidden_values


def test_created_feeds_are_inactive(monkeypatch):
    created = {}

    def create_feed(values):
        created.update(values)
        return 8

    monkeypatch.setattr(feed_service.db, "create_feed", create_feed)
    monkeypatch.setattr(feed_service.db, "get_feed", lambda feed_id: {**STORED_ROW, "feed_id": feed_id})
    feed_service.create_feed(ADMIN, FeedCreate(
        system_id="check", feed_url="https://example.com/gbfs.json",
        feed_type="gbfs", data_type="vehicles",
    ))
    assert created["is_active"] is False


def test_update_rejects_system_id_change(monkeypatch):
    monkeypatch.setattr(feed_service.db, "get_feed", lambda feed_id: STORED_ROW)
    with pytest.raises(HTTPException) as error:
        feed_service.update_feed(ADMIN, FeedUpdate(feed_id=7, system_id="dott"))
    assert error.value.status_code == 400


def test_update_only_writes_given_fields(monkeypatch):
    updated = {}

    def update_feed(feed_id, values):
        updated.update(values)
        return True

    monkeypatch.setattr(feed_service.db, "get_feed", lambda feed_id: STORED_ROW)
    monkeypatch.setattr(feed_service.db, "update_feed", update_feed)
    feed_service.update_feed(ADMIN, FeedUpdate(feed_id=7, system_id="check", is_active=False))
    assert updated == {"is_active": False}


def test_validate_uses_stored_credentials(monkeypatch):
    sent = {}
    monkeypatch.setattr(feed_service.db, "get_feed", lambda feed_id: STORED_ROW)
    monkeypatch.setattr(feed_service.validator_client, "validate", lambda config: sent.update(config) or {})
    feed_service.validate_feed(ADMIN, FeedValidateRequest(feed_id=7, feed_type="full_gbfs"))
    assert sent["feed_url"] == STORED_ROW["feed_url"]
    assert sent["authentication"] == STORED_ROW["authentication"]
    assert sent["feed_type"] == "full_gbfs"
    assert sent["data_type"] == "vehicles"
