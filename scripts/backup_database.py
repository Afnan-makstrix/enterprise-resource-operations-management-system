"""
Universal Database Backup Utility for EROMS
Generates complete SQL schema and data dumps using psycopg2.
Compatible with any standard PostgreSQL server.
"""
import os
import sys
import psycopg2
from datetime import datetime

def backup_db(dbname="eroms_enterprise_db", output_dir="database/backups"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(output_dir, f"{dbname}_{timestamp}.sql")
    
    print(f"Connecting to '{dbname}' on 127.0.0.1:5432...")
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="eroms_admin",
        password="eroms_secure_password_2026",
        dbname=dbname
    )
    cur = conn.cursor()

    # Get all base tables in dependency-friendly order
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cur.fetchall()]

    print(f"Dumping {len(tables)} tables to '{backup_file}'...")
    total_records = 0

    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(f"-- ============================================================================\n")
        f.write(f"-- EROMS DATABASE BACKUP DUMP\n")
        f.write(f"-- Database: {dbname}\n")
        f.write(f"-- Timestamp: {timestamp}\n")
        f.write(f"-- Architect: Muhammad Afnan (https://github.com/Afnan-makstrix)\n")
        f.write(f"-- ============================================================================\n\n")
        f.write("SET statement_timeout = 0;\n")
        f.write("SET client_encoding = 'UTF8';\n")
        f.write("SET standard_conforming_strings = on;\n")
        f.write("SET check_function_bodies = false;\n\n")

        for table in tables:
            cur.execute(f"SELECT count(*) FROM {table};")
            count = cur.fetchone()[0]
            f.write(f"\n-- Data for table: {table} ({count} rows)\n")
            if count == 0:
                continue

            # Fetch columns
            cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position;
            """)
            columns = [row[0] for row in cur.fetchall()]
            col_list = ", ".join(columns)

            cur.execute(f"SELECT {col_list} FROM {table};")
            rows = cur.fetchall()
            total_records += len(rows)

            for row in rows:
                formatted_vals = []
                for val in row:
                    if val is None:
                        formatted_vals.append("NULL")
                    elif isinstance(val, (int, float)):
                        formatted_vals.append(str(val))
                    elif isinstance(val, bool):
                        formatted_vals.append("TRUE" if val else "FALSE")
                    else:
                        clean_str = str(val).replace("'", "''")
                        formatted_vals.append(f"'{clean_str}'")
                vals_str = ", ".join(formatted_vals)
                f.write(f"INSERT INTO {table} ({col_list}) VALUES ({vals_str}) ON CONFLICT DO NOTHING;\n")

    cur.close()
    conn.close()

    size_kb = os.path.getsize(backup_file) / 1024.0
    print(f"SUCCESS: Backup completed! Dumped {total_records} rows ({size_kb:.2f} KB) -> {backup_file}")
    return backup_file

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else "eroms_enterprise_db"
    backup_db(target)
