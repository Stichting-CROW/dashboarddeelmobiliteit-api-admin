from db_helper import db_helper
from organisation.organisation import Organisation
from organisation.view_data_access import ViewDataAccessUser, ViewDataAccessOrganisation
import json

def create_organisation(organisation: Organisation):
    stmt = """
        INSERT INTO organisation (name, type_of_organisation, data_owner_of_municipalities, data_owner_of_operators, organisation_details) 
        VALUES (%(name)s, %(type_of_organisation)s, %(data_owner_of_municipalities)s, %(data_owner_of_operators)s, %(organisation_details)s)
        RETURNING organisation_id;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {
                "name": organisation.name, 
                "type_of_organisation": organisation.type_of_organisation, 
                "data_owner_of_municipalities": organisation.data_owner_of_municipalities,
                "data_owner_of_operators": organisation.data_owner_of_operators,
                "organisation_details": json.dumps(organisation.organisation_details)
            })
            conn.commit()
            organisation.organisation_id = cur.fetchone()["organisation_id"]
            return organisation
        except Exception as e:
            print(e)
            conn.rollback()
            return False

def create_view_data_access_organisation(view_data_access: ViewDataAccessOrganisation):
    stmt = """
        INSERT INTO view_data_access (owner_organisation_id, granted_organisation_id) 
        VALUES (%(owner_organisation_id)s, %(granted_organisation_id)s)
        RETURNING grant_view_data_id;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {
                "owner_organisation_id": view_data_access.owner_organisation_id, 
                "granted_organisation_id": view_data_access.granted_organisation_id,
            })
            conn.commit()
            view_data_access.grant_view_data_id = cur.fetchone()["grant_view_data_id"]
            return view_data_access
        except Exception as e:
            print(e)
            conn.rollback()
            return False

def create_view_data_access_user(view_data_access: ViewDataAccessUser):
    stmt = """
        INSERT INTO view_data_access (owner_organisation_id, granted_user) 
        VALUES (%(owner_organisation_id)s, %(granted_user)s)
        RETURNING grant_view_data_id;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {
                "owner_organisation_id": view_data_access.owner_organisation_id, 
                "granted_user": view_data_access.granted_user_id,
            })
            conn.commit()
            view_data_access.grant_view_data_id = cur.fetchone()["grant_view_data_id"]
            return view_data_access
        except Exception as e:
            print(e)
            conn.rollback()
            return False

def list_given_data_access(organisation_id: int):
    stmt = """
        SELECT grant_view_data_id, owner_organisation_id, j1.name as owner_organisation_name,
        granted_organisation_id, j2.name as granted_organisation_name, granted_user
        FROM view_data_access
        LEFT JOIN organisation j1
        ON owner_organisation_id = j1.organisation_id
        LEFT JOIN organisation j2
        ON granted_organisation_id = j2.organisation_id
        WHERE owner_organisation_id = %(owner_organisation_id)s;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {
                "owner_organisation_id": organisation_id, 
            })
            return cur.fetchall()
        except Exception as e:
            print(e)
            conn.rollback()
            return False
        
def list_received_data_access(organisation_id: int, user_id: str):
    stmt = """
        SELECT grant_view_data_id, owner_organisation_id, j1.name as owner_organisation_name,
        granted_organisation_id, j2.name as granted_organisation_name, granted_user
        FROM view_data_access 
        LEFT JOIN organisation j1
        ON owner_organisation_id = j1.organisation_id
        LEFT JOIN organisation j2
        ON granted_organisation_id = j2.organisation_id
        WHERE granted_organisation_id = %(granted_organisation_id)s
        OR granted_user = %(granted_user)s;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {
                "granted_organisation_id": organisation_id, 
                "granted_user": user_id
            })
            return cur.fetchall()
        except Exception as e:
            print(e)
            conn.rollback()
            return False

def check_if_organisation_has_users(organisation_id: int):
    stmt = """
        SELECT count(*) as number_of_users
        FROM user_account
        WHERE organisation_id = %(organisation_id)s
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {"organisation_id": organisation_id})
            return cur.fetchone()["number_of_users"] > 0
        except Exception as e:
            conn.rollback()
            return True
        
def check_if_organisation_has_granted_data_access(organisation_id: int):
    stmt = """
        SELECT count(*) as granted_data_access_count
        FROM view_data_access
        WHERE owner_organisation_id = %(organisation_id)s
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {"organisation_id": organisation_id})
            return cur.fetchone()["granted_data_access_count"] > 0
        except Exception as e:
            conn.rollback()
            return True
        
def delete_organisation(organisation_id: int):
    stmt = """
        DELETE
        FROM organisation
        WHERE organisation_id = %(organisation_id)s
        RETURNING *
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {"organisation_id": organisation_id})
            conn.commit()
            return cur.fetchone() != None
        except Exception as e:
            conn.rollback()
            return False

def list_organisations():
    stmt = """
        SELECT organisation_id, name, type_of_organisation, 
        data_owner_of_municipalities, data_owner_of_operators 
        FROM organisation
        ORDER BY name;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt)
            return cur.fetchall()
        except Exception as e:
            conn.rollback()
            print(e)
            return False