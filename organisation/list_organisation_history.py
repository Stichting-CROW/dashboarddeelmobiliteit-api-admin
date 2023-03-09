from organisation.historical_organisation_detail import HistoricalOrganisationDetail
from organisation import db

from acl import acl
from fastapi import HTTPException
from pydantic import BaseModel

def is_allowed_to_list_organisation_history(acl: acl.ACL):
    return acl.is_admin == True

# Any user is allowed to receive this data
def list_organisation_detail_history(acl: acl.ACL, organisation_id: int):
    if not is_allowed_to_list_organisation_history(acl=acl):
        raise HTTPException(status_code=403, detail="user not allowed to list organisation history")
    rows = db.list_organisation_details(organisation_id)
    return list(map(lambda row: convert_organisation_detail_row(row=row), rows))

def convert_organisation_detail_row(row):
    return HistoricalOrganisationDetail(
        organisation_history_id=row["organisation_history_id"],
        organisation_id=row["organisation_id"],
        organisation_details=row["details"],
        timetstamp=row["timestamp"]
    )