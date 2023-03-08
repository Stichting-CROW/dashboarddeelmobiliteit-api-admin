from organisation import organisation, db
from acl import acl
from fastapi import HTTPException
import json

def is_allowed_to_update_organisation(acl: acl.ACL):
    return acl.is_admin == True

def update_organisation(acl: acl.ACL, new_organisation_object: organisation.OrganisationWithDetails):
    if not is_allowed_to_update_organisation(acl):
        raise HTTPException(status_code=403, detail="user not authorized to update organisations")
    organisation_id = new_organisation_object.organisation_id
    if organisation_id  == None:
        raise HTTPException(status_code=400, detail="organisation_id should be specified")
    
    old_organisation_row = db.get_organisation(organisation_id=organisation_id)
    if not old_organisation_row:
        raise HTTPException(status_code=404, detail="organisation with this organisation_id doesn't exists")
    
    result = db.update_organisation(organisation=new_organisation_object)
    if not result:
        raise HTTPException(status_code=500, detail="something went wrong with updating organisation, probably you are setting a name that is already in use.")
    if old_organisation_row["organisation_details"] != new_organisation_object.organisation_details:
        db.create_historical_organisation_detail(new_organisation_object)
    return new_organisation_object
    # 5. if changed add history record (add this to create organisation as well)
    
    #result = db.create_organisation(organisation_object)
    #if not result:
    #    raise HTTPException(status_code=400, detail="something went wrong with creating the organisation, " +
    #                         "probably an organisation with this name already exits")
    #return result
