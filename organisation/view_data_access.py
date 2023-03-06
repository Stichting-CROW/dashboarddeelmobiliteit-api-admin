from pydantic import BaseModel

class ViewDataAccess(BaseModel):
    grant_view_data_id: int = None
    owner_organisation_id: int   

class ViewDataAccessOrganisation(ViewDataAccess):
    granted_organisation_id: int

class ViewDataAccessUser(ViewDataAccess):
    granted_user_id: str

class ViewDataAccessListResult(ViewDataAccess):
    owner_organisation_name: str
    granted_organisation_id: int = None
    granted_organisation_name: str = None
    granted_user_id: str = None

def convert_data_access_row(row):
    return ViewDataAccessListResult(
        grant_view_data_id=row["grant_view_data_id"],
        owner_organisation_id=row["owner_organisation_id"],
        owner_organisation_name=row["owner_organisation_name"],
        granted_organisation_id=row["granted_organisation_id"],
        granted_organisation_name=row["granted_organisation_name"],
        granted_user_id=row["granted_user"]
    )