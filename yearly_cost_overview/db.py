from db_helper import db_helper
from user.user_account import UserAccount
from datetime import date

def query_yearly_cost_overview(reference_date: date):
    stmt = """
        SELECT name, number_of_vehicles
        FROM organisation
        JOIN
        (
            SELECT organisation_id, sum(value) as number_of_vehicles
            FROM
            organisation
            JOIN
                (SELECT * 
                FROM stats_pre_process 
                WHERE date = %(reference_date)s 
                AND stat_description = 'number_of_vehicles_available' 
                AND system_id is null
                ) q1
            ON right(zone_ref,-4) = ANY(data_owner_of_municipalities)
            WHERE
            type_of_organisation = 'MUNICIPALITY'
            GROUP BY organisation_id) q2
        USING (organisation_id)
        ORDER BY name;
    """
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt, 
            {   
                "reference_date": reference_date
            })
            return cur.fetchall()
        except Exception as e:
            print(e)
            conn.rollback()
            return False
        
