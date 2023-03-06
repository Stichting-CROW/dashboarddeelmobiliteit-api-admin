from organisation.view_data_access import ViewDataAccessOrganisation, ViewDataAccess
from organisation import db
from acl import acl
from fastapi import HTTPException

def is_allowed_to_revoke_data_access(acl: acl.ACL, owner_organisation_id: int):
    if acl.is_admin == True:
        return True
    if ("ORGANISATION_ADMIN" in acl.privileges and acl.organisation_id == owner_organisation_id):
        return True
    return False

def revoke_data_access(acl: acl.ACL, grant_view_data_id: int):
    view_data_access_record = db.get_view_data_access(grant_view_data_id=grant_view_data_id)
    if view_data_access_record == None:
        raise HTTPException(status_code=404, detail="grant_view_data_id doesn't exists")
    owner_organisation_id = view_data_access_record["owner_organisation_id"]

    if not is_allowed_to_revoke_data_access(acl=acl, owner_organisation_id=owner_organisation_id):
        raise HTTPException(status_code=403, detail="user not authorized to revoke data access for this organisation")

    result = db.delete_view_data_access_user(grant_view_data_id=grant_view_data_id)
    if not result:
        raise HTTPException(status_code=400, detail="something went wrong revoking data access")
    return result
