import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_postgres():
    conn = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', dbname='postgres')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Create role eroms_admin if not exists
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = 'eroms_admin'")
    if not cur.fetchone():
        cur.execute("CREATE ROLE eroms_admin WITH LOGIN SUPERUSER PASSWORD 'eroms_secure_password_2026'")
        print("Created role: eroms_admin")
    else:
        print("Role eroms_admin already exists")

    # Create eroms_enterprise_db
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'eroms_enterprise_db'")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE eroms_enterprise_db OWNER eroms_admin")
        print("Created database: eroms_enterprise_db")
    else:
        print("Database eroms_enterprise_db already exists")

    # Create eroms_test_db
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'eroms_test_db'")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE eroms_test_db OWNER eroms_admin")
        print("Created database: eroms_test_db")
    else:
        print("Database eroms_test_db already exists")

    cur.close()
    conn.close()

    # Verify connection as eroms_admin
    conn2 = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        user='eroms_admin',
        password='eroms_secure_password_2026',
        dbname='eroms_enterprise_db'
    )
    cur2 = conn2.cursor()
    cur2.execute("SELECT current_user, current_database(), version()")
    user, db, ver = cur2.fetchone()
    print(f"SUCCESS: Connected as '{user}' to '{db}' running {ver.split(',')[0]}")
    cur2.close()
    conn2.close()

if __name__ == '__main__':
    init_postgres()
