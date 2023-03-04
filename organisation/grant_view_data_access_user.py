from organisation.view_data_access import ViewDataAccess, ViewDataAccessUser
from organisation import db
from acl import acl, get_acl
from fastapi import HTTPException

def is_allowed_to_grant_data_access(acl: acl.ACL, view_data_access: ViewDataAccess):
    if acl.is_admin == True:
        return True
    if ("ORGANISATION_ADMIN" in acl.privileges and acl.organisation_id == view_data_access.owner_organisation_id):
        return True
    return False

def grant_data_access_user(acl: acl.ACL, view_data_access: ViewDataAccessUser):
    if not is_allowed_to_grant_data_access(acl=acl, view_data_access=view_data_access):
        raise HTTPException(status_code=403, detail="user not authorized to grant data access")
    acl_user = get_acl.get_acl_for_user_id(view_data_access.granted_user_id)
    if not acl_user:
        raise HTTPException(status_code=404, detail="granted_user_id doesn't exist")
    if acl_user.part_of_organisation == view_data_access.owner_organisation_id:
        raise HTTPException(status_code=400, detail="can't grant data access because granted_user_id is part of owner organisation")

    result = db.create_view_data_access_user(view_data_access=view_data_access)
    if not result:
        raise HTTPException(status_code=400, detail="something went wrong with granting data access, probably data is already granted to this user")
    return result
