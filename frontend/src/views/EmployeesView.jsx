import React, { useState, useEffect } from "react";
import { 
  Users, 
  Search, 
  Filter, 
  ChevronLeft, 
  ChevronRight, 
  GitBranch, 
  Shield, 
  Briefcase, 
  Calendar,
  Building,
  DollarSign
} from "lucide-react";
import { api } from "../services/api";

export default function EmployeesView() {
  const [activeTab, setActiveTab] = useState("directory"); // 'directory' | 'org-chart'
  const [employees, setEmployees] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(12);
  const [search, setSearch] = useState("");
  const [departmentId, setDepartmentId] = useState("");
  const [departments, setDepartments] = useState([]);
  const [orgChart, setOrgChart] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDepartments();
  }, []);

  useEffect(() => {
    if (activeTab === "directory") {
      loadEmployees();
    } else {
      loadOrgChart();
    }
  }, [activeTab, page, departmentId]);

  const loadDepartments = async () => {
    const list = await api.getDepartments();
    setDepartments(list || []);
  };

  const loadEmployees = async () => {
    setLoading(true);
    const data = await api.getEmployees(page, pageSize, search, departmentId);
    setEmployees(data?.items || []);
    setTotal(data?.total || 0);
    setLoading(false);
  };

  const loadOrgChart = async () => {
    setLoading(true);
    const chart = await api.getOrgChart();
    setOrgChart(chart || []);
    setLoading(false);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    loadEmployees();
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-2xl">
            Enterprise Workforce & Organizational Architecture
          </h1>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Managing 10,010 relational employee records, department assignments, and recursive reporting hierarchy.
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="inline-flex rounded-xl border border-slate-200 bg-slate-100 p-1 dark:border-slate-800 dark:bg-slate-900">
          <button
            onClick={() => setActiveTab("directory")}
            className={`inline-flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-semibold transition ${
              activeTab === "directory"
                ? "bg-white text-slate-900 shadow-sm dark:bg-sky-500 dark:text-slate-950"
                : "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
            }`}
          >
            <Users className="h-3.5 w-3.5" />
            Employee Directory ({total ? total.toLocaleString() : "10k+"})
          </button>
          <button
            onClick={() => setActiveTab("org-chart")}
            className={`inline-flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-semibold transition ${
              activeTab === "org-chart"
                ? "bg-white text-slate-900 shadow-sm dark:bg-sky-500 dark:text-slate-950"
                : "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
            }`}
          >
            <GitBranch className="h-3.5 w-3.5" />
            Recursive CTE Org Chart
          </button>
        </div>
      </div>

      {activeTab === "directory" ? (
        <div className="space-y-4">
          {/* Filter & Search Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900/60">
            <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search by name, employee ID, title..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="h-9 w-full rounded-xl border border-slate-200 bg-slate-50 pl-9 pr-4 text-xs font-medium text-slate-900 placeholder-slate-400 focus:border-sky-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-sky-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:placeholder-slate-500"
              />
            </form>

            <div className="flex w-full sm:w-auto items-center gap-3">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-slate-400" />
                <select
                  value={departmentId}
                  onChange={(e) => {
                    setDepartmentId(e.target.value);
                    setPage(1);
                  }}
                  className="h-9 rounded-xl border border-slate-200 bg-slate-50 px-3 text-xs font-medium text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 focus:outline-none"
                >
                  <option value="">All Departments (8)</option>
                  {departments.map((d) => (
                    <option key={d.department_id} value={d.department_id}>
                      {d.name}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={loadEmployees}
                className="h-9 rounded-xl bg-sky-600 px-4 text-xs font-semibold text-white hover:bg-sky-500 transition shadow-sm"
              >
                Apply Filter
              </button>
            </div>
          </div>

          {/* Directory Data Grid */}
          <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden dark:border-slate-800 dark:bg-slate-900/60">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
                <thead className="bg-slate-50 text-[11px] uppercase font-bold text-slate-500 dark:bg-slate-800/60 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
                  <tr>
                    <th className="px-5 py-3.5">Employee</th>
                    <th className="px-5 py-3.5">Designation & Role</th>
                    <th className="px-5 py-3.5">Department</th>
                    <th className="px-5 py-3.5 text-right">Annual Salary</th>
                    <th className="px-5 py-3.5 text-center">Status</th>
                    <th className="px-5 py-3.5">Hire Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                  {loading ? (
                    <tr>
                      <td colSpan="6" className="py-12 text-center text-slate-400">
                        Querying PostgreSQL database...
                      </td>
                    </tr>
                  ) : employees.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="py-12 text-center text-slate-400">
                        No employees found matching filter criteria.
                      </td>
                    </tr>
                  ) : (
                    employees.map((emp) => (
                      <tr key={emp.employee_id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/30 transition-colors">
                        <td className="px-5 py-3.5 font-medium text-slate-900 dark:text-white">
                          <div className="flex items-center gap-3">
                            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800 font-semibold text-slate-700 dark:text-slate-300 text-xs">
                              {emp.full_name.split(" ").map(n => n[0]).slice(0, 2).join("")}
                            </div>
                            <div>
                              <div className="font-semibold text-slate-900 dark:text-white">{emp.full_name}</div>
                              <div className="text-[10px] text-slate-400 font-mono">{emp.employee_number}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-5 py-3.5">
                          <div className="font-medium text-slate-800 dark:text-slate-200">{emp.job_title}</div>
                          <div className="text-[11px] text-sky-600 dark:text-sky-400">{emp.role_name}</div>
                        </td>
                        <td className="px-5 py-3.5">
                          <span className="inline-flex items-center gap-1.5 rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                            <Building className="h-3 w-3 text-slate-400" />
                            {emp.department_name}
                          </span>
                        </td>
                        <td className="px-5 py-3.5 text-right font-mono font-medium text-slate-900 dark:text-slate-100">
                          ${emp.salary?.toLocaleString()}
                        </td>
                        <td className="px-5 py-3.5 text-center">
                          <span className={`inline-block rounded-full px-2 py-0.5 text-[10px] font-bold ${
                            emp.status === "ACTIVE"
                              ? "bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400"
                              : "bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400"
                          }`}>
                            {emp.status}
                          </span>
                        </td>
                        <td className="px-5 py-3.5 text-slate-500 dark:text-slate-400 text-[11px] font-mono">
                          {emp.hire_date}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-between border-t border-slate-200 px-5 py-3 dark:border-slate-800 text-xs text-slate-500">
              <div>
                Showing <span className="font-semibold text-slate-900 dark:text-white">{(page - 1) * pageSize + 1}</span> to{" "}
                <span className="font-semibold text-slate-900 dark:text-white">{Math.min(page * pageSize, total)}</span> of{" "}
                <span className="font-semibold text-slate-900 dark:text-white">{total.toLocaleString()}</span> employees
              </div>

              <div className="flex items-center gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage(page - 1)}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-1.5 font-medium hover:bg-slate-100 disabled:opacity-40 disabled:pointer-events-none dark:border-slate-700 dark:hover:bg-slate-800"
                >
                  <ChevronLeft className="h-3.5 w-3.5" /> Prev
                </button>
                <span className="px-2 font-mono text-slate-700 dark:text-slate-300">
                  Page {page} of {totalPages}
                </span>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage(page + 1)}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-1.5 font-medium hover:bg-slate-100 disabled:opacity-40 disabled:pointer-events-none dark:border-slate-700 dark:hover:bg-slate-800"
                >
                  Next <ChevronRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Tab 2: Recursive CTE Org Chart */
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/60">
          <div className="mb-6 border-b border-slate-100 pb-4 dark:border-slate-800">
            <div className="inline-flex items-center gap-2 rounded-md bg-indigo-500/10 px-2.5 py-1 text-xs font-semibold text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400">
              <GitBranch className="h-3.5 w-3.5" />
              PostgreSQL Recursive CTE Demonstration
            </div>
            <h2 className="mt-2 text-base font-bold text-slate-900 dark:text-white">
              Recursive Manager Reporting Chain Traversal
            </h2>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Generated in real-time via <code className="font-mono text-sky-600 dark:text-sky-400">WITH RECURSIVE employee_hierarchy AS (...)</code> querying the self-referential foreign key <code className="font-mono text-sky-600 dark:text-sky-400">manager_id REFERENCES employees(id)</code>.
            </p>
          </div>

          <div className="space-y-3">
            {orgChart.map((node, idx) => (
              <div
                key={node.employee_id || idx}
                style={{ marginLeft: `${(node.hierarchy_level - 1) * 28}px` }}
                className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50/60 p-3.5 transition hover:border-sky-500/50 hover:bg-white dark:border-slate-800 dark:bg-slate-900/40 dark:hover:border-sky-500/50 dark:hover:bg-slate-800/50 shadow-sm"
              >
                <div className="flex items-center gap-3">
                  <div className={`flex h-8 w-8 items-center justify-center rounded-lg text-xs font-bold ${
                    node.hierarchy_level === 1 
                      ? "bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20"
                      : node.hierarchy_level === 2
                      ? "bg-sky-600 text-white shadow-md shadow-sky-600/20"
                      : "bg-slate-200 text-slate-800 dark:bg-slate-800 dark:text-slate-200"
                  }`}>
                    L{node.hierarchy_level}
                  </div>

                  <div>
                    <div className="text-xs font-bold text-slate-900 dark:text-white">
                      {node.full_name}
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400">
                      {node.job_title}
                    </div>
                  </div>
                </div>

                <div className="hidden md:flex items-center gap-2">
                  <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500 max-w-md truncate">
                    Chain: {node.reporting_chain}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
