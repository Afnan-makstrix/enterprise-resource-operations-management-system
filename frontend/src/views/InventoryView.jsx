import React, { useState, useEffect } from "react";
import { Package, AlertCircle, CheckCircle, ChevronLeft, ChevronRight, Layers, ArrowDownRight, Warehouse } from "lucide-react";
import { api } from "../services/api";

export default function InventoryView() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInventory();
  }, [page, lowStockOnly]);

  const loadInventory = async () => {
    setLoading(true);
    const data = await api.getInventoryItems(page, lowStockOnly);
    setItems(data?.items || []);
    setTotal(data?.total || 0);
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-2xl">
            Inventory Catalog & Multi-Warehouse Logistics
          </h1>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Real-time stock balance calculated across warehouses with trigger-enforced ledger auditing.
          </p>
        </div>

        {/* Filter Toggle */}
        <div className="flex items-center gap-3">
          <label className="inline-flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-700 dark:text-slate-300">
            <input
              type="checkbox"
              checked={lowStockOnly}
              onChange={(e) => {
                setLowStockOnly(e.target.checked);
                setPage(1);
              }}
              className="h-4 w-4 rounded border-slate-300 text-sky-600 focus:ring-sky-500"
            />
            <span className="flex items-center gap-1.5 text-amber-600 dark:text-amber-400">
              <AlertCircle className="h-4 w-4" />
              Low Stock & Depleted Alerts Only
            </span>
          </label>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden dark:border-slate-800 dark:bg-slate-900/60">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
            <thead className="bg-slate-50 text-[11px] uppercase font-bold text-slate-500 dark:bg-slate-800/60 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="px-5 py-3.5">SKU & Item Name</th>
                <th className="px-5 py-3.5">Category</th>
                <th className="px-5 py-3.5 text-right">Unit Cost</th>
                <th className="px-5 py-3.5 text-right">Selling Price</th>
                <th className="px-5 py-3.5 text-right">Qty On Hand</th>
                <th className="px-5 py-3.5 text-right">Reorder Level</th>
                <th className="px-5 py-3.5 text-center">Stock Health</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-400">
                    Querying inventory ledger...
                  </td>
                </tr>
              ) : items.map((item) => (
                <tr key={item.item_id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="px-5 py-3.5 font-medium text-slate-900 dark:text-white">
                    <div className="font-semibold">{item.name}</div>
                    <div className="text-[10px] text-slate-400 font-mono">{item.sku}</div>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="inline-block rounded-md bg-slate-100 px-2 py-0.5 text-[11px] text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                      {item.category_name}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-right font-mono text-slate-600 dark:text-slate-400">
                    ${Number(item.cost_price).toFixed(2)}
                  </td>
                  <td className="px-5 py-3.5 text-right font-mono font-semibold text-slate-900 dark:text-white">
                    ${Number(item.selling_price).toFixed(2)}
                  </td>
                  <td className="px-5 py-3.5 text-right font-mono font-bold text-slate-900 dark:text-white">
                    {item.total_quantity_on_hand}
                  </td>
                  <td className="px-5 py-3.5 text-right font-mono text-slate-500">
                    {item.reorder_level}
                  </td>
                  <td className="px-5 py-3.5 text-center">
                    <span className={`inline-block rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                      item.stock_status === "OPTIMAL"
                        ? "bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400"
                        : item.stock_status === "LOW_STOCK"
                        ? "bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400"
                        : "bg-rose-500/10 text-rose-600 dark:bg-rose-500/20 dark:text-rose-400"
                    }`}>
                      {item.stock_status.replace("_", " ")}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between border-t border-slate-200 px-5 py-3.5 dark:border-slate-800 text-xs text-slate-500">
          <div>Showing <span className="font-bold text-slate-900 dark:text-white">{items.length}</span> of {total.toLocaleString()} SKUs</div>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-1.5 font-medium hover:bg-slate-100 disabled:opacity-40 disabled:pointer-events-none dark:border-slate-700 dark:hover:bg-slate-800"
            >
              <ChevronLeft className="h-3.5 w-3.5" /> Prev
            </button>
            <span className="font-mono text-slate-700 dark:text-slate-300">Page {page}</span>
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

