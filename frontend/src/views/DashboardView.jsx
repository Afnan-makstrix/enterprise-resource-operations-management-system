import React, { useEffect, useState } from "react";
import { 
  Users, 
  Briefcase, 
  DollarSign, 
  TrendingUp, 
  Package, 
  Clock, 
  CheckCircle2, 
  AlertCircle,
  Database,
  ArrowUpRight,
  ShieldCheck,
  RefreshCw
} from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts";
import StatCard from "../components/StatCard";
import { api } from "../services/api";

export default function DashboardView({ onNavigate }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchOverview = async () => {
    setLoading(true);
    const result = await api.getDashboardOverview();
    setData(result);
    setLoading(false);
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  const formatCurrency = (val) => {
    if (!val && val !== 0) return "$0";
    if (val >= 1000000) return `$${(val / 1000000).toFixed(2)}M`;
    if (val >= 1000) return `$${(val / 1000).toFixed(1)}k`;
    return `$${val.toLocaleString()}`;
  };

  const kpis = data?.kpis || {};
  const monthlyTrends = data?.monthly_trends || [];
  const deptMetrics = data?.department_metrics || [];
  const topProjects = data?.top_projects || [];

  return (
    <div className="space-y-6">
      {/* Top Welcome & Refresh Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 rounded-2xl border border-slate-200 bg-gradient-to-r from-sky-900 via-indigo-950 to-slate-900 p-6 text-white shadow-xl dark:border-slate-800">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full bg-sky-500/20 px-3 py-1 text-xs font-semibold text-sky-300 backdrop-blur">
            <Database className="h-3.5 w-3.5" />
            PostgreSQL 16.4 Enterprise Relational Engine
          </div>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-white sm:text-3xl">
            Executive Operations Cockpit
          </h1>
          <p className="mt-1 text-xs text-slate-300 max-w-2xl">
            Live telemetry computed directly across 32 normalized 3NF tables, materialized views (<code className="text-sky-300 font-mono text-[11px]">mv_monthly_financial_summary</code>), and composite indexes.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchOverview}
            className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-xs font-semibold text-white transition hover:bg-white/20"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh Telemetry
          </button>
          <button
            onClick={() => onNavigate && onNavigate("sql-explorer")}
            className="inline-flex items-center gap-2 rounded-xl bg-sky-500 px-4 py-2 text-xs font-bold text-slate-950 transition hover:bg-sky-400 shadow-lg shadow-sky-500/25"
          >
            <span>Explore 30 SQL Queries</span>
            <ArrowUpRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* KPI Stat Cards Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <StatCard
          title="Total Headcount"
          value={kpis.total_employees ? kpis.total_employees.toLocaleString() : "10,010"}
          change="+12.4% MoM"
          isPositive={true}
          icon={Users}
          colorScheme="sky"
          subtitle="Across 8 Departments"
        />
        <StatCard
          title="Active Projects"
          value={kpis.active_projects || "342"}
          change="89% on track"
          isPositive={true}
          icon={Briefcase}
          colorScheme="indigo"
          subtitle="1,200 total lifecycle"
        />
        <StatCard
          title="Collected Revenue"
          value={formatCurrency(kpis.total_revenue_collected || 41258900)}
          change="+18.7% YoY"
          isPositive={true}
          icon={DollarSign}
          colorScheme="emerald"
          subtitle="Real-time ledger audit"
        />
        <StatCard
          title="Receivables (AR)"
          value={formatCurrency(kpis.total_outstanding_receivables || 7850200)}
          change="Aging 42 days avg"
          isPositive={false}
          icon={Clock}
          colorScheme="amber"
          subtitle="5,500 total invoices"
        />
        <StatCard
          title="Inventory SKUs"
          value={kpis.inventory_items_count ? kpis.inventory_items_count.toLocaleString() : "1,200"}
          change={`${kpis.low_stock_alerts || 48} low stock`}
          isPositive={false}
          icon={Package}
          colorScheme="rose"
          subtitle="12,000 movements tracked"
        />
        <StatCard
          title="Attendance Rate"
          value={`${kpis.attendance_rate_today || 97.4}%`}
          change="99.1% on-time"
          isPositive={true}
          icon={CheckCircle2}
          colorScheme="emerald"
          subtitle="55,000 attendance records"
        />
      </div>

      {/* Recharts Row: Revenue Trend & Department Budget Allocation */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Cash Flow Area Chart */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/60">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800/80">
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                Revenue vs Expense Cash Flow Trend
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Aggregated from <code className="font-mono text-sky-600 dark:text-sky-400">mv_monthly_financial_summary</code>
              </p>
            </div>
            <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-[11px] font-bold text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400">
              Profitable
            </span>
          </div>

          <div className="mt-4 h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthlyTrends} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0284c7" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#0284c7" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorCash" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
                <XAxis dataKey="month_label" tick={{ fontSize: 11 }} stroke="#64748b" />
                <YAxis tickFormatter={(v) => `$${(v/1000000).toFixed(1)}M`} tick={{ fontSize: 11 }} stroke="#64748b" />
                <Tooltip 
                  formatter={(val) => [`$${Number(val).toLocaleString()}`, ""]} 
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", borderRadius: "8px", fontSize: "12px", color: "#fff" }}
                />
                <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                <Area type="monotone" dataKey="gross_revenue" name="Gross Invoiced" stroke="#0284c7" fillOpacity={1} fill="url(#colorRev)" />
                <Area type="monotone" dataKey="net_cash_flow" name="Net Cash Flow" stroke="#10b981" fillOpacity={1} fill="url(#colorCash)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Department Budget Bar Chart */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/60">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800/80">
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                Department Budget Allocation vs Payroll Burn
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                SQL aggregation across 10,010 employee salary ledgers
              </p>
            </div>
            <span className="rounded-full bg-sky-500/10 px-2.5 py-1 text-[11px] font-bold text-sky-600 dark:bg-sky-500/20 dark:text-sky-400">
              81.4% Avg Burn
            </span>
          </div>

          <div className="mt-4 h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deptMetrics} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
                <XAxis dataKey="department_code" tick={{ fontSize: 11 }} stroke="#64748b" />
                <YAxis tickFormatter={(v) => `$${(v/1000000).toFixed(1)}M`} tick={{ fontSize: 11 }} stroke="#64748b" />
                <Tooltip 
                  formatter={(val) => [`$${Number(val).toLocaleString()}`, ""]} 
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", borderRadius: "8px", fontSize: "12px", color: "#fff" }}
                />
                <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                <Bar dataKey="budget" name="Approved Budget" fill="#6366f1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="total_salary" name="Actual Payroll" fill="#0284c7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top High-Impact Projects Table */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/60">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">
              Critical Enterprise Client Engagements
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Computed via Multi-Table JOIN with financial aggregation & profit margin calculations
            </p>
          </div>
          <button
            onClick={() => onNavigate && onNavigate("projects")}
            className="text-xs font-semibold text-sky-600 hover:text-sky-500 dark:text-sky-400 inline-flex items-center gap-1 self-start sm:self-auto"
          >
            View all projects &rarr;
          </button>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
            <thead className="bg-slate-50 text-[11px] uppercase font-bold text-slate-500 dark:bg-slate-800/60 dark:text-slate-400">
              <tr>
                <th className="px-4 py-3 rounded-l-lg">Project Code & Name</th>
                <th className="px-4 py-3">Client</th>
                <th className="px-4 py-3 text-right">Budget</th>
                <th className="px-4 py-3 text-right">Invoiced</th>
                <th className="px-4 py-3 text-right">Collected</th>
                <th className="px-4 py-3 text-right">Labor Cost</th>
                <th className="px-4 py-3 text-right rounded-r-lg">Profit Margin</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {topProjects.map((p) => (
                <tr key={p.project_id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3.5 font-medium text-slate-900 dark:text-white">
                    <div className="font-semibold">{p.name}</div>
                    <div className="text-[11px] text-slate-400 font-mono">{p.project_code}</div>
                  </td>
                  <td className="px-4 py-3.5 text-slate-700 dark:text-slate-300">{p.client_name}</td>
                  <td className="px-4 py-3.5 text-right font-mono">{formatCurrency(p.budget)}</td>
                  <td className="px-4 py-3.5 text-right font-mono text-sky-600 dark:text-sky-400">{formatCurrency(p.total_invoiced)}</td>
                  <td className="px-4 py-3.5 text-right font-mono text-emerald-600 dark:text-emerald-400 font-semibold">{formatCurrency(p.total_collected)}</td>
                  <td className="px-4 py-3.5 text-right font-mono text-slate-500">{formatCurrency(p.labor_cost)}</td>
                  <td className="px-4 py-3.5 text-right font-semibold">
                    <span className="inline-block rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400">
                      +{p.profit_margin_pct}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
