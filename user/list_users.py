from user import db
from user.user_account import PrivilegesEnum
from acl import acl
from fastapi import HTTPException
from pydantic import BaseModel

class UserAccountListItem(BaseModel):
    user_id:           str
    privileges:        list[PrivilegesEnum]
    organisation_id:   int
    organisation_name: str
    is_admin:          bool

def is_allowed_to_list_users(acl: acl.ACL, organisation_id: int):
    if (acl.is_admin == True):
        return True
    if (acl.part_of_organisation == organisation_id):
        return True
    return False

def enforce_organisation_filter(acl: acl.ACL):
    if (acl.is_admin == True):
        return False
    return acl.part_of_organisation

def list_users(acl: acl.ACL, organisation_id: int):
    if not is_allowed_to_list_users(acl=acl, organisation_id=organisation_id):
        raise HTTPException(status_code=403, detail="user not authorized to list users for this organisation")

    result = enforce_organisation_filter(acl=acl)
    if result:
        organisation_id = result
    rows = db.list_users(organisation_id=organisation_id)
    return list(map(lambda row: convert_user_row(row=row), rows))

def convert_user_row(row):
    privileges = []
    if row["privileges"]:
        privileges = list(map(lambda x: PrivilegesEnum(x), row["privileges"]))
    print(row)
    return UserAccountListItem(
        user_id=row["user_id"],
        privileges=privileges,
        organisation_id=row["organisation_id"],
        organisation_name=row["organisation_name"],
        is_admin=row["is_admin"]
    )