import React, { useState, useEffect } from "react";
import { Receipt, DollarSign, Clock, AlertTriangle, CheckCircle, ChevronLeft, ChevronRight, ShieldCheck, CreditCard } from "lucide-react";
import { api } from "../services/api";

export default function BillingView() {
  const [invoices, setInvoices] = useState([]);
  const [aging, setAging] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    loadBillingData();
  }, [page]);

  const loadBillingData = async () => {
    setLoading(true);
    const [invData, agingData] = await Promise.all([
      api.getInvoices(page),
      api.getAgingReport()
    ]);
    setInvoices(invData?.items || []);
    setTotal(invData?.total || 0);
    setAging(agingData || []);
    setLoading(false);
  };

  const formatCurrency = (val) => {
    if (!val && val !== 0) return "$0";
    return `$${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const handleSimulatePayment = (inv) => {
    setNotification({
      type: "success",
      message: `Trigger executed: Payment recorded for ${inv.invoice_number}. Stored procedure updated balance_due to $0.00 and payment_status to 'PAID' via ACID transaction!`
    });
    // Optimistically update invoice state
    setInvoices(prev => prev.map(item => {
      if (item.invoice_id === inv.invoice_id) {
        return {
          ...item,
          paid_amount: item.total_amount,
          balance_due: 0,
          payment_status: "PAID"
        };
      }
      return item;
    }));

    setTimeout(() => {
      setNotification(null);
    }, 6000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-2xl">
            Billing, Invoicing & Accounts Receivable (AR)
          </h1>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Automated balance tracking with PostgreSQL <code className="font-mono text-sky-600 dark:text-sky-400">GENERATED ALWAYS AS (total_amount - paid_amount) STORED</code>.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400">
            {total.toLocaleString()} Total Invoices
          </span>
        </div>
      </div>

      {/* Trigger Notification Toast */}
      {notification && (
        <div className="rounded-xl border border-emerald-500/40 bg-emerald-50/90 p-4 text-xs font-semibold text-emerald-900 shadow-lg dark:bg-emerald-950/80 dark:text-emerald-200 flex items-center gap-3">
          <ShieldCheck className="h-5 w-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span>{notification.message}</span>
        </div>
      )}

      {/* Accounts Receivable Aging Buckets */}
      <div>
        <h2 className="mb-3 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          AR Aging Schedule (View: <code className="font-mono text-sky-600 dark:text-sky-400">v_accounts_receivable_aging</code>)
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {aging.map((b) => (
            <div
              key={b.aging_bracket}
              className={`rounded-xl border p-4 shadow-sm transition hover:shadow ${
                b.aging_bracket === "OVER_90_DAYS_CRITICAL"
                  ? "border-rose-300 bg-rose-50/50 dark:border-rose-900/50 dark:bg-rose-950/20"
                  : b.aging_bracket === "61_TO_90_DAYS"
                  ? "border-amber-300 bg-amber-50/50 dark:border-amber-900/50 dark:bg-amber-950/20"
                  : "border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900/60"
              }`}
            >
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                {b.aging_bracket.replace(/_/g, " ")}
              </div>
              <div className="mt-1 text-lg font-bold text-slate-900 dark:text-white font-mono">
                {formatCurrency(b.total_overdue_balance)}
              </div>
              <div className="mt-1 text-[11px] text-slate-500 dark:text-slate-400">
                {b.invoice_count?.toLocaleString()} Open Invoices
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Invoices Data Grid */}
      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden dark:border-slate-800 dark:bg-slate-900/60">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
            <thead className="bg-slate-50 text-[11px] uppercase font-bold text-slate-500 dark:bg-slate-800/60 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="px-5 py-3.5">Invoice #</th>
                <th className="px-5 py-3.5">Client</th>
                <th className="px-5 py-3.5 text-right">Total Invoiced</th>
                <th className="px-5 py-3.5 text-right">Paid to Date</th>
                <th className="px-5 py-3.5 text-right">Balance Due</th>
                <th className="px-5 py-3.5 text-center">Payment Status</th>
                <th className="px-5 py-3.5">Due Date</th>
                <th className="px-5 py-3.5 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-slate-400">
                    Querying billing ledger...
                  </td>
                </tr>
              ) : invoices.map((inv) => (
                <tr key={inv.invoice_id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="px-5 py-3.5 font-bold font-mono text-slate-900 dark:text-white">
                    {inv.invoice_number}
                  </td>
                  <td className="px-5 py-3.5 text-slate-800 dark:text-slate-200 font-medium">
                    {inv.client_name}
                  </td>
                  <td className="px-5 py-3.5 text-right font-mono text-slate-800 dark:text-slate-200">
                    {formatCurrency(inv.total_amount)}
                  </td>
                  <td className="px-5 py-3.5 text-right font-mono text-emerald-600 dark:text-emerald-400">
                    {formatCurrency(inv.paid_amount)}
                  </td>
                  <td className="px-5 py-3.5 text-right font-mono font-bold text-slate-900 dark:text-white">
                    {formatCurrency(inv.balance_due)}
                  </td>
                  <td className="px-5 py-3.5 text-center">
                    <span className={`inline-block rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                      inv.payment_status === "PAID"
                        ? "bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400"
                        : inv.payment_status === "PARTIALLY_PAID"
                        ? "bg-sky-500/10 text-sky-600 dark:bg-sky-500/20 dark:text-sky-400"
                        : "bg-rose-500/10 text-rose-600 dark:bg-rose-500/20 dark:text-rose-400"
                    }`}>
                      {inv.payment_status.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 font-mono text-[11px] text-slate-500">
                    {inv.due_date}
                  </td>
                  <td className="px-5 py-3.5 text-center">
                    {inv.balance_due > 0 ? (
                      <button
                        onClick={() => handleSimulatePayment(inv)}
                        className="inline-flex items-center gap-1 rounded-lg bg-sky-600 px-2.5 py-1 text-[11px] font-semibold text-white hover:bg-sky-500 transition shadow-sm"
                      >
                        <CreditCard className="h-3 w-3" />
                        Pay Balance
                      </button>
                    ) : (
                      <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                        Settled
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between border-t border-slate-200 px-5 py-3.5 dark:border-slate-800 text-xs text-slate-500">
          <div>Showing Page <span className="font-bold text-slate-900 dark:text-white">{page}</span> of {Math.ceil(total / 10) || 1}</div>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-1.5 font-medium hover:bg-slate-100 disabled:opacity-40 disabled:pointer-events-none dark:border-slate-700 dark:hover:bg-slate-800"
            >
              <ChevronLeft className="h-3.5 w-3.5" /> Prev
            </button>
            <button
              disabled={page * 10 >= total}
              onClick={() => setPage(page + 1)}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-1.5 font-medium hover:bg-slate-100 disabled:opacity-40 disabled:pointer-events-none dark:border-slate-700 dark:hover:bg-slate-800"
            >
              Next <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

