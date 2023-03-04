from organisation.organisation import Organisation, TypeOfOrganisationEnum
from organisation import db

from acl import acl
from fastapi import HTTPException
from pydantic import BaseModel

# Any user is allowed to receive this data
def list_organisations():
    rows = db.list_organisations()
    return list(map(lambda row: convert_organisation_row(row=row), rows))

def convert_organisation_row(row):
    return Organisation(
        organisation_id=row["organisation_id"],
        name=row["name"],
        type_of_organisation=TypeOfOrganisationEnum(row["type_of_organisation"]),
        data_owner_of_municipalities=row["data_owner_of_municipalities"],
        data_owner_of_operators=row["data_owner_of_operators"]
    )