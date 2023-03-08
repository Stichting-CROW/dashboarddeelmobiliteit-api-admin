from organisation import organisation, db
from acl import acl
from fastapi import HTTPException

def is_allowed_to_create_organisation(acl: acl.ACL):
    return acl.is_admin == True

def create_organisation(acl: acl.ACL, organisation_object: organisation.Organisation):
    if not is_allowed_to_create_organisation(acl):
        raise HTTPException(status_code=403, detail="user not authorized to create organisations")
    result = db.create_organisation(organisation_object)
    db.create_historical_organisation_detail(result)
    if not result:
        raise HTTPException(status_code=400, detail="something went wrong with creating the organisation, " +
                             "probably an organisation with this name already exits")
    return result
