import React from "react";
import { 
  Bell, 
  Search, 
  Sun, 
  Moon, 
  Database, 
  ShieldCheck, 
  ExternalLink,
  Cpu
} from "lucide-react";

export default function Header({ darkMode, setDarkMode, activeView, onSearch, searchQuery }) {
  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/95 px-6 backdrop-blur transition-colors dark:border-slate-800 dark:bg-[#0f172a]/95">
      {/* Left: Search & Breadcrumb */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 text-sm text-slate-500 dark:text-slate-400">
          <span className="font-semibold text-sky-600 dark:text-sky-400">EROMS</span>
          <span>/</span>
          <span className="capitalize text-slate-800 dark:text-slate-200">
            {activeView.replace("-", " ")}
          </span>
        </div>

        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search records, SKUs, queries..."
            value={searchQuery || ""}
            onChange={(e) => onSearch && onSearch(e.target.value)}
            className="h-9 w-64 rounded-lg border border-slate-200 bg-slate-50 pl-9 pr-4 text-xs font-medium text-slate-800 placeholder-slate-400 transition-all focus:border-sky-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-sky-500 dark:border-slate-700 dark:bg-slate-900/60 dark:text-slate-200 dark:placeholder-slate-500 dark:focus:border-sky-400"
          />
        </div>
      </div>

      {/* Right: DB Status + Theme Toggle + User Info */}
      <div className="flex items-center space-x-4">
        {/* PostgreSQL Live Engine Status Badge */}
        <div className="hidden lg:flex items-center space-x-2 rounded-full border border-emerald-500/30 bg-emerald-50/50 px-3 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
          </span>
          <Database className="h-3.5 w-3.5" />
          <span>PostgreSQL 16.4</span>
          <span className="text-emerald-400">|</span>
          <span>32 Relational Tables</span>
        </div>

        {/* ACID Transactions Badge */}
        <div className="hidden xl:flex items-center space-x-1.5 rounded-full border border-sky-500/20 bg-sky-50/50 px-3 py-1 text-xs font-medium text-sky-700 dark:bg-sky-950/40 dark:text-sky-300">
          <ShieldCheck className="h-3.5 w-3.5 text-sky-500" />
          <span>3NF • RLS Active</span>
        </div>

        {/* Dark Mode Toggle */}
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-slate-100 text-slate-600 transition-colors hover:bg-slate-200 dark:border-slate-800 dark:bg-slate-800/80 dark:text-slate-300 dark:hover:bg-slate-800"
          title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
        >
          {darkMode ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4 text-slate-600" />}
        </button>

        {/* Notifications */}
        <div className="relative">
          <button className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-slate-100 text-slate-600 hover:bg-slate-200 dark:border-slate-800 dark:bg-slate-800/80 dark:text-slate-300">
            <Bell className="h-4 w-4" />
            <span className="absolute right-1.5 top-1.5 flex h-2 w-2 rounded-full bg-rose-500" />
          </button>
        </div>

        {/* User Profile */}
        <div className="flex items-center space-x-3 border-l border-slate-200 pl-4 dark:border-slate-800">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-tr from-sky-600 to-indigo-600 text-sm font-semibold text-white shadow-sm ring-2 ring-sky-500/30">
            MA
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-semibold text-slate-900 dark:text-white flex items-center gap-1.5">
              Muhammad Afnan
              <a
                href="https://github.com/Afnan-makstrix"
                target="_blank"
                rel="noreferrer"
                className="text-slate-400 hover:text-sky-500"
                title="GitHub Profile"
              >
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
            <div className="text-[10px] font-medium text-slate-500 dark:text-slate-400">
              Lead Database Architect
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
