from db_helper import db_helper
from user.user_account import UserAccount

def create_user(user_account: UserAccount):
    stmt = """
        INSERT INTO user_account (user_id, privileges, organisation_id) 
        VALUES (%(user_id)s, %(privileges)s, %(organisation_id)s);
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {"user_id": user_account.user_id, 
                               "privileges": user_account.privileges, 
                               "organisation_id": user_account.organisation_id
                                })
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        
def list_users(organisation_id: int):
    stmt = """
        SELECT organisation_id, user_id, privileges, name as organisation_name, type_of_organisation = 'ADMIN' as is_admin 
        FROM user_account 
        JOIN organisation USING(organisation_id) 
        WHERE true = %(filter_on_organisation_id)s OR organisation_id = %(organisation_id)s
        ORDER BY organisation_id, user_id;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {
                "filter_on_organisation_id": organisation_id == None, 
                "organisation_id": organisation_id
            })
            return cur.fetchall()
        except Exception as e:
            conn.rollback()
            print(e)
            return False