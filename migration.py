from db_helper import db_helper
from organisation.organisation import OrganisationWithDetails, TypeOfOrganisationEnum
from organisation import db as db
from user import db as user_db
from user.user_account import UserAccount, PrivilegesEnum

# This script migrates the dashboard deelmobiliteit from the old user centric
# acl structure to the new organisation centric acl structure. 

def query_rows(stmt):
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt)
            return cur.fetchall()
        except Exception as e:
            print(e)
            conn.rollback()
            return False


stmt = """
    SELECT organisation_id
    FROM organisation
    WHERE name = 'CROW';
"""
admin_organisation = query_rows(stmt=stmt)
if len(admin_organisation) != 1:
    print("CROW organisation doesn't exists")
    exit()
admin_organisation_id = admin_organisation[0]["organisation_id"]

# 1. Create organisations.
# a. operators
stmt = """
    SELECT DISTINCT(system_id) as system_id FROM feeds;
"""
operators = query_rows(stmt)
operator_look_up = {}
for operator in operators:
    new_organisation = OrganisationWithDetails(
        name=operator["system_id"].capitalize(),
        type_of_organisation=TypeOfOrganisationEnum.operator,
        data_owner_of_operators=[operator["system_id"]]
    )
    new_organisation = db.create_organisation(organisation=new_organisation)
    db.create_historical_organisation_detail(organisation=new_organisation)
    operator_look_up[operator["system_id"]] = new_organisation.organisation_id



# b. municipalities
stmt = """
    SELECT municipality as gmcode, name 
    FROM zones 
    WHERE municipality IN 
        (SELECT DISTINCT(municipality) 
        FROM acl_municipalities) 
    AND zone_type = 'municipality';
"""
municipalities = query_rows(stmt)
municipality_look_up = {}
for municipality in municipalities:
    new_organisation = OrganisationWithDetails(
        name=municipality["name"],
        type_of_organisation=TypeOfOrganisationEnum.municipality,
        data_owner_of_municipalities=[municipality["gmcode"]]
    )
    new_organisation = db.create_organisation(organisation=new_organisation)
    db.create_historical_organisation_detail(organisation=new_organisation)
    municipality_look_up[municipality["gmcode"]] = new_organisation.organisation_id

# c. create organisation for users where it's unclear to what organisation they belong.
new_organisation = OrganisationWithDetails(
    name="Onbekend",
    type_of_organisation=TypeOfOrganisationEnum.other_company
)
new_organisation = db.create_organisation(organisation=new_organisation)
db.create_historical_organisation_detail(organisation=new_organisation)
unknown_organisation_id = new_organisation.organisation_id

# 2. Import users 
stmt = """
SELECT username, is_admin, is_contact_person_municipality, 
(
    SELECT array_agg(municipality) 
    FROM acl_municipalities 
    WHERE username = t1.username
) as municipalities,
(
    SELECT array_agg(operator) 
    FROM acl_operator 
    WHERE username = t1.username
) as operators
FROM acl as t1;
"""

users = query_rows(stmt)
for user in users:
    organisation_id = unknown_organisation_id
    priviliges = []
    if user["is_admin"]:
        organisation_id = admin_organisation_id
    elif user["municipalities"] and len(user["municipalities"]) == 1:
        municipality = user["municipalities"][0]
        organisation_id = municipality_look_up[municipality]
    elif user["operators"] and len(user["operators"]) == 1:
        operator = user["operators"][0]
        organisation_id = operator_look_up[operator]
    if user["is_contact_person_municipality"]:
        priviliges = [PrivilegesEnum.core_group, PrivilegesEnum.microhub_edit, PrivilegesEnum.download_raw_data, PrivilegesEnum.organisation_admin]

    new_user = UserAccount(
        user_id=user["username"],
        privileges=priviliges,
        organisation_id=organisation_id
    )
    user_db.create_user(new_user)

