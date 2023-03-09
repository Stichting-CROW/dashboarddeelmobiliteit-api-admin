from organisation.organisation import OrganisationWithDetails, TypeOfOrganisationEnum
from organisation import db

from acl import acl
from fastapi import HTTPException
from pydantic import BaseModel

def is_allowed_to_get_organisation_details_from_other_organisation(acl: acl.ACL):
    return acl.is_admin == True

def get_organisation(organisation_id: int, acl: acl.ACL):
    if organisation_id == None:
        organisation_id = acl.part_of_organisation
    if organisation_id != acl.part_of_organisation and not is_allowed_to_get_organisation_details_from_other_organisation:
        raise HTTPException(status_code=403, detail="user is not allowed to view details of other organisation")
    
    result = db.get_organisation(organisation_id=organisation_id)
    if not result:
        raise HTTPException(status_code=404, detail="organisation not found")
    return convert_organisation_with_details(row=result)

def convert_organisation_with_details(row):
    return OrganisationWithDetails(
        organisation_id=row["organisation_id"],
        name=row["name"],
        type_of_organisation=TypeOfOrganisationEnum(row["type_of_organisation"]),
        data_owner_of_municipalities=row["data_owner_of_municipalities"],
        data_owner_of_operators=row["data_owner_of_operators"],
        organisation_details=row["organisation_details"]
    )