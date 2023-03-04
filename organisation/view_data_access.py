from pydantic import BaseModel

class ViewDataAccess(BaseModel):
    grant_view_data_id: int = None
    owner_organisation_id: int   

class ViewDataAccessOrganisation(ViewDataAccess):
    granted_organisation_id: int

class ViewDataAccessUser(ViewDataAccess):
    granted_user_id: str
