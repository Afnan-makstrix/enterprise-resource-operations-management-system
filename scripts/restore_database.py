"""
Universal Database Restore Utility for EROMS
Restores SQL backup dump files into target PostgreSQL database.
"""
import os
import sys
import psycopg2

def restore_db(dump_file: str, dbname: str = "eroms_enterprise_db"):
    if not os.path.exists(dump_file):
        print(f"ERROR: Dump file '{dump_file}' does not exist.")
        sys.exit(1)

    print(f"Connecting to database '{dbname}' on 127.0.0.1:5432...")
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="eroms_admin",
        password="eroms_secure_password_2026",
        dbname=dbname
    )
    cur = conn.cursor()

    print(f"Restoring from '{dump_file}'...")
    with open(dump_file, "r", encoding="utf-8") as f:
        sql = f.read()

    cur.execute(sql)
    conn.commit()

    cur.close()
    conn.close()
    print(f"SUCCESS: Database '{dbname}' restored successfully from '{dump_file}'!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python restore_database.py <path_to_dump.sql> [target_dbname]")
        sys.exit(1)
    target_file = sys.argv[1]
    target_db = sys.argv[2] if len(sys.argv) > 2 else "eroms_enterprise_db"
    restore_db(target_file, target_db)
