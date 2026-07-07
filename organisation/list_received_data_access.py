from organisation.view_data_access import convert_data_access_row
from organisation import db

from acl import acl, get_acl
from fastapi import HTTPException
from pydantic import BaseModel

# Any user is allowed to receive this data
def list_received_data_access(acl_user: acl.ACL):
    rows = db.list_received_data_access(acl_user.part_of_organisation, acl_user.user_id)
    return list(map(lambda row: convert_data_access_row(row=row), rows))

def is_allowed_to_list_received_data_access_for_user(acl_user: acl.ACL, organisation_id: int):
    if acl_user.is_admin == True:
        return True
    if acl_user.part_of_organisation == organisation_id:
        return True
    return False

# List the data access received by a specific user (their organisation grants
# + grants made directly to that user). Used by admins/organisation-admins to
# inspect what data another user can access.
def list_received_data_access_for_user(acl_user: acl.ACL, user_id: str):
    target_acl = get_acl.get_acl_for_user_id(user_id)
    if target_acl == None:
        raise HTTPException(status_code=404, detail="user not found")

    if not is_allowed_to_list_received_data_access_for_user(acl_user=acl_user, organisation_id=target_acl.part_of_organisation):
        raise HTTPException(status_code=403, detail="user not authorized to list received data access for this user")

    rows = db.list_received_data_access(target_acl.part_of_organisation, target_acl.user_id)
    return list(map(lambda row: convert_data_access_row(row=row), rows))
