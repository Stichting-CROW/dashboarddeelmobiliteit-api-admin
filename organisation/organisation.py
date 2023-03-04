from pydantic import BaseModel
from enum import Enum

class TypeOfOrganisationEnum(str, Enum):
    municipality = 'MUNICIPALITY'
    other_governement = 'OTHER_GOVERNMENT'
    operator = 'OPERATOR'
    admin = 'ADMIN'
    other_company = 'OTHER_COMPANY'

class Organisation(BaseModel):
    organisation_id: int = None
    name: str
    type_of_organisation: TypeOfOrganisationEnum
    data_owner_of_municipalities: list[str] = None
    data_owner_of_operators: list[str] = None    

class OrganisationWithDetails(Organisation):
    organisation_details: dict = None
