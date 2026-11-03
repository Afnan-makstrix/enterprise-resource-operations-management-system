import React, { useState, useEffect } from "react";
import { Briefcase, CheckCircle2, Clock, AlertTriangle, Layers, ChevronLeft, ChevronRight, DollarSign } from "lucide-react";
import { api } from "../services/api";

export default function ProjectsView() {
  const [projects, setProjects] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, [page]);

  const loadProjects = async () => {
    setLoading(true);
    const data = await api.getProjects(page);
    setProjects(data?.items || []);
    setTotal(data?.total || 0);
    setLoading(false);
  };

  const formatCurrency = (val) => {
    if (!val && val !== 0) return "$0";
    if (val >= 1000000) return `$${(val / 1000000).toFixed(2)}M`;
    if (val >= 1000) return `$${(val / 1000).toFixed(0)}k`;
    return `$${val.toLocaleString()}`;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-2xl">
            Enterprise Projects & Workflow Deliverables
          </h1>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Lifecycle monitoring across 1,200 client engagements, 8,000 tasks, and linked cost accounting.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-indigo-500/10 px-3 py-1 text-xs font-semibold text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400">
            {total.toLocaleString()} Total Projects
          </span>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {projects.map((prj) => {
          const taskCompletion = prj.total_tasks > 0 ? Math.round((prj.completed_tasks / prj.total_tasks) * 100) : 0;
          return (
            <div
              key={prj.project_id}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md dark:border-slate-800 dark:bg-slate-900/60"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[10px] font-mono font-bold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                      {prj.project_code}
                    </span>
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                      prj.priority === "CRITICAL"
                        ? "bg-rose-500/10 text-rose-600 dark:bg-rose-500/20 dark:text-rose-400"
                        : prj.priority === "HIGH"
                        ? "bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400"
                        : "bg-sky-500/10 text-sky-600 dark:bg-sky-500/20 dark:text-sky-400"
                    }`}>
                      {prj.priority}
                    </span>
                  </div>

                  <h3 className="mt-2 text-base font-bold text-slate-900 dark:text-white">
                    {prj.name}
                  </h3>
                  <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                    Client: <span className="font-semibold text-slate-700 dark:text-slate-300">{prj.client_name}</span>
                  </p>
                </div>

                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                  prj.status === "COMPLETED"
                    ? "bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400"
                    : prj.status === "IN_PROGRESS"
                    ? "bg-sky-500/10 text-sky-600 dark:bg-sky-500/20 dark:text-sky-400"
                    : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
                }`}>
                  {prj.status}
                </span>
              </div>

              {/* Financial Progress */}
              <div className="mt-4 grid grid-cols-2 gap-3 border-t border-slate-100 pt-3 dark:border-slate-800/80">
                <div>
                  <div className="text-[10px] uppercase font-semibold text-slate-400">Contract Budget</div>
                  <div className="text-sm font-bold text-slate-900 dark:text-white font-mono">
                    {formatCurrency(prj.budget)}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] uppercase font-semibold text-slate-400">Cost Incurred</div>
                  <div className="text-sm font-bold text-slate-700 dark:text-slate-300 font-mono">
                    {formatCurrency(prj.cost_to_date)}
                  </div>
                </div>
              </div>

              {/* Task Progress Bar */}
              <div className="mt-4">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 dark:text-slate-400">
                    Tasks: {prj.completed_tasks} / {prj.total_tasks} finished
                  </span>
                  <span className="font-semibold text-slate-900 dark:text-white">{taskCompletion}%</span>
                </div>
                <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                  <div
                    style={{ width: `${taskCompletion}%` }}
                    className="h-full rounded-full bg-indigo-500 transition-all duration-500"
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between border-t border-slate-200 pt-4 dark:border-slate-800 text-xs text-slate-500">
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
  );
}
