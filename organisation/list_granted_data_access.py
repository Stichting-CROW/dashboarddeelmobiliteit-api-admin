from organisation.view_data_access import convert_data_access_row
from organisation import db

from acl import acl
from fastapi import HTTPException
from pydantic import BaseModel

def is_allowed_to_list_granted_data_access(acl: acl.ACL, organisation_id: int):
    if acl.is_admin == True:
        return True
    if (acl.part_of_organisation == organisation_id):
        return True
    return False

# Any user is allowed to receive this data
def list_granted_data_access(acl_user: acl.ACL, organisation_id: int):
    if not is_allowed_to_list_granted_data_access(acl=acl_user, organisation_id=organisation_id):
        raise HTTPException(status_code=403, detail="user is not allowed to list granted_data access of other organisations.")

    rows = db.list_given_data_access(organisation_id=organisation_id)
    return list(map(lambda row: convert_data_access_row(row=row), rows))
