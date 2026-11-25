from fastapi import HTTPException

from acl import acl
from feed import db, validator_client
from feed.feed import (
    DataTypeEnum, FeedCreate, FeedCredentials, FeedSummary, FeedUpdate,
    FeedValidateRequest, VehicleTypeOption
)
from feed.validation import (
    check_authentication, check_feed_type, check_feed_url, check_import_strategy,
    check_remarks, check_request_headers, check_system_id, mask_url
)


def ensure_admin(acl: acl.ACL):
    if not acl.is_admin:
        raise HTTPException(status_code=403, detail="only admins are allowed to manage feeds")


def to_summary(row) -> FeedSummary:
    feed_url, has_hidden_values = mask_url(row["feed_url"])
    authentication = row["authentication"] if isinstance(row["authentication"], dict) else None
    request_headers = row["request_headers"] if isinstance(row["request_headers"], dict) else {}
    authentication_type = authentication.get("authentication_type") if authentication else None
    return FeedSummary(
        feed_id=row["feed_id"],
        system_id=row["system_id"],
        feed_url=feed_url,
        feed_url_has_hidden_values=has_hidden_values,
        feed_type=row["feed_type"],
        data_type=row["data_type"],
        import_strategy=row["import_strategy"],
        is_active=row["is_active"],
        default_vehicle_type=row["default_vehicle_type"],
        trip_import_start_date=row["trip_import_start_date"],
        remarks=row["remarks"],
        authentication_type=authentication_type,
        has_authentication=authentication_type is not None,
        request_header_names=sorted(request_headers),
        last_time_updated=row["last_time_updated"],
        last_time_succesfully_imported=row["last_time_succesfully_imported"],
        ignore_disruptions_in_feed_until=row["ignore_disruptions_in_feed_until"],
        down_since=row["down_since"],
    )


def get_row_or_404(feed_id: int):
    row = db.get_feed(feed_id)
    if not row:
        raise HTTPException(status_code=404, detail="feed not found")
    return row


def check_vehicle_type(vehicle_type_id: int | None):
    if vehicle_type_id is not None and not db.vehicle_type_exists(vehicle_type_id):
        raise HTTPException(status_code=400, detail="default_vehicle_type does not exist")


def list_feeds(acl: acl.ACL) -> list[FeedSummary]:
    ensure_admin(acl)
    rows = db.list_feeds()
    if rows is None:
        raise HTTPException(status_code=500, detail="feeds could not be loaded")
    return [to_summary(row) for row in rows]


def get_credentials(acl: acl.ACL, feed_id: int) -> FeedCredentials:
    ensure_admin(acl)
    row = get_row_or_404(feed_id)
    print(f"Feed credentials of feed {feed_id} viewed by {acl.user_id}")
    return FeedCredentials(
        feed_id=feed_id,
        feed_url=row["feed_url"],
        authentication=row["authentication"] or None,
        request_headers=row["request_headers"] or None,
    )


def create_feed(acl: acl.ACL, feed: FeedCreate) -> FeedSummary:
    """New feeds are always inactive, so they are validated before importing."""
    ensure_admin(acl)
    check_system_id(feed.system_id)
    check_feed_type(feed.data_type, feed.feed_type)
    check_feed_url(feed.feed_url)
    check_import_strategy(feed.import_strategy)
    check_authentication(feed.authentication)
    check_request_headers(feed.request_headers)
    check_remarks(feed.remarks)
    check_vehicle_type(feed.default_vehicle_type)

    values = feed.dict()
    values["is_active"] = False
    if feed.data_type != DataTypeEnum.trips:
        values["trip_import_start_date"] = None
    feed_id = db.create_feed(values)
    if feed_id is None:
        raise HTTPException(status_code=500, detail="feed could not be created")
    print(f"Feed {feed_id} ({feed.system_id}, {feed.data_type.value}) created by {acl.user_id}")
    return to_summary(get_row_or_404(feed_id))


def update_feed(acl: acl.ACL, update: FeedUpdate) -> FeedSummary:
    ensure_admin(acl)
    row = get_row_or_404(update.feed_id)
    values = update.dict(exclude_unset=True)
    values.pop("feed_id")

    if "system_id" in values:
        if values.pop("system_id") != row["system_id"]:
            raise HTTPException(status_code=400, detail="system_id cannot be changed, create a new feed instead")
    if "data_type" in values:
        data_type = values.pop("data_type")
        if data_type is None or data_type.value != row["data_type"]:
            raise HTTPException(status_code=400, detail="data_type cannot be changed, create a new feed instead")
    for required in ("feed_url", "feed_type", "import_strategy", "is_active"):
        if required in values and values[required] is None:
            raise HTTPException(status_code=400, detail=f"{required} cannot be empty")

    data_type = DataTypeEnum(row["data_type"])
    check_feed_type(data_type, values.get("feed_type", row["feed_type"]))
    if "feed_url" in values:
        check_feed_url(values["feed_url"])
    if "import_strategy" in values:
        check_import_strategy(values["import_strategy"])
    if "authentication" in values:
        check_authentication(values["authentication"])
    if "request_headers" in values:
        check_request_headers(values["request_headers"])
    if "remarks" in values:
        check_remarks(values["remarks"])
    if "default_vehicle_type" in values:
        check_vehicle_type(values["default_vehicle_type"])
    if data_type != DataTypeEnum.trips and values.get("trip_import_start_date") is not None:
        raise HTTPException(status_code=400, detail="trip_import_start_date only applies to trips feeds")

    if not values:
        return to_summary(row)
    if not db.update_feed(update.feed_id, values):
        raise HTTPException(status_code=500, detail="feed could not be updated")
    print(f"Feed {update.feed_id} updated by {acl.user_id}: {', '.join(sorted(values))}")
    return to_summary(get_row_or_404(update.feed_id))


def validate_feed(acl: acl.ACL, request: FeedValidateRequest) -> dict:
    """Validates a stored feed, optionally with unsaved values. Values that are
    not given (such as credentials that were not replaced) come from the stored feed."""
    ensure_admin(acl)
    given = request.dict(exclude_unset=True)
    given.pop("feed_id", None)

    config = {}
    if request.feed_id is not None:
        row = get_row_or_404(request.feed_id)
        config = {
            "system_id": row["system_id"],
            "data_type": row["data_type"],
            "feed_url": row["feed_url"],
            "feed_type": row["feed_type"],
            "authentication": row["authentication"] or None,
            "request_headers": row["request_headers"] or None,
        }
    for key, value in given.items():
        config[key] = value.value if isinstance(value, DataTypeEnum) else value

    for required in ("data_type", "feed_url", "feed_type"):
        if not config.get(required):
            raise HTTPException(status_code=400, detail=f"{required} is required")
    config.setdefault("system_id", "")
    check_feed_type(DataTypeEnum(config["data_type"]), config["feed_type"])
    check_feed_url(config["feed_url"])
    check_authentication(config.get("authentication"))
    check_request_headers(config.get("request_headers"))

    print(f"Feed validation ({config['system_id']}, {config['data_type']}) requested by {acl.user_id}")
    return validator_client.validate(config)


def list_vehicle_types(acl: acl.ACL) -> list[VehicleTypeOption]:
    ensure_admin(acl)
    options = []
    for row in db.list_vehicle_types():
        parts = [row["form_factor"], row["propulsion_type"]]
        label = " / ".join(p for p in parts if p)
        if row["name"]:
            label += f" ({row['name']})"
        options.append(VehicleTypeOption(vehicle_type_id=row["vehicle_type_id"], label=label))
    return options
