from dataclasses import dataclass
from user.user_account import PrivilegesEnum

@dataclass
class ACL:
    part_of_organisation: int
    privileges: list[PrivilegesEnum]
    is_admin: bool