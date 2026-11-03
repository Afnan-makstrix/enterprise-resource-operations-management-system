import React from "react";
import {
  LayoutDashboard,
  Users,
  Building2,
  Briefcase,
  Package,
  Receipt,
  Terminal,
  ShieldAlert,
  Gauge,
  ChevronLeft,
  ChevronRight,
  Database,
  ExternalLink,
  Layers
} from "lucide-react";

export default function Sidebar({ activeView, setActiveView, collapsed, setCollapsed }) {
  const navItems = [
    {
      id: "dashboard",
      label: "Executive Dashboard",
      icon: LayoutDashboard,
      badge: "Live"
    },
    {
      id: "employees",
      label: "Employees & Org Chart",
      icon: Users,
      badge: "10k"
    },
    {
      id: "departments",
      label: "Departments & Units",
      icon: Building2
    },
    {
      id: "projects",
      label: "Projects & Operations",
      icon: Briefcase
    },
    {
      id: "inventory",
      label: "Inventory & Warehouses",
      icon: Package
    },
    {
      id: "billing",
      label: "Billing & Invoices",
      icon: Receipt
    },
    {
      id: "sql-explorer",
      label: "SQL Explorer (Q01-Q30)",
      icon: Terminal,
      highlight: true
    },
    {
      id: "audit",
      label: "Audit Logs & Security",
      icon: ShieldAlert
    },
    {
      id: "benchmarks",
      label: "Query Performance",
      icon: Gauge
    }
  ];

  return (
    <aside
      className={`relative flex flex-col border-r border-slate-200 bg-white transition-all duration-300 dark:border-slate-800 dark:bg-[#0B0F19] ${
        collapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between border-b border-slate-200 px-4 dark:border-slate-800">
        <div className="flex items-center space-x-3 overflow-hidden">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-sky-500 to-indigo-600 text-white shadow-md shadow-sky-500/20">
            <Database className="h-5 w-5" />
          </div>
          {!collapsed && (
            <div className="flex flex-col truncate">
              <span className="font-bold tracking-tight text-slate-900 dark:text-white">
                EROMS Enterprise
              </span>
              <span className="text-[10px] uppercase font-semibold text-sky-600 dark:text-sky-400 tracking-wider">
                PostgreSQL Core
              </span>
            </div>
          )}
        </div>

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-100 dark:border-slate-800 dark:text-slate-400 dark:hover:bg-slate-800"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      {/* Navigation List */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {!collapsed && (
          <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
            Enterprise Modules
          </div>
        )}

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`group flex w-full items-center rounded-xl px-3 py-2.5 text-xs font-medium transition-all ${
                isActive
                  ? "bg-sky-600 text-white shadow-sm shadow-sky-600/30 dark:bg-sky-500 dark:text-slate-950 font-semibold"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800/60 dark:hover:text-slate-200"
              }`}
              title={collapsed ? item.label : undefined}
            >
              <Icon
                className={`h-4 w-4 shrink-0 transition-transform group-hover:scale-110 ${
                  collapsed ? "mx-auto" : "mr-3"
                } ${
                  isActive
                    ? "text-white dark:text-slate-950"
                    : item.highlight
                    ? "text-amber-500 dark:text-amber-400"
                    : "text-slate-400 dark:text-slate-500"
                }`}
              />

              {!collapsed && (
                <span className="flex-1 text-left truncate">{item.label}</span>
              )}

              {!collapsed && item.badge && (
                <span
                  className={`ml-2 rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                    isActive
                      ? "bg-white/20 text-white dark:bg-slate-950/20 dark:text-slate-950"
                      : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
                  }`}
                >
                  {item.badge}
                </span>
              )}

              {!collapsed && item.highlight && (
                <span className="ml-2 rounded-full bg-amber-500/10 px-1.5 py-0.5 text-[10px] font-bold text-amber-600 dark:bg-amber-400/20 dark:text-amber-300">
                  30 SQL
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Bottom Profile / Intern Information Card */}
      <div className="border-t border-slate-200 p-3 dark:border-slate-800">
        {!collapsed ? (
          <div className="rounded-xl border border-slate-200/80 bg-slate-50 p-3 dark:border-slate-800/80 dark:bg-slate-900/50">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Engineer Portfolio
              </span>
              <a
                href="https://github.com/Afnan-makstrix"
                target="_blank"
                rel="noreferrer"
                className="text-xs text-sky-600 hover:text-sky-500 dark:text-sky-400 inline-flex items-center gap-1 font-semibold"
              >
                GitHub <ExternalLink className="h-3 w-3" />
              </a>
            </div>
            <div className="mt-2 text-xs font-medium text-slate-700 dark:text-slate-300">
              Muhammad Afnan
            </div>
            <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">
              Database Architect Intern
            </div>
          </div>
        ) : (
          <a
            href="https://github.com/Afnan-makstrix"
            target="_blank"
            rel="noreferrer"
            className="flex h-10 w-10 mx-auto items-center justify-center rounded-xl bg-slate-100 text-slate-600 hover:text-sky-600 dark:bg-slate-800 dark:text-slate-300"
            title="Afnan-makstrix GitHub"
          >
            <ExternalLink className="h-4 w-4" />
          </a>
        )}
      </div>
    </aside>
  );
}
