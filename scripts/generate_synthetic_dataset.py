"""
Enterprise Resource & Operations Management System (EROMS)
High-Performance Synthetic Data Generator
Architect: Muhammad Afnan (https://github.com/Afnan-makstrix)

Generates:
- 10,000+ Employees & Profiles
- 50,000+ Attendance Records
- 20,000+ Financial Payments & Transactions
- 5,000+ Sales Invoices & Line Items
- 10,000+ Inventory Transactions & Movements
- 1,500+ Projects & Tasks
- Complete RBAC & Organization Structure
"""
import sys
import random
import time
from datetime import date, datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

def generate_enterprise_data(dbname="eroms_enterprise_db"):
    print(f"\n" + "="*80)
    print(f"EROMS SYNTHETIC ENTERPRISE DATASET GENERATION")
    print(f"Target Database: {dbname} on 127.0.0.1:5432")
    print(f"Architect: Muhammad Afnan (https://github.com/Afnan-makstrix)")
    print("="*80 + "\n")

    t_start = time.time()
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="eroms_admin",
        password="eroms_secure_password_2026",
        dbname=dbname
    )
    conn.autocommit = False
    cur = conn.cursor()

    print("Cleaning existing business data for clean reproducible run...")
    cur.execute("""
        TRUNCATE TABLE 
            financial_payments, invoice_items, sales_invoices, 
            task_time_logs, project_tasks, project_members, projects, 
            purchase_order_items, purchase_orders, inventory_transactions, 
            warehouse_stocks, inventory_items, warehouses, suppliers, clients, 
            payrolls, salary_structures, attendance_records, leave_requests, 
            leave_balances, employee_profiles, user_credentials, employees
        CASCADE;
    """)
    conn.commit()

    # ---------------------------------------------------------
    # 1. ROLES & PERMISSIONS
    # ---------------------------------------------------------
    print("[1/12] Seeding Roles and Granular RBAC Permissions...")
    roles_data = [
        ("Super Admin", "Full system unrestricted access", True),
        ("Admin", "General administrative privileges", True),
        ("Department Manager", "Departmental supervision and approval rights", False),
        ("Project Manager", "Project planning, task assignment, and delivery tracking", False),
        ("Senior Engineer", "Core engineering execution and technical review", False),
        ("Staff Engineer", "Engineering execution and task reporting", False),
        ("HR Manager", "Personnel management, leave policies, and onboarding", False),
        ("Finance Manager", "Accounting, invoices, payroll, and payments", False),
        ("Procurement Specialist", "Purchasing and supplier management", False),
        ("Inventory Specialist", "Warehouse stock tracking and transfers", False),
    ]
    cur.executemany("""
        INSERT INTO roles (role_name, description, is_system) 
        VALUES (%s, %s, %s) ON CONFLICT (role_name) DO NOTHING;
    """, roles_data)
    conn.commit()

    cur.execute("SELECT role_id, role_name FROM roles;")
    role_map = {row[1]: row[0] for row in cur.fetchall()}

    modules = ["employees", "departments", "projects", "tasks", "attendance", "leaves", "payroll", "inventory", "purchasing", "sales", "finance", "audit"]
    actions = ["view", "create", "edit", "delete", "approve", "export"]
    perms_data = [(f"{m}:{a}", m, a, f"Permission to {a} {m}") for m in modules for a in actions]
    execute_values(cur, """
        INSERT INTO permissions (permission_code, module_name, action, description)
        VALUES %s ON CONFLICT (permission_code) DO NOTHING;
    """, perms_data)
    conn.commit()

    cur.execute("SELECT permission_id FROM permissions;")
    perm_ids = [row[0] for row in cur.fetchall()]
    admin_role_id = role_map["Super Admin"]
    rp_data = [(admin_role_id, pid) for pid in perm_ids]
    execute_values(cur, """
        INSERT INTO role_permissions (role_id, permission_id)
        VALUES %s ON CONFLICT DO NOTHING;
    """, rp_data)
    conn.commit()

    # ---------------------------------------------------------
    # 2. DEPARTMENTS
    # ---------------------------------------------------------
    print("[2/12] Seeding Corporate Departments...")
    depts_data = [
        ("EXEC", "Executive Leadership", "C-suite management & corporate governance", 2500000.00, "Headquarters Tower A"),
        ("ENG", "Software Engineering", "Core platform and infrastructure development", 5000000.00, "Headquarters Tower B"),
        ("PROD", "Product Management", "Product discovery and roadmap management", 1500000.00, "Headquarters Tower B"),
        ("FIN", "Finance & Accounting", "Treasury, bookkeeping, payroll, and audits", 1800000.00, "Headquarters Tower A"),
        ("HR", "Human Resources", "Talent acquisition, benefits, and workplace ops", 1200000.00, "Headquarters Tower A"),
        ("SALES", "Sales & Business Development", "Enterprise partnerships and client acquisition", 3500000.00, "Regional Office East"),
        ("MKTG", "Marketing & Growth", "Demand generation and brand awareness", 2000000.00, "Regional Office East"),
        ("OPS", "Global Operations", "Facilities, IT support, and business continuity", 1600000.00, "Headquarters Tower C"),
        ("SCM", "Supply Chain & Logistics", "Warehouse operations and vendor logistics", 2800000.00, "Central Logistics Hub"),
        ("LEGAL", "Legal & Compliance", "Contracts, risk governance, and IP defense", 1100000.00, "Headquarters Tower A")
    ]
    cur.executemany("""
        INSERT INTO departments (department_code, name, description, budget, location)
        VALUES (%s, %s, %s, %s, %s) ON CONFLICT (department_code) DO NOTHING;
    """, depts_data)
    conn.commit()

    cur.execute("SELECT department_id, department_code FROM departments;")
    dept_map = {row[1]: row[0] for row in cur.fetchall()}
    dept_ids = list(dept_map.values())

    # ---------------------------------------------------------
    # 3. LEAVE TYPES
    # ---------------------------------------------------------
    print("[3/12] Seeding Leave Types...")
    leave_types_data = [
        ("Annual Vacation", "VAC", 20, True, True, "Standard accrued paid annual vacation"),
        ("Sick Leave", "SCK", 12, True, False, "Paid medical and personal illness leave"),
        ("Casual Leave", "CSL", 8, True, False, "Short emergency and casual leave"),
        ("Maternity / Paternity", "PAR", 60, True, False, "Parental bonding leave"),
        ("Unpaid Sabbatical", "UNP", 30, False, False, "Unpaid personal extended sabbatical")
    ]
    cur.executemany("""
        INSERT INTO leave_types (name, code, annual_allowance, is_paid, carry_forward, description)
        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (code) DO NOTHING;
    """, leave_types_data)
    conn.commit()
    cur.execute("SELECT leave_type_id FROM leave_types;")
    leave_type_ids = [row[0] for row in cur.fetchall()]

    # ---------------------------------------------------------
    # 4. 10,000+ EMPLOYEES & CREDENTIALS & SALARIES
    # ---------------------------------------------------------
    print("[4/12] Generating 10,000+ Employees with Organizational Hierarchy...")
    
    # Tier 1: 10 Executives (Managers for departments)
    exec_data = []
    job_titles_exec = ["Chief Executive Officer", "Chief Technology Officer", "Chief Financial Officer", "Chief Operating Officer", "VP Engineering", "VP Sales", "VP Product", "Chief HR Officer", "VP Supply Chain", "General Counsel"]
    
    # Common bcrypt hash for testing (password: "Password123!")
    # Precomputed standard bcrypt hash to avoid 10,000 slow bcrypt hashing rounds:
    test_pw_hash = "$2b$12$e80yE6kP8r.o3qX3bKkW2eN8Qp/C8o7J7M6bH4T4M/5X5s0Q3QYy2"

    for i in range(10):
        emp_num = f"EMP-{1000 + i:05d}"
        fn = fake.first_name()
        ln = fake.last_name()
        email = f"{fn.lower()}.{ln.lower()}{i}@eroms-enterprise.com"
        phone = fake.phone_number()[:25]
        job = job_titles_exec[i]
        d_id = dept_ids[i % len(dept_ids)]
        r_id = role_map["Super Admin"] if i == 0 else role_map["Admin"]
        hire_d = date(2018, 1, 15) + timedelta(days=i*60)
        salary = 180000.00 + (i * 12000.00)
        exec_data.append((emp_num, fn, ln, email, phone, job, d_id, None, r_id, hire_d, salary, 'FULL_TIME', 'ACTIVE', False))

    execute_values(cur, """
        INSERT INTO employees (
            employee_number, first_name, last_name, email, phone, job_title,
            department_id, manager_id, role_id, hire_date, salary, employment_type, status, is_deleted
        ) VALUES %s RETURNING employee_id;
    """, exec_data)
    exec_ids = [row[0] for row in cur.fetchall()]
    conn.commit()

    # Set department managers
    for idx, d_id in enumerate(dept_ids[:len(exec_ids)]):
        cur.execute("UPDATE departments SET manager_id = %s WHERE department_id = %s;", (exec_ids[idx], d_id))
    conn.commit()

    # Tier 2: 200 Department Managers & Leads
    lead_data = []
    for i in range(200):
        emp_num = f"EMP-{2000 + i:05d}"
        fn = fake.first_name()
        ln = fake.last_name()
        email = f"{fn.lower()}.{ln.lower()}{2000+i}@eroms-enterprise.com"
        phone = fake.phone_number()[:25]
        job = random.choice(["Engineering Director", "Senior Engineering Manager", "Finance Lead", "HR Business Partner", "Regional Sales Director", "Supply Chain Lead", "Product Group Manager"])
        d_id = random.choice(dept_ids)
        m_id = random.choice(exec_ids)
        r_id = role_map["Department Manager"]
        hire_d = date(2019, 3, 1) + timedelta(days=random.randint(0, 1200))
        salary = random.randint(110000, 165000)
        lead_data.append((emp_num, fn, ln, email, phone, job, d_id, m_id, r_id, hire_d, salary, 'FULL_TIME', 'ACTIVE', False))

    execute_values(cur, """
        INSERT INTO employees (
            employee_number, first_name, last_name, email, phone, job_title,
            department_id, manager_id, role_id, hire_date, salary, employment_type, status, is_deleted
        ) VALUES %s RETURNING employee_id;
    """, lead_data)
    lead_ids = [row[0] for row in cur.fetchall()]
    conn.commit()

    # Tier 3: 9,800 Staff Employees (Reaching 10,010 total employees)
    total_staff = 9800
    batch_size = 2000
    all_employee_ids = list(exec_ids) + list(lead_ids)

    tech_titles = ["Software Engineer", "Backend Developer", "Frontend Developer", "DevOps Engineer", "Data Engineer", "QA Specialist", "Security Analyst", "System Architect", "Solutions Consultant"]
    biz_titles = ["Financial Analyst", "Accountant", "HR Coordinator", "Talent Recruiter", "Account Executive", "Business Development Rep", "Logistics Coordinator", "Warehouse Operations Specialist", "Customer Success Manager"]

    print(f"  Generating {total_staff} staff records in bulk batches...")
    for b in range(0, total_staff, batch_size):
        cur_batch_size = min(batch_size, total_staff - b)
        staff_data = []
        for i in range(cur_batch_size):
            seq = 10000 + b + i
            emp_num = f"EMP-{seq:06d}"
            fn = fake.first_name()
            ln = fake.last_name()
            email = f"emp.{seq}@eroms-work.com"
            phone = fake.phone_number()[:25]
            d_id = random.choice(dept_ids)
            m_id = random.choice(lead_ids)
            
            if d_id == dept_map["ENG"]:
                job = random.choice(tech_titles)
                r_id = random.choice([role_map["Senior Engineer"], role_map["Staff Engineer"]])
                salary = random.randint(75000, 140000)
            elif d_id == dept_map["FIN"]:
                job = random.choice(["Financial Analyst", "Junior Accountant", "Senior Accountant"])
                r_id = role_map["Finance Manager"] if random.random() < 0.1 else role_map["Staff Engineer"]
                salary = random.randint(60000, 110000)
            elif d_id == dept_map["SCM"]:
                job = random.choice(["Warehouse Specialist", "Logistics Clerk", "Procurement Associate"])
                r_id = role_map["Inventory Specialist"] if random.random() < 0.5 else role_map["Procurement Specialist"]
                salary = random.randint(48000, 85000)
            else:
                job = random.choice(biz_titles)
                r_id = role_map["Staff Engineer"]
                salary = random.randint(52000, 98000)

            hire_d = date(2020, 1, 1) + timedelta(days=random.randint(0, 2100))
            emp_type = random.choice(["FULL_TIME", "FULL_TIME", "FULL_TIME", "CONTRACT"])
            status = random.choices(["ACTIVE", "ON_LEAVE", "TERMINATED"], weights=[92, 5, 3])[0]
            is_del = (status == "TERMINATED")
            staff_data.append((emp_num, fn, ln, email, phone, job, d_id, m_id, r_id, hire_d, salary, emp_type, status, is_del))

        execute_values(cur, """
            INSERT INTO employees (
                employee_number, first_name, last_name, email, phone, job_title,
                department_id, manager_id, role_id, hire_date, salary, employment_type, status, is_deleted
            ) VALUES %s;
        """, staff_data, page_size=2000)
        conn.commit()
        print(f"    Committed batch of {cur_batch_size} staff records...")

    cur.execute("SELECT employee_id FROM employees WHERE is_deleted = FALSE ORDER BY employee_id;")
    all_employee_ids = [row[0] for row in cur.fetchall()]
    print(f"  Total active employee IDs loaded: {len(all_employee_ids)}")

    # Seed Admin User Credentials
    cur.execute("""
        INSERT INTO user_credentials (employee_id, username, password_hash)
        VALUES (%s, 'admin', %s) ON CONFLICT (username) DO NOTHING;
    """, (exec_ids[0], test_pw_hash))
    conn.commit()

    # ---------------------------------------------------------
    # 5. CLIENTS & SUPPLIERS
    # ---------------------------------------------------------
    print("[5/12] Seeding 1,000 Clients and 500 Suppliers...")
    clients_data = []
    for c_i in range(1000):
        code = f"CLI-{1000 + c_i:05d}"
        comp = f"{fake.company()} {fake.company_suffix()}"
        cp = fake.name()
        em = f"contact{c_i}@clientcorp{c_i}.com"
        ph = fake.phone_number()[:25]
        addr = fake.street_address()
        city = fake.city()
        cred = random.choice([25000, 50000, 100000, 250000, 500000])
        clients_data.append((code, comp, cp, em, ph, addr, city, cred, 'ACTIVE'))

    execute_values(cur, """
        INSERT INTO clients (client_code, company_name, contact_person, email, phone, billing_address, city, credit_limit, status)
        VALUES %s RETURNING client_id;
    """, clients_data)
    client_ids = [row[0] for row in cur.fetchall()]
    conn.commit()

    suppliers_data = []
    for s_i in range(500):
        code = f"SUP-{1000 + s_i:05d}"
        comp = f"{fake.company()} Supplies & Logistics"
        cp = fake.name()
        em = f"sales{s_i}@supplierpartner{s_i}.com"
        ph = fake.phone_number()[:25]
        tax_id = f"TAX-US-{10000000 + s_i}"
        terms = random.choice(["NET_15", "NET_30", "NET_60"])
        addr = fake.street_address()
        city = fake.city()
        rating = round(random.uniform(3.5, 5.0), 2)
        suppliers_data.append((code, comp, cp, em, ph, tax_id, terms, addr, city, rating, 'ACTIVE'))

    execute_values(cur, """
        INSERT INTO suppliers (supplier_code, company_name, contact_person, email, phone, tax_identification_number, payment_terms, address, city, rating, status)
        VALUES %s RETURNING supplier_id;
    """, suppliers_data)
    supplier_ids = [row[0] for row in cur.fetchall()]
    conn.commit()

    # ---------------------------------------------------------
    # 6. PRODUCT CATEGORIES, INVENTORY ITEMS & WAREHOUSES
    # ---------------------------------------------------------
    print("[6/12] Seeding Product Categories, 1,000 Inventory Items, & 5 Warehouses...")
    categories_data = [
        ("CAT-IT-HW", "IT Hardware & Server Equipment", None),
        ("CAT-NET", "Enterprise Networking & Telephony", None),
        ("CAT-OFFICE", "Office & Ergonomic Furniture", None),
        ("CAT-IND-TOOL", "Industrial Tools & Machinery", None),
        ("CAT-RAW-ELEC", "Raw Electronic Components & PCB", None),
        ("CAT-PACK", "Packaging & Dispatch Supplies", None),
        ("CAT-SAFETY", "Workplace Safety & PPE Gear", None)
    ]
    cur.executemany("""
        INSERT INTO product_categories (category_code, name, description)
        VALUES (%s, %s, %s) ON CONFLICT (category_code) DO NOTHING;
    """, categories_data)
    conn.commit()
    cur.execute("SELECT category_id FROM product_categories;")
    cat_ids = [row[0] for row in cur.fetchall()]

    warehouses_data = [
        ("WH-NA-01", "North American Central Fulfillment Hub", "Chicago, IL", 50000, exec_ids[3]),
        ("WH-WE-02", "West Coast Distribution Facility", "Reno, NV", 35000, lead_ids[0]),
        ("WH-EC-03", "East Coast Logistics Port", "Newark, NJ", 40000, lead_ids[1]),
        ("WH-EU-04", "European Central Depository", "Frankfurt, Germany", 45000, lead_ids[2]),
        ("WH-AP-05", "Asia-Pacific Regional Depot", "Singapore", 30000, lead_ids[3])
    ]
    cur.executemany("""
        INSERT INTO warehouses (warehouse_code, name, location, capacity, manager_id)
        VALUES (%s, %s, %s, %s, %s) ON CONFLICT (warehouse_code) DO NOTHING;
    """, warehouses_data)
    conn.commit()
    cur.execute("SELECT warehouse_id FROM warehouses;")
    warehouse_ids = [row[0] for row in cur.fetchall()]

    items_data = []
    item_nouns = ["Switch", "Router", "Optic Cable", "Rack Cabinet", "Display Monitor", "Ergonomic Chair", "Sensor Module", "Power Inverter", "Microcontroller", "Docking Station", "Transceiver", "Battery Pack"]
    for it_i in range(1200):
        sku = f"SKU-{10000 + it_i:06d}"
        noun = random.choice(item_nouns)
        name = f"Enterprise Pro {noun} Series {random.randint(100, 999)}"
        desc = f"Heavy duty commercial grade {name} with automated telemetry."
        cat_id = random.choice(cat_ids)
        cost = round(random.uniform(20.0, 1500.0), 2)
        sell = round(cost * random.uniform(1.25, 2.10), 2)
        qty = random.randint(15, 800)
        reorder_lvl = random.choice([20, 30, 50, 100])
        reorder_qty = reorder_lvl * 3
        items_data.append((sku, name, desc, cat_id, 'UNIT', cost, sell, qty, reorder_lvl, reorder_qty, True))

    execute_values(cur, """
        INSERT INTO inventory_items (sku, name, description, category_id, unit_of_measure, cost_price, selling_price, total_quantity_on_hand, reorder_level, reorder_quantity, is_active)
        VALUES %s RETURNING item_id;
    """, items_data)
    item_ids = [row[0] for row in cur.fetchall()]
    conn.commit()

    # Seed initial stocks per warehouse
    stock_rows = []
    for wh_id in warehouse_ids:
        for it_id in item_ids[:600]:
            stock_rows.append((wh_id, it_id, random.randint(10, 250), f"Aisle-{random.randint(1,20)}-Bin-{random.randint(1,50)}"))
    execute_values(cur, """
        INSERT INTO warehouse_stocks (warehouse_id, item_id, quantity, bin_location)
        VALUES %s ON CONFLICT (warehouse_id, item_id) DO NOTHING;
    """, stock_rows)
    conn.commit()

    # ---------------------------------------------------------
    # 7. 10,000+ INVENTORY TRANSACTIONS / MOVEMENTS
    # ---------------------------------------------------------
    print("[7/12] Generating 10,000+ Inventory Transactions / Stock Movements...")
    inv_trans_data = []
    trans_types = ["PURCHASE_RECEIPT", "SALE_DISPATCH", "TRANSFER", "ADJUSTMENT", "RETURN"]
    for t_i in range(12000):
        ttype = random.choice(trans_types)
        it_id = random.choice(item_ids)
        wh_id = random.choice(warehouse_ids)
        dest_wh = random.choice(warehouse_ids) if ttype == "TRANSFER" else None
        qty = random.randint(5, 100) if ttype in ("PURCHASE_RECEIPT", "RETURN") else -random.randint(1, 50)
        ucost = round(random.uniform(25.0, 500.0), 2)
        ref_type = "PURCHASE_ORDER" if ttype == "PURCHASE_RECEIPT" else "SALES_INVOICE" if ttype == "SALE_DISPATCH" else "STOCK_TRANSFER"
        ref_id = f"REF-{100000 + t_i}"
        t_date = datetime.now() - timedelta(days=random.randint(1, 360), minutes=random.randint(0, 1440))
        by_emp = random.choice(lead_ids)
        notes = f"Batch transaction {t_i} movement recorded in ledger."
        inv_trans_data.append((ttype, it_id, wh_id, dest_wh, qty, ucost, ref_type, ref_id, notes, by_emp, t_date))

    execute_values(cur, """
        INSERT INTO inventory_transactions (
            transaction_type, item_id, warehouse_id, destination_warehouse_id,
            quantity, unit_cost, reference_type, reference_id, notes, created_by, transaction_date
        ) VALUES %s;
    """, inv_trans_data)
    conn.commit()

    # ---------------------------------------------------------
    # 8. 50,000+ ATTENDANCE RECORDS
    # ---------------------------------------------------------
    print("[8/12] Generating 50,000+ Daily Attendance Records...")
    # Sample 1,000 active employees across 55 working days
    sample_emps = random.sample(all_employee_ids, 1000)
    attendance_data = []
    base_date = date.today() - timedelta(days=75)
    
    day_count = 0
    cur_d = base_date
    valid_workdays = []
    while len(valid_workdays) < 55:
        if cur_d.weekday() < 5:  # Monday to Friday
            valid_workdays.append(cur_d)
        cur_d += timedelta(days=1)

    for w_date in valid_workdays:
        for emp_id in sample_emps:
            st = random.choices(["PRESENT", "PRESENT", "PRESENT", "LATE", "HALF_DAY", "ON_LEAVE"], weights=[82, 5, 4, 4, 3, 2])[0]
            if st == "PRESENT":
                cin = datetime.combine(w_date, datetime.min.time()) + timedelta(hours=8, minutes=random.randint(45, 59))
                cout = datetime.combine(w_date, datetime.min.time()) + timedelta(hours=17, minutes=random.randint(0, 45))
                hw = round(random.uniform(8.0, 9.5), 2)
                ot = round(max(0.0, hw - 8.0), 2)
            elif st == "LATE":
                cin = datetime.combine(w_date, datetime.min.time()) + timedelta(hours=9, minutes=random.randint(20, 55))
                cout = datetime.combine(w_date, datetime.min.time()) + timedelta(hours=17, minutes=random.randint(0, 30))
                hw = round(random.uniform(7.0, 8.0), 2)
                ot = 0.0
            elif st == "HALF_DAY":
                cin = datetime.combine(w_date, datetime.min.time()) + timedelta(hours=9, minutes=0)
                cout = datetime.combine(w_date, datetime.min.time()) + timedelta(hours=13, minutes=0)
                hw = 4.00
                ot = 0.0
            else: # ON_LEAVE
                cin, cout = None, None
                hw, ot = 0.0, 0.0

            ip = f"192.168.10.{random.randint(2, 254)}"
            attendance_data.append((emp_id, w_date, cin, cout, st, hw, ot, ip, "Badge scan automated"))

    # Bulk insert attendance in chunks
    att_batch_size = 10000
    for a_idx in range(0, len(attendance_data), att_batch_size):
        chunk = attendance_data[a_idx:a_idx + att_batch_size]
        execute_values(cur, """
            INSERT INTO attendance_records (
                employee_id, work_date, check_in, check_out, status, hours_worked, overtime_hours, ip_address, notes
            ) VALUES %s ON CONFLICT (employee_id, work_date) DO NOTHING;
        """, chunk)
        conn.commit()
    print(f"  Inserted {len(attendance_data)} attendance records!")

    # ---------------------------------------------------------
    # 9. PROJECTS, MEMBERS & TASKS
    # ---------------------------------------------------------
    print("[9/12] Generating Projects, Project Members, and Work Breakdown Tasks...")
    projects_data = []
    p_names = ["Enterprise Cloud Modernization", "Global Supply Chain Automation", "NextGen ERP Implementation", "AI Predictive Analytics Suite", "Zero Trust Cyber Defense Architecture", "Customer 360 CRM Overhaul", "Automated Financial Settlement Portal", "Real-Time Telemetry Data Lake"]
    
    for pr_i in range(1200):
        pcode = f"PRJ-{1000 + pr_i:05d}"
        pname = f"{random.choice(p_names)} Phase {random.randint(1, 4)}"
        desc = f"Strategic organizational initiative {pcode}: {pname}."
        cl_id = random.choice(client_ids)
        pm_id = random.choice(lead_ids)
        sdate = date(2023, 1, 1) + timedelta(days=random.randint(0, 600))
        edate = sdate + timedelta(days=random.randint(90, 365))
        budget = random.choice([75000, 150000, 300000, 600000, 1200000])
        cost = budget * random.uniform(0.3, 0.95)
        st = random.choice(["PLANNING", "IN_PROGRESS", "IN_PROGRESS", "COMPLETED", "ON_HOLD"])
        prio = random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        projects_data.append((pcode, pname, desc, cl_id, pm_id, sdate, edate, budget, cost, st, prio))

    execute_values(cur, """
        INSERT INTO projects (
            project_code, name, description, client_id, project_manager_id,
            start_date, target_end_date, budget, cost_to_date, status, priority
        ) VALUES %s RETURNING project_id;
    """, projects_data)
    project_ids = [row[0] for row in cur.fetchall()]
    conn.commit()

    # Seed Project Tasks
    tasks_data = []
    task_types = ["Architecture Spec", "Database Modeling", "API Endpoint Implementation", "Security Penetration Test", "Frontend UI Integration", "Load Testing Benchmark", "User Acceptance Sign-off", "Disaster Recovery Drill"]
    for tk_i in range(8000):
        tcode = f"TSK-{10000 + tk_i:06d}"
        pr_id = random.choice(project_ids)
        title = f"{random.choice(task_types)} for Module {random.randint(1, 20)}"
        desc = f"Technical task assignment {tcode}: {title}."
        assigned = random.choice(all_employee_ids[:2000])
        reporter = random.choice(lead_ids)
        prio = random.choice(["LOW", "MEDIUM", "HIGH", "URGENT"])
        st = random.choice(["TODO", "IN_PROGRESS", "IN_REVIEW", "DONE", "DONE"])
        est_h = random.choice([8.0, 16.0, 24.0, 40.0, 80.0])
        act_h = est_h * random.uniform(0.7, 1.3) if st == "DONE" else est_h * 0.4
        due_d = date.today() + timedelta(days=random.randint(-30, 90))
        tasks_data.append((tcode, pr_id, title, desc, assigned, reporter, prio, st, est_h, act_h, due_d))

    execute_values(cur, """
        INSERT INTO project_tasks (
            task_code, project_id, title, description, assigned_to, reporter_id,
            priority, status, estimated_hours, actual_hours, due_date
        ) VALUES %s RETURNING task_id;
    """, tasks_data)
    conn.commit()

    # ---------------------------------------------------------
    # 10. 5,000+ SALES INVOICES & 15,000+ LINE ITEMS
    # ---------------------------------------------------------
    print("[10/12] Generating 5,000+ Sales Invoices & Line Items...")
    invoices_data = []
    for inv_i in range(5500):
        inv_num = f"INV-{10000 + inv_i:06d}"
        cl_id = random.choice(client_ids)
        pr_id = random.choice(project_ids) if random.random() < 0.6 else None
        issue_d = date(2023, 6, 1) + timedelta(days=random.randint(0, 500))
        due_d = issue_d + timedelta(days=30)
        subtotal = round(random.uniform(1500.0, 45000.0), 2)
        tax_rt = 10.00
        tax_amt = round(subtotal * 0.10, 2)
        disc = round(random.choice([0.0, 0.0, 100.0, 250.0, 500.0]), 2)
        tot = subtotal + tax_amt - disc
        
        # Payment status distribution
        p_roll = random.random()
        if p_roll < 0.70:
            pst = "PAID"
            paid = tot
        elif p_roll < 0.88:
            pst = "PARTIALLY_PAID"
            paid = round(tot * random.uniform(0.2, 0.7), 2)
        else:
            pst = "UNPAID"
            paid = 0.00

        by_emp = random.choice(lead_ids)
        invoices_data.append((inv_num, cl_id, pr_id, issue_d, due_d, subtotal, tax_rt, tax_amt, disc, tot, paid, pst, by_emp))

    execute_values(cur, """
        INSERT INTO sales_invoices (
            invoice_number, client_id, project_id, issue_date, due_date,
            subtotal, tax_rate, tax_amount, discount_amount, total_amount, paid_amount, payment_status, created_by
        ) VALUES %s;
    """, invoices_data, page_size=2000)
    conn.commit()

    cur.execute("SELECT invoice_id, total_amount, paid_amount, client_id FROM sales_invoices ORDER BY invoice_id;")
    inv_results = cur.fetchall()
    invoice_ids = [r[0] for r in inv_results]

    # Generate invoice line items (multiple line items per invoice)
    inv_items_data = []
    for inv_id in invoice_ids:
        for _ in range(random.randint(2, 4)):
            it_id = random.choice(item_ids)
            qty = random.randint(1, 10)
            up = round(random.uniform(50.0, 1200.0), 2)
            inv_items_data.append((inv_id, it_id, f"Line item deliverable for Invoice #{inv_id}", qty, up))
    
    execute_values(cur, """
        INSERT INTO invoice_items (invoice_id, item_id, description, quantity, unit_price)
        VALUES %s;
    """, inv_items_data, page_size=5000)
    conn.commit()
    print(f"  Inserted {len(inv_items_data)} invoice line items across {len(invoice_ids)} invoices!")

    # ---------------------------------------------------------
    # 11. 20,000+ FINANCIAL PAYMENTS & TRANSACTIONS
    # ---------------------------------------------------------
    print("[11/12] Generating 20,000+ Financial Payments (Receipts, Disbursements & Payroll)...")
    payments_data = []
    pay_methods = ["BANK_TRANSFER", "AUTOMATED_CLEARING", "CREDIT_CARD", "CHECK"]

    # Customer Receipts (from invoices)
    for inv_rec in inv_results:
        inv_id, tot, paid, cl_id = inv_rec
        if paid > 0:
            p_num = f"PAY-REC-{inv_id:06d}"
            pmeth = random.choice(pay_methods)
            pref = f"TXN-ACH-{fake.uuid4()[:16]}"
            pdate = datetime.now() - timedelta(days=random.randint(1, 400))
            by_emp = random.choice(lead_ids)
            payments_data.append((p_num, 'CUSTOMER_RECEIPT', inv_id, None, None, paid, pmeth, pref, pdate, 'Customer payment received via clearing house', by_emp))

    # Vendor Disbursements (9,000 records)
    for vd_i in range(9000):
        p_num = f"PAY-VND-{10000 + vd_i:06d}"
        amt = round(random.uniform(500.0, 35000.0), 2)
        pmeth = random.choice(pay_methods)
        pref = f"TXN-WIRE-{fake.uuid4()[:16]}"
        pdate = datetime.now() - timedelta(days=random.randint(1, 400))
        by_emp = random.choice(lead_ids)
        payments_data.append((p_num, 'VENDOR_DISBURSEMENT', None, None, None, amt, pmeth, pref, pdate, 'Vendor supply settlement disbursement', by_emp))

    # Seed payroll disbursements (8,000 records)
    for pr_i in range(8000):
        p_num = f"PAY-PRL-{10000 + pr_i:06d}"
        amt = round(random.uniform(3500.0, 12000.0), 2)
        pref = f"TXN-DIRDEP-{fake.uuid4()[:16]}"
        pdate = datetime.now() - timedelta(days=random.randint(1, 365))
        by_emp = random.choice(lead_ids)
        payments_data.append((p_num, 'PAYROLL_DISBURSEMENT', None, None, None, amt, 'BANK_TRANSFER', pref, pdate, 'Monthly employee direct deposit', by_emp))

    print(f"  Inserting {len(payments_data)} payments in batches...")
    pay_batch_size = 5000
    for p_idx in range(0, len(payments_data), pay_batch_size):
        chunk = payments_data[p_idx:p_idx + pay_batch_size]
        execute_values(cur, """
            INSERT INTO financial_payments (
                payment_number, payment_type, invoice_id, po_id, payroll_id,
                amount, payment_method, transaction_reference, payment_date, notes, processed_by
            ) VALUES %s;
        """, chunk)
        conn.commit()

    # ---------------------------------------------------------
    # 12. AUDIT LOGS, NOTIFICATIONS & REFRESH MATERIALIZED VIEWS
    # ---------------------------------------------------------
    print("[12/12] Seeding System Notifications & Refreshing Materialized Views...")
    notifications_data = []
    for n_i in range(1500):
        rec_id = random.choice(all_employee_ids[:2000])
        ntype = random.choice(["TASK_ASSIGNED", "LEAVE_STATUS", "INVOICE_ALERT", "SYSTEM"])
        title = f"System Notification: {ntype} Event #{n_i}"
        msg = f"Automatic workflow trigger notification dispatched to employee {rec_id}."
        is_r = random.choice([True, False, False])
        notifications_data.append((rec_id, title, msg, ntype, is_r))

    execute_values(cur, """
        INSERT INTO system_notifications (recipient_id, title, message, notification_type, is_read)
        VALUES %s;
    """, notifications_data)
    conn.commit()

    print("  Refreshing Materialized Views...")
    cur.execute("REFRESH MATERIALIZED VIEW mv_monthly_financial_summary;")
    cur.execute("REFRESH MATERIALIZED VIEW mv_department_kpi_summary;")
    conn.commit()

    cur.close()
    conn.close()

    t_elapsed = time.time() - t_start
    print("\n" + "="*80)
    print(f"SUCCESS: Enterprise Dataset Generation Complete in {t_elapsed:.2f} seconds!")
    print("="*80 + "\n")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else "eroms_enterprise_db"
    generate_enterprise_data(target)
