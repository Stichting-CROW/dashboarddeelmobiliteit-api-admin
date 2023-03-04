from db_helper import db_helper

def get_organisation_and_privileges(username):
    stmt = """
        SELECT organisation_id, privileges, type_of_organisation
        FROM user_account
        JOIN organisation
        USING (organisation_id)
        WHERE user_id = %(user_id)s;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, {"user_id": username})
            return cur.fetchone()
        except Exception as e:
            conn.rollback()
            print(e)

