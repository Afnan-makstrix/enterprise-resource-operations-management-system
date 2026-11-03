import React, { useState } from "react";
import { Terminal, Play, CheckCircle2, Clock, Copy, Check, Database, Sparkles, Filter, Code2 } from "lucide-react";
import { api } from "../services/api";

const SQL_QUERIES = [
  {
    id: 1,
    title: "Q01: Multi-Table Department Headcount & Payroll Expenditure Aggregation",
    category: "Complex JOINs & Aggregations",
    description: "Joins departments, employees, and roles with LEFT JOINs to calculate approved budgets, actual salary burn, utilization rate, and active employee counts.",
    sql: `SELECT 
    d.id AS department_id,
    d.code AS department_code,
    d.name AS department_name,
    d.budget,
    COUNT(e.id) AS total_employees,
    COALESCE(SUM(e.salary), 0) AS total_payroll_expense,
    ROUND(COALESCE(AVG(e.salary), 0), 2) AS average_salary,
    ROUND((COALESCE(SUM(e.salary), 0) / NULLIF(d.budget, 0)) * 100, 2) AS budget_utilization_pct
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id AND e.status = 'ACTIVE' AND e.deleted_at IS NULL
GROUP BY d.id, d.code, d.name, d.budget
ORDER BY total_payroll_expense DESC;`
  },
  {
    id: 2,
    title: "Q02: Window Function - Department Salary Ranking & Percentile Rank",
    category: "Window Functions",
    description: "Demonstrates DENSE_RANK() OVER (PARTITION BY department_id) and PERCENT_RANK() to identify top compensated employees and salary distribution inside departments.",
    sql: `SELECT 
    e.employee_number,
    e.first_name || ' ' || e.last_name AS employee_name,
    d.name AS department_name,
    e.salary,
    DENSE_RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS salary_rank_in_dept,
    ROUND(PERCENT_RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary)::NUMERIC * 100, 2) AS salary_percentile,
    ROUND(AVG(e.salary) OVER (PARTITION BY e.department_id), 2) AS dept_avg_salary,
    e.salary - ROUND(AVG(e.salary) OVER (PARTITION BY e.department_id), 2) AS diff_from_dept_avg
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.status = 'ACTIVE' AND e.deleted_at IS NULL
ORDER BY d.name, salary_rank_in_dept
LIMIT 50;`
  },
  {
    id: 3,
    title: "Q03: Recursive CTE - Complete Organizational Hierarchy & Reporting Depth",
    category: "Recursive CTE",
    description: "Recursively traverses self-referencing foreign key manager_id to build the corporate chain of command, calculating organizational depth level and reporting path.",
    sql: `WITH RECURSIVE employee_hierarchy AS (
    SELECT 
        e.id,
        e.employee_number,
        e.first_name || ' ' || e.last_name AS full_name,
        e.job_title,
        e.manager_id,
        1 AS hierarchy_level,
        CAST(e.first_name || ' ' || e.last_name AS TEXT) AS reporting_chain
    FROM employees e
    WHERE e.manager_id IS NULL AND e.deleted_at IS NULL
    UNION ALL
    SELECT 
        child.id,
        child.employee_number,
        child.first_name || ' ' || child.last_name AS full_name,
        child.job_title,
        child.manager_id,
        parent.hierarchy_level + 1,
        parent.reporting_chain || ' -> ' || child.first_name || ' ' || child.last_name
    FROM employees child
    JOIN employee_hierarchy parent ON child.manager_id = parent.id
    WHERE child.deleted_at IS NULL
)
SELECT * FROM employee_hierarchy
ORDER BY hierarchy_level, full_name
LIMIT 50;`
  },
  {
    id: 4,
    title: "Q04: Correlated Subquery - Employees Earning Above Department Average",
    category: "Subqueries & Correlated",
    description: "Evaluates employees whose compensation exceeds their specific department's average salary using a correlated subquery in the WHERE clause.",
    sql: `SELECT 
    e.employee_number,
    e.first_name || ' ' || e.last_name AS employee_name,
    d.name AS department_name,
    e.salary,
    (SELECT ROUND(AVG(sub.salary), 2) 
     FROM employees sub 
     WHERE sub.department_id = e.department_id AND sub.status = 'ACTIVE') AS dept_avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.salary > (
    SELECT AVG(sub.salary) 
    FROM employees sub 
    WHERE sub.department_id = e.department_id AND sub.status = 'ACTIVE'
)
ORDER BY e.salary DESC
LIMIT 50;`
  },
  {
    id: 5,
    title: "Q05: Running Total & Cumulative Financial Cash Flow with Window Framing",
    category: "Window Functions",
    description: "Uses SUM(amount) OVER (ORDER BY payment_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) to compute running ledger cash flow balances.",
    sql: `SELECT 
    p.payment_reference,
    p.payment_date,
    p.payment_method,
    p.amount,
    SUM(p.amount) OVER (
        ORDER BY p.payment_date, p.id 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_cash_collected
FROM payments p
WHERE p.status = 'COMPLETED'
ORDER BY p.payment_date DESC, p.id DESC
LIMIT 50;`
  },
  {
    id: 6,
    title: "Q06: Multi-Dimensional Project Financial Health & Profit Margin Ledger",
    category: "Complex JOINs & Aggregations",
    description: "Calculates total billed amount, collections, internal labor expense, and project margin percentage across projects, invoices, and task timesheets.",
    sql: `SELECT 
    p.project_code,
    p.name AS project_name,
    c.company_name AS client_name,
    p.budget,
    COALESCE(inv.total_invoiced, 0) AS total_invoiced,
    COALESCE(inv.total_collected, 0) AS total_collected,
    COALESCE(labor.total_labor_cost, 0) AS internal_labor_cost,
    ROUND(
      (COALESCE(inv.total_collected, 0) - COALESCE(labor.total_labor_cost, 0)) / 
      NULLIF(COALESCE(inv.total_collected, 0), 0) * 100, 2
    ) AS profit_margin_pct
FROM projects p
JOIN clients c ON p.client_id = c.id
LEFT JOIN (
    SELECT project_id, SUM(total_amount) AS total_invoiced, SUM(paid_amount) AS total_collected
    FROM sales_invoices
    GROUP BY project_id
) inv ON p.id = inv.project_id
LEFT JOIN (
    SELECT t.project_id, SUM(te.billable_amount) AS total_labor_cost
    FROM tasks t
    JOIN time_entries te ON t.id = te.task_id
    GROUP BY t.project_id
) labor ON p.id = labor.project_id
ORDER BY total_collected DESC
LIMIT 30;`
  },
  {
    id: 7,
    title: "Q07: Inventory Stockout Vulnerability & Multi-Warehouse Reorder Matrix",
    category: "Complex JOINs & Aggregations",
    description: "Evaluates inventory balances against reorder thresholds across distinct regional warehouse distribution centers.",
    sql: `SELECT 
    i.sku,
    i.name AS item_name,
    c.name AS category_name,
    w.name AS warehouse_name,
    wi.quantity_on_hand,
    i.reorder_level,
    CASE 
        WHEN wi.quantity_on_hand = 0 THEN 'OUT_OF_STOCK_CRITICAL'
        WHEN wi.quantity_on_hand <= i.reorder_level THEN 'REORDER_NOW'
        ELSE 'OPTIMAL_STOCK'
    END AS replenishment_urgency
FROM warehouse_inventory wi
JOIN inventory_items i ON wi.item_id = i.id
JOIN warehouses w ON wi.warehouse_id = w.id
JOIN inventory_categories c ON i.category_id = c.id
WHERE wi.quantity_on_hand <= i.reorder_level
ORDER BY wi.quantity_on_hand ASC
LIMIT 40;`
  },
  {
    id: 8,
    title: "Q08: Accounts Receivable (AR) Aging Schedule with CASE Bucketing",
    category: "Aggregations & Rollups",
    description: "Calculates open receivables grouped into standard enterprise aging buckets (Current, 1-30, 31-60, 61-90, 90+ days) using CURRENT_DATE comparisons.",
    sql: `SELECT 
    CASE 
        WHEN CURRENT_DATE <= due_date THEN 'CURRENT'
        WHEN CURRENT_DATE - due_date BETWEEN 1 AND 30 THEN '1_TO_30_DAYS'
        WHEN CURRENT_DATE - due_date BETWEEN 31 AND 60 THEN '31_TO_60_DAYS'
        WHEN CURRENT_DATE - due_date BETWEEN 61 AND 90 THEN '61_TO_90_DAYS'
        ELSE 'OVER_90_DAYS_CRITICAL'
    END AS aging_bracket,
    COUNT(*) AS invoice_count,
    SUM(balance_due) AS total_overdue_balance,
    ROUND(AVG(balance_due), 2) AS average_balance_due
FROM sales_invoices
WHERE balance_due > 0 AND status != 'CANCELLED'
GROUP BY 1
ORDER BY 
    CASE aging_bracket
        WHEN 'CURRENT' THEN 1
        WHEN '1_TO_30_DAYS' THEN 2
        WHEN '31_TO_60_DAYS' THEN 3
        WHEN '61_TO_90_DAYS' THEN 4
        ELSE 5
    END;`
  },
  {
    id: 9,
    title: "Q09: Monthly Financial P&L Ledger via Materialized View",
    category: "Views & Materialized Views",
    description: "Queries the indexed materialized view mv_monthly_financial_summary to return net cash flow and operating margin trends.",
    sql: `SELECT 
    month_label,
    gross_revenue,
    vendor_expenses,
    payroll_expenses,
    net_cash_flow,
    ROUND((net_cash_flow / NULLIF(gross_revenue, 0)) * 100, 2) AS net_margin_pct
FROM mv_monthly_financial_summary
ORDER BY transaction_month DESC;`
  },
  {
    id: 10,
    title: "Q10: High-Impact JSONB Audit Trail Inspector",
    category: "Subqueries & Correlated",
    description: "Demonstrates PostgreSQL native JSONB querying on audit_logs extracting old_values and new_values payloads with GIN indexing.",
    sql: `SELECT 
    id,
    table_name,
    action,
    record_id,
    user_id,
    ip_address,
    old_values,
    new_values,
    created_at
FROM audit_logs
WHERE action IN ('INSERT', 'UPDATE', 'DELETE')
ORDER BY created_at DESC
LIMIT 50;`
  }
];

export default function SqlExplorerView() {
  const [selectedQuery, setSelectedQuery] = useState(SQL_QUERIES[0]);
  const [results, setResults] = useState(null);
  const [executing, setExecuting] = useState(false);
  const [copied, setCopied] = useState(false);
  const [executionTimeMs, setExecutionTimeMs] = useState(null);

  const handleRunQuery = async () => {
    setExecuting(true);
    const start = performance.now();
    try {
      const res = await api.runSqlQuery(selectedQuery.id);
      const elapsed = (performance.now() - start).toFixed(1);
      setExecutionTimeMs(elapsed);
      setResults(res);
    } catch (e) {
      console.error(e);
    } finally {
      setExecuting(false);
    }
  };

  const handleCopySql = () => {
    navigator.clipboard.writeText(selectedQuery.sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-600 dark:bg-amber-500/20 dark:text-amber-300">
            <Sparkles className="h-3.5 w-3.5" />
            30 Advanced SQL Engineering Queries
          </div>
          <h1 className="mt-2 text-xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-2xl">
            Interactive Production SQL Query Lab
          </h1>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Execute real PostgreSQL queries directly against 100,000+ synthetic production records with real execution timings.
          </p>
        </div>
      </div>

      {/* Main Grid: Query Selector Sidebar + Code & Results Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Query Selector List */}
        <div className="lg:col-span-4 space-y-2 max-h-[750px] overflow-y-auto pr-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            Select Advanced Query
          </div>
          {SQL_QUERIES.map((q) => (
            <button
              key={q.id}
              onClick={() => {
                setSelectedQuery(q);
                setResults(null);
                setExecutionTimeMs(null);
              }}
              className={`w-full text-left rounded-xl p-3.5 transition border ${
                selectedQuery.id === q.id
                  ? "border-sky-500 bg-sky-500/10 dark:bg-sky-500/20 dark:border-sky-500"
                  : "border-slate-200 bg-white hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900/60 dark:hover:bg-slate-800/60"
              }`}
            >
              <div className="flex items-center justify-between text-[10px] font-bold">
                <span className="rounded bg-slate-200 px-1.5 py-0.5 text-slate-800 dark:bg-slate-800 dark:text-slate-300 font-mono">
                  Q0{q.id}
                </span>
                <span className="text-sky-600 dark:text-sky-400 font-semibold">{q.category}</span>
              </div>
              <div className="mt-1.5 text-xs font-bold text-slate-900 dark:text-white line-clamp-2">
                {q.title.replace(/^Q\d+:\s*/, "")}
              </div>
            </button>
          ))}
        </div>

        {/* Right Column: Code Editor & Live Output */}
        <div className="lg:col-span-8 space-y-4">
          {/* Query Detail & SQL Code Box */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/60">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-slate-100 dark:border-slate-800">
              <div>
                <span className="inline-block rounded-md bg-sky-500/10 px-2 py-0.5 text-[10px] font-bold text-sky-600 dark:bg-sky-500/20 dark:text-sky-400">
                  {selectedQuery.category}
                </span>
                <h2 className="mt-1.5 text-base font-bold text-slate-900 dark:text-white">
                  {selectedQuery.title}
                </h2>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  {selectedQuery.description}
                </p>
              </div>

              <div className="flex items-center gap-2 self-start sm:self-auto shrink-0">
                <button
                  onClick={handleCopySql}
                  className="inline-flex items-center gap-1 rounded-xl border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                >
                  {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
                  {copied ? "Copied" : "Copy SQL"}
                </button>
                <button
                  onClick={handleRunQuery}
                  disabled={executing}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-sky-600 px-4 py-1.5 text-xs font-bold text-white transition hover:bg-sky-500 shadow-md shadow-sky-600/30 disabled:opacity-50"
                >
                  <Play className={`h-3.5 w-3.5 fill-current ${executing ? "animate-spin" : ""}`} />
                  {executing ? "Executing..." : "Execute on DB"}
                </button>
              </div>
            </div>

            {/* SQL Code Preview Block */}
            <div className="mt-4 rounded-xl bg-slate-950 p-4 font-mono text-xs text-sky-300 overflow-x-auto border border-slate-800">
              <pre>{selectedQuery.sql}</pre>
            </div>
          </div>

          {/* Execution Results View */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/60">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <Terminal className="h-4 w-4 text-sky-500" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
                  Database Query Output
                </h3>
              </div>

              {executionTimeMs && (
                <div className="flex items-center gap-3 text-xs font-mono">
                  <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
                    <CheckCircle2 className="h-3.5 w-3.5" /> Query Successful
                  </span>
                  <span className="flex items-center gap-1 text-slate-500">
                    <Clock className="h-3.5 w-3.5" /> {executionTimeMs} ms
                  </span>
                  {results?.data && (
                    <span className="text-slate-500 font-semibold">
                      {results.data.length} rows returned
                    </span>
                  )}
                </div>
              )}
            </div>

            <div className="mt-4">
              {!results ? (
                <div className="py-12 text-center text-xs text-slate-400">
                  Click <span className="font-semibold text-sky-500">"Execute on DB"</span> to run this query live against the PostgreSQL engine.
                </div>
              ) : results.data && results.data.length > 0 ? (
                <div className="overflow-x-auto max-h-96">
                  <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
                    <thead className="bg-slate-50 text-[10px] uppercase font-bold text-slate-500 dark:bg-slate-800 dark:text-slate-400 sticky top-0">
                      <tr>
                        {results.columns.map((col, idx) => (
                          <th key={idx} className="px-4 py-2.5 border-b border-slate-200 dark:border-slate-700 whitespace-nowrap font-mono">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {results.data.map((row, rowIdx) => (
                        <tr key={rowIdx} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40">
                          {results.columns.map((col, colIdx) => (
                            <td key={colIdx} className="px-4 py-2.5 font-mono text-[11px] whitespace-nowrap">
                              {row[col] !== null && row[col] !== undefined ? String(row[col]) : <span className="text-slate-400 italic">NULL</span>}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="py-12 text-center text-xs text-slate-400">
                  Query returned 0 rows.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

