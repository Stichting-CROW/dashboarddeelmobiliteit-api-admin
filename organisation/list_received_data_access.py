from organisation.view_data_access import convert_data_access_row
from organisation import db

from acl import acl
from fastapi import HTTPException
from pydantic import BaseModel

# Any user is allowed to receive this data
def list_received_data_access(acl_user: acl.ACL):
    rows = db.list_received_data_access(acl_user.part_of_organisation, acl_user.user_id)
    return list(map(lambda row: convert_data_access_row(row=row), rows))
