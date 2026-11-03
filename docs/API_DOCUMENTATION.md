# EROMS Backend REST API Documentation

**Framework:** FastAPI (Python 3.11+)  
**ORM:** SQLAlchemy 2.0 (psycopg2)  
**Security:** OAuth2 Password Bearer with JWT (HMAC-SHA256) & RBAC  
**Base URL:** `http://localhost:8000/api/v1`  
**Swagger UI:** `http://localhost:8000/docs`  
**ReDoc:** `http://localhost:8000/redoc`  

---

## 1. Authentication Endpoints (`/api/v1/auth`)

### `POST /auth/login` (OAuth2 Form)
- **Request:** Form data `username`, `password`
- **Response:** `{ "access_token": "...", "token_type": "bearer", "role": "Super Admin", ... }`

### `POST /auth/json-login` (REST JSON)
- **Request Body:**
  ```json
  {
    "username": "afnan_admin",
    "password": "AdminPassword123!"
  }
  ```
- **Response:**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user_id": 1,
    "username": "afnan_admin",
    "role": "Super Admin",
    "full_name": "Muhammad Afnan",
    "employee_id": 1
  }
  ```

### `GET /auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** Current authenticated profile, role, and permission grants.

---

## 2. Workforce Management Endpoints (`/api/v1/employees`)

### `GET /employees/`
- **Query Params:** `page` (int), `page_size` (int), `search` (str), `department_id` (int)
- **Description:** Returns paginated employee directory (10,010 records) with total counts and pagination metadata.

### `POST /employees/`
- **Description:** Triggers stored procedure `sp_onboard_employee` creating employee record, default credentials, and leave entitlements within an atomic transaction.

### `GET /employees/{employee_id}`
- **Description:** Full employee profile, job title, salary, manager, and department details.

### `GET /employees/org-chart/tree`
- **Description:** Executes PostgreSQL Recursive CTE query `WITH RECURSIVE employee_hierarchy AS (...)` returning the complete organizational chain of command.

---

## 3. Department Management Endpoints (`/api/v1/departments`)

### `GET /departments/`
- **Description:** Lists all active departments, approved budgets, location, headcount, and total payroll expenses.

### `GET /departments/{department_id}`
- **Description:** Single department details with assigned staff list and fiscal metrics.

---

## 4. Projects & Operations Endpoints (`/api/v1/projects`)

### `GET /projects/`
- **Query Params:** `page` (int), `page_size` (int), `status` (str)
- **Description:** Lists 1,200 project records, budget vs cost, client name, and task completion metrics.

### `GET /projects/{project_id}/tasks`
- **Description:** Tasks and work breakdown schedule linked to a specific project.

---

## 5. Inventory & Multi-Warehouse Endpoints (`/api/v1/inventory`)

### `GET /inventory/items`
- **Query Params:** `page` (int), `page_size` (int), `low_stock_only` (bool)
- **Description:** Real-time stock counts across warehouses, cost price, selling price, and stock status.

### `GET /inventory/warehouses`
- **Description:** Lists all active warehouse distribution centers and capacity.

### `POST /inventory/transactions`
- **Description:** Posts an inventory movement into `inventory_transactions` ledger; automatically updates physical stock via trigger.

---

## 6. Billing & Accounts Receivable Endpoints (`/api/v1/billing`)

### `GET /billing/invoices`
- **Query Params:** `page` (int), `page_size` (int), `status` (str)
- **Description:** Sales invoices with total amount, paid amount, balance due (generated column), and due dates.

### `GET /billing/aging-report`
- **Description:** Real-time Accounts Receivable aging schedule grouped into CURRENT, 1-30, 31-60, 61-90, and >90 days overdue.

### `POST /billing/payments`
- **Description:** Reconciles invoice payment; triggers automated payment status advancement.

---

## 7. Business Analytics & SQL Execution Endpoints (`/api/v1/analytics`)

### `GET /analytics/overview`
- **Description:** Executive telemetry combining headcount, active projects, gross revenue collected, open receivables, monthly cash flow trends, and department budget burns.

### `GET /analytics/execute-query/{query_number}`
- **Description:** Dynamic execution laboratory executing advanced SQL queries (Q01 to Q30) directly against the PostgreSQL database and returning tabular data with column metadata.
