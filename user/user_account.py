from enum import Enum
from pydantic import BaseModel

class PrivilegesEnum(str, Enum):
    organisation_admin = 'ORGANISATION_ADMIN'
    microhub_edit = 'MICROHUB_EDIT'
    download_raw_data = 'DOWNLOAD_RAW_DATA'
    core_group = 'CORE_GROUP'

class UserAccount(BaseModel):
    user_id:         str
    privileges:      list[PrivilegesEnum] = None
    organisation_id: int

class UserAccountSuccesfullyCreated(BaseModel):
    user_account:       UserAccount
    generated_password: str