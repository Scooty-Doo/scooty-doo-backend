import psycopg

def run_sql_file(conn, sql_file_path):
    """
    Run a SQL file using psycopg.

    Parameters:
    conn (psycopg.Connection): The connection object to the PostgreSQL database.
    sql_file_path (str): The path to the SQL file.
    """
    with open(sql_file_path, 'r') as file:
        sql = file.read()

    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()


sql_file_path = '../schema/schema.sql'

with psycopg.connect(
    dbname="sddb",
    user="user",
    password="pass",
    host="localhost",
    port="5432"
) as conn:
    run_sql_file(conn, sql_file_path)