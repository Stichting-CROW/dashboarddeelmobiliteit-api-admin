from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class DataTypeEnum(str, Enum):
    vehicles = "vehicles"
    trips = "trips"
    service_areas = "service_areas"


# Feed types each data type supports, matching the importers in dd-importer-v2
# (main.go, cmd/trip_importer, cmd/service_area_importer) and validator.FeedTypesByDataType.
FEED_TYPES_BY_DATA_TYPE = {
    DataTypeEnum.vehicles: ["gbfs", "full_gbfs", "mds", "mds-v2", "tomp"],
    DataTypeEnum.trips: ["mds-trips-v1", "mds-trips-v2"],
    DataTypeEnum.service_areas: ["gbfs", "full_gbfs", "manifest_gbfs"],
}

IMPORT_STRATEGIES = ["clean", "gps"]


class FeedSummary(BaseModel):
    """A feeds row without credentials, safe to show on screen."""
    feed_id: int
    system_id: str
    # Query values are masked; the full URL is returned by /feed/{feed_id}/credentials.
    feed_url: str
    feed_url_has_hidden_values: bool
    feed_type: str
    data_type: DataTypeEnum
    import_strategy: str
    is_active: bool
    default_vehicle_type: int | None
    trip_import_start_date: datetime | None
    remarks: str | None
    authentication_type: str | None
    has_authentication: bool
    request_header_names: list[str]
    last_time_updated: datetime | None
    last_time_succesfully_imported: datetime | None
    ignore_disruptions_in_feed_until: datetime | None
    down_since: datetime | None


class FeedCredentials(BaseModel):
    feed_id: int
    feed_url: str
    authentication: dict | None
    request_headers: dict | None


class FeedCreate(BaseModel):
    system_id: str
    feed_url: str
    feed_type: str
    data_type: DataTypeEnum
    import_strategy: str = "clean"
    authentication: dict | None = None
    request_headers: dict | None = None
    default_vehicle_type: int | None = None
    trip_import_start_date: datetime | None = None
    remarks: str | None = None


class FeedUpdate(BaseModel):
    """Only the fields present in the request are changed. system_id and
    data_type may be sent but must equal the stored values."""
    feed_id: int
    system_id: str | None = None
    data_type: DataTypeEnum | None = None
    feed_url: str | None = None
    feed_type: str | None = None
    import_strategy: str | None = None
    is_active: bool | None = None
    authentication: dict | None = None
    request_headers: dict | None = None
    default_vehicle_type: int | None = None
    trip_import_start_date: datetime | None = None
    remarks: str | None = None


class FeedValidateRequest(BaseModel):
    """Validate a stored feed (feed_id), unsaved form values, or a stored feed
    with some values replaced. Missing credentials are taken from the stored feed."""
    feed_id: int | None = None
    system_id: str | None = None
    data_type: DataTypeEnum | None = None
    feed_url: str | None = None
    feed_type: str | None = None
    authentication: dict | None = None
    request_headers: dict | None = None


class VehicleTypeOption(BaseModel):
    vehicle_type_id: int
    label: str
