import sys
import psycopg2

def apply_file(filepath: str, dbname: str = 'eroms_enterprise_db'):
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        user='eroms_admin',
        password='eroms_secure_password_2026',
        dbname=dbname
    )
    cur = conn.cursor()
    print(f"Applying '{filepath}' to '{dbname}'...")
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    cur.execute(sql)
    conn.commit()

    cur.execute("""
        SELECT count(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """)
    count = cur.fetchone()[0]
    print(f"SUCCESS! Currently {count} tables in '{dbname}'.")

    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cur.fetchall()]
    for i, t in enumerate(tables, 1):
        print(f"  {i:02d}. {t}")

    cur.close()
    conn.close()

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'sql/schema.sql'
    apply_file(target)
