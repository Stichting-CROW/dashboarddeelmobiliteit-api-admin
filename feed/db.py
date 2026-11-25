import json

from db_helper import db_helper

FEED_COLUMNS = """
    f.feed_id, f.system_id, f.feed_url, f.feed_type, f.data_type::text AS data_type,
    f.import_strategy, COALESCE(f.is_active, FALSE) AS is_active, f.default_vehicle_type,
    f.trip_import_start_date, f.remarks, f.authentication, f.request_headers,
    f.last_time_updated, f.last_time_succesfully_imported, f.ignore_disruptions_in_feed_until,
    downtime.downtime_start AS down_since
"""

FEED_FROM = """
    FROM feeds f
    LEFT JOIN LATERAL (
        SELECT downtime_start
        FROM feed_downtime d
        WHERE d.feed_id = f.feed_id AND d.downtime_end IS NULL
        ORDER BY downtime_start DESC
        LIMIT 1
    ) downtime ON TRUE
"""

# Columns that may be written through the API, with their SQL placeholder.
WRITABLE_COLUMNS = {
    "system_id": "%(system_id)s",
    "feed_url": "%(feed_url)s",
    "feed_type": "%(feed_type)s",
    "data_type": "%(data_type)s::feed_data_type",
    "import_strategy": "%(import_strategy)s",
    "is_active": "%(is_active)s",
    "authentication": "%(authentication)s",
    "request_headers": "%(request_headers)s",
    "default_vehicle_type": "%(default_vehicle_type)s",
    "trip_import_start_date": "%(trip_import_start_date)s",
    "remarks": "%(remarks)s",
}
JSON_COLUMNS = {"authentication", "request_headers"}


def _params(values: dict) -> dict:
    params = {}
    for column, value in values.items():
        if column in JSON_COLUMNS:
            params[column] = json.dumps(value) if value else None
        elif hasattr(value, "value"):
            params[column] = value.value
        else:
            params[column] = value
    return params


def list_feeds():
    stmt = f"SELECT {FEED_COLUMNS} {FEED_FROM} ORDER BY f.system_id, f.data_type, f.feed_id;"
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt)
            return cur.fetchall()
        except Exception as e:
            print(e)
            conn.rollback()
            return None


def get_feed(feed_id: int):
    stmt = f"SELECT {FEED_COLUMNS} {FEED_FROM} WHERE f.feed_id = %(feed_id)s;"
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {"feed_id": feed_id})
            return cur.fetchone()
        except Exception as e:
            print(e)
            conn.rollback()
            return None


def create_feed(values: dict):
    """Inserts a feed; values only holds WRITABLE_COLUMNS. Returns the new feed_id."""
    columns = list(values)
    stmt = f"""
        INSERT INTO feeds ({", ".join(columns)}, last_time_updated)
        VALUES ({", ".join(WRITABLE_COLUMNS[c] for c in columns)}, NOW())
        RETURNING feed_id;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, _params(values))
            conn.commit()
            return cur.fetchone()["feed_id"]
        except Exception as e:
            print(e)
            conn.rollback()
            return None


def update_feed(feed_id: int, values: dict) -> bool:
    """Updates the given WRITABLE_COLUMNS of one feed."""
    assignments = ", ".join(f"{column} = {WRITABLE_COLUMNS[column]}" for column in values)
    stmt = f"""
        UPDATE feeds
        SET {assignments}, last_time_updated = NOW()
        WHERE feed_id = %(feed_id)s;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {**_params(values), "feed_id": feed_id})
            conn.commit()
            return cur.rowcount == 1
        except Exception as e:
            print(e)
            conn.rollback()
            return False


def vehicle_type_exists(vehicle_type_id: int) -> bool:
    stmt = "SELECT 1 FROM vehicle_type WHERE vehicle_type_id = %(vehicle_type_id)s;"
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {"vehicle_type_id": vehicle_type_id})
            return cur.fetchone() is not None
        except Exception as e:
            print(e)
            conn.rollback()
            return False


def list_vehicle_types():
    """Generic vehicle types (not tied to an operator) and types already used
    as a feed default."""
    stmt = """
        SELECT vehicle_type_id, form_factor, propulsion_type, name
        FROM vehicle_type
        WHERE system_id IS NULL
        OR vehicle_type_id IN (SELECT default_vehicle_type FROM feeds WHERE default_vehicle_type IS NOT NULL)
        ORDER BY vehicle_type_id;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt)
            return cur.fetchall()
        except Exception as e:
            print(e)
            conn.rollback()
            return []
