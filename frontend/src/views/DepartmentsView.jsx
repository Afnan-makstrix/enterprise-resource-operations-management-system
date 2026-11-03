import React, { useState, useEffect } from "react";
import { Building2, Users, DollarSign, MapPin, TrendingUp, CheckCircle, PieChart } from "lucide-react";
import { api } from "../services/api";

export default function DepartmentsView() {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDepartments();
  }, []);

  const loadDepartments = async () => {
    setLoading(true);
    const data = await api.getDepartments();
    setDepartments(data || []);
    setLoading(false);
  };

  const formatCurrency = (val) => {
    if (!val && val !== 0) return "$0";
    if (val >= 1000000) return `$${(val / 1000000).toFixed(2)}M`;
    if (val >= 1000) return `$${(val / 1000).toFixed(1)}k`;
    return `$${val.toLocaleString()}`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-2xl">
            Departmental Structure & Fiscal Allocations
          </h1>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Self-balancing organizational units mapped with 1-to-many employee assignments and budget caps.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-sky-500/10 px-3 py-1 text-xs font-semibold text-sky-600 dark:bg-sky-500/20 dark:text-sky-400">
            {departments.length} Active Departments
          </span>
        </div>
      </div>

      {/* Grid of Department Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {departments.map((dept) => {
          const burnPct = dept.budget > 0 ? Math.min(100, Math.round((dept.total_payroll / dept.budget) * 100)) : 0;
          return (
            <div
              key={dept.department_id}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md dark:border-slate-800 dark:bg-slate-900/60"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="inline-block rounded-md bg-slate-100 px-2 py-0.5 text-[10px] font-mono font-bold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                    {dept.department_code}
                  </span>
                  <h3 className="mt-2 text-base font-bold text-slate-900 dark:text-white">
                    {dept.name}
                  </h3>
                  <div className="mt-1 flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                    <MapPin className="h-3.5 w-3.5 text-slate-400" />
                    <span>{dept.location || "Global HQ"}</span>
                  </div>
                </div>

                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500/10 text-sky-600 dark:bg-sky-500/20 dark:text-sky-400">
                  <Building2 className="h-5 w-5" />
                </div>
              </div>

              {/* Stats */}
              <div className="mt-5 grid grid-cols-2 gap-3 border-t border-slate-100 pt-4 dark:border-slate-800/80">
                <div>
                  <div className="text-[10px] uppercase font-semibold text-slate-400">
                    Assigned Headcount
                  </div>
                  <div className="mt-0.5 text-sm font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1">
                    <Users className="h-3.5 w-3.5 text-sky-500" />
                    {dept.headcount?.toLocaleString() || "0"}
                  </div>
                </div>

                <div>
                  <div className="text-[10px] uppercase font-semibold text-slate-400">
                    Annual Budget
                  </div>
                  <div className="mt-0.5 text-sm font-bold text-slate-800 dark:text-slate-200 font-mono">
                    {formatCurrency(dept.budget)}
                  </div>
                </div>
              </div>

              {/* Budget Burn Progress Bar */}
              <div className="mt-4">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 dark:text-slate-400">Payroll Utilization</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">{burnPct}%</span>
                </div>
                <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                  <div
                    style={{ width: `${burnPct}%` }}
                    className={`h-full rounded-full transition-all duration-500 ${
                      burnPct > 90
                        ? "bg-rose-500"
                        : burnPct > 75
                        ? "bg-amber-500"
                        : "bg-emerald-500"
                    }`}
                  />
                </div>
                <div className="mt-1.5 flex justify-between text-[11px] text-slate-400 font-mono">
                  <span>Burn: {formatCurrency(dept.total_payroll)}</span>
                  <span>Remain: {formatCurrency(Math.max(0, dept.budget - dept.total_payroll))}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
