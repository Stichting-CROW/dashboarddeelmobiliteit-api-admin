from user import user_account, db
from acl import acl
from fastapi import HTTPException

def is_allowed_to_update_user(acl: acl.ACL, organisation_id: int):
    if acl.is_admin == True:
        return True
    if ("ORGANISATION_ADMIN" in acl.privileges and acl.part_of_organisation == organisation_id):
        return True
    return False

def is_allowed_to_change_organisation_user(acl: acl.ACL):
    if acl.is_admin == True:
        return True
    return False

def update_user(acl: acl.ACL, user_account_object: user_account.UserAccount):
    user_account_object.user_id = user_account_object.user_id.lower()
    user_row = db.get_user(user_account_object.user_id)
    
    if not user_row:
        raise HTTPException(status_code=404, detail="user doesn't exists")
    if user_row["organisation_id"] != user_account_object.organisation_id and not is_allowed_to_change_organisation_user(acl=acl):
        raise HTTPException(status_code=403, detail="user not authorized to move users between organisations")
    if not is_allowed_to_update_user(acl=acl, organisation_id=user_row["organisation_id"]):
        raise HTTPException(status_code=403, detail="user not authorized to update this user")
    
    result_db = db.update_user(user_account=user_account_object)
    if not result_db:
        raise HTTPException(status_code=500, detail="something went wrong with updating user")
    return user_account_object
