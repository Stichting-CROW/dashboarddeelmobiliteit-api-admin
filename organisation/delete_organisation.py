from organisation import db
from acl import acl
from fastapi import HTTPException

def is_allowed_to_delete_organisation(acl: acl.ACL):
    return acl.is_admin == True

def delete_organisation(acl: acl.ACL, organisation_id: int):
    if not is_allowed_to_delete_organisation(acl):
        raise HTTPException(status_code=403, detail="user not authorized to delete organisations")
    if db.check_if_organisation_has_users(organisation_id=organisation_id):
        raise HTTPException(status_code=400, detail="can't delete organisation because it contains users," +
                            " please delete all users before deleting the organisation.")
    if db.check_if_organisation_has_granted_data_access(organisation_id=organisation_id):
        raise HTTPException(status_code=400, detail="can't delete organisation because it has granted data access," +
                            " please retract all granted data access before deleting the organisation.")

    result = db.delete_organisation(organisation_id)
    if not result:
        raise HTTPException(status_code=400, detail="something went wrong with deleting the organisation, " +
                             "probably the organisation was already deleted")
    return
