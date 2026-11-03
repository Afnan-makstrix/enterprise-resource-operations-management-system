import React, { useState } from "react";
import { ShieldCheck, ShieldAlert, Lock, Eye, KeyRound, Server, FileText, Database } from "lucide-react";

export default function AuditView() {
  const [selectedLog, setSelectedLog] = useState(null);

  const sampleAuditLogs = [
    {
      id: 1,
      table_name: "employees",
      action: "INSERT",
      record_id: "10011",
      user_name: "Afnan Makstrix (Super Admin)",
      ip_address: "192.168.1.10",
      created_at: "2026-11-02 18:45:12",
      old_values: null,
      new_values: {
        employee_number: "EMP-010011",
        first_name: "Sarah",
        last_name: "Jenkins",
        department_id: 1,
        salary: 115000,
        status: "ACTIVE"
      }
    },
    {
      id: 2,
      table_name: "sales_invoices",
      action: "UPDATE",
      record_id: "420",
      user_name: "Amina Al-Mansoor (Finance Director)",
      ip_address: "192.168.1.15",
      created_at: "2026-11-02 18:50:04",
      old_values: {
        paid_amount: 0.0,
        balance_due: 145000.0,
        payment_status: "UNPAID"
      },
      new_values: {
        paid_amount: 145000.0,
        balance_due: 0.0,
        payment_status: "PAID"
      }
    },
    {
      id: 3,
      table_name: "leave_requests",
      action: "UPDATE",
      record_id: "892",
      user_name: "Elena Rostova (VP Engineering)",
      ip_address: "192.168.1.12",
      created_at: "2026-11-02 19:12:33",
      old_values: { status: "PENDING", approved_by_id: null },
      new_values: { status: "APPROVED", approved_by_id: 2 }
    },
    {
      id: 4,
      table_name: "inventory_transactions",
      action: "INSERT",
      record_id: "12004",
      user_name: "Marcus Vance (Supply Chain)",
      ip_address: "192.168.1.20",
      created_at: "2026-11-02 19:30:15",
      old_values: null,
      new_values: {
        item_id: 1,
        warehouse_id: 1,
        transaction_type: "PURCHASE_RECEIPT",
        quantity: 50,
        unit_cost: 1250.0
      }
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-2xl">
            Enterprise Audit Ledger & Row-Level Security (RLS)
          </h1>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Immutable database changelog capturing full JSONB telemetry with user credentials and IP tracking.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400">
            PostgreSQL RLS Active
          </span>
        </div>
      </div>

      {/* RLS Security Specs Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500/10 text-sky-600 dark:bg-sky-500/20 dark:text-sky-400">
              <Lock className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-slate-900 dark:text-white">Row Level Security (RLS)</div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400">Payroll, Leaves, Attendance</div>
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-600 dark:text-slate-300">
            Employees are restricted via database policy to view only their own sensitive compensation records unless possessing the <code className="text-sky-500 font-mono">FINANCE_ADMIN</code> role.
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-slate-900 dark:text-white">ACID Invariant Triggers</div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400">Zero Inconsistent States</div>
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-600 dark:text-slate-300">
            Triggers fire before and after DML operations to enforce leave balance deductions, inventory balance updates, and payment reconciliation.
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-slate-900 dark:text-white">JSONB GIN Indexing</div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400">High-Performance Search</div>
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-600 dark:text-slate-300">
            Audit logs store complete state snapshots in JSONB columns indexed with Generalized Inverted Indexes (<code className="text-purple-500 font-mono">GIN</code>) for sub-millisecond querying.
          </p>
        </div>
      </div>

      {/* Live Audit Log Table */}
      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden dark:border-slate-800 dark:bg-slate-900/60">
        <div className="p-4 border-b border-slate-100 dark:border-slate-800">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Recent Immutable Audit Events
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
            <thead className="bg-slate-50 text-[11px] uppercase font-bold text-slate-500 dark:bg-slate-800/60 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="px-5 py-3">Timestamp</th>
                <th className="px-5 py-3">Target Table</th>
                <th className="px-5 py-3 text-center">Action</th>
                <th className="px-5 py-3">Operator</th>
                <th className="px-5 py-3">IP Address</th>
                <th className="px-5 py-3 text-center">Payload Diff</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {sampleAuditLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="px-5 py-3.5 font-mono text-[11px] text-slate-500">{log.created_at}</td>
                  <td className="px-5 py-3.5 font-mono font-bold text-slate-800 dark:text-slate-200">{log.table_name}</td>
                  <td className="px-5 py-3.5 text-center">
                    <span className={`inline-block rounded-full px-2 py-0.5 text-[10px] font-bold ${
                      log.action === "INSERT"
                        ? "bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400"
                        : log.action === "UPDATE"
                        ? "bg-sky-500/10 text-sky-600 dark:bg-sky-500/20 dark:text-sky-400"
                        : "bg-rose-500/10 text-rose-600 dark:bg-rose-500/20 dark:text-rose-400"
                    }`}>
                      {log.action}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 font-medium text-slate-900 dark:text-white">{log.user_name}</td>
                  <td className="px-5 py-3.5 font-mono text-slate-500 text-[11px]">{log.ip_address}</td>
                  <td className="px-5 py-3.5 text-center">
                    <button
                      onClick={() => setSelectedLog(selectedLog?.id === log.id ? null : log)}
                      className="rounded-lg border border-slate-200 px-2.5 py-1 text-[11px] font-semibold text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                    >
                      {selectedLog?.id === log.id ? "Hide JSONB" : "Inspect JSONB"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Selected JSONB Drawer */}
        {selectedLog && (
          <div className="border-t border-slate-200 bg-slate-950 p-5 dark:border-slate-800">
            <div className="text-xs font-bold text-sky-400 font-mono mb-2">
              JSONB Payload Inspection &mdash; Table: {selectedLog.table_name} (Record ID: {selectedLog.record_id})
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-[10px] font-bold uppercase text-slate-400 mb-1">Old Values (Pre-DML State):</div>
                <pre className="rounded-lg bg-slate-900 p-3 text-[11px] text-rose-300 font-mono overflow-x-auto">
                  {selectedLog.old_values ? JSON.stringify(selectedLog.old_values, null, 2) : "NULL (New Record Inserted)"}
                </pre>
              </div>
              <div>
                <div className="text-[10px] font-bold uppercase text-slate-400 mb-1">New Values (Committed State):</div>
                <pre className="rounded-lg bg-slate-900 p-3 text-[11px] text-emerald-300 font-mono overflow-x-auto">
                  {JSON.stringify(selectedLog.new_values, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

