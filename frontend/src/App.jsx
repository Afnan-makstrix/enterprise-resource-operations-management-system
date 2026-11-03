import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import DashboardView from "./views/DashboardView";
import EmployeesView from "./views/EmployeesView";
import DepartmentsView from "./views/DepartmentsView";
import ProjectsView from "./views/ProjectsView";
import InventoryView from "./views/InventoryView";
import BillingView from "./views/BillingView";
import SqlExplorerView from "./views/SqlExplorerView";
import AuditView from "./views/AuditView";
import BenchmarksView from "./views/BenchmarksView";

export default function App() {
  const [activeView, setActiveView] = useState("dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  const renderActiveView = () => {
    switch (activeView) {
      case "dashboard":
        return <DashboardView onNavigate={(view) => setActiveView(view)} />;
      case "employees":
        return <EmployeesView />;
      case "departments":
        return <DepartmentsView />;
      case "projects":
        return <ProjectsView />;
      case "inventory":
        return <InventoryView />;
      case "billing":
        return <BillingView />;
      case "sql-explorer":
        return <SqlExplorerView />;
      case "audit":
        return <AuditView />;
      case "benchmarks":
        return <BenchmarksView />;
      default:
        return <DashboardView onNavigate={(view) => setActiveView(view)} />;
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 font-sans text-slate-900 transition-colors duration-200 dark:bg-[#0B0F19] dark:text-[#F3F4F6]">
      {/* Sidebar Navigation */}
      <Sidebar
        activeView={activeView}
        setActiveView={setActiveView}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header
          darkMode={darkMode}
          setDarkMode={setDarkMode}
          activeView={activeView}
          searchQuery={searchQuery}
          onSearch={(query) => setSearchQuery(query)}
        />

        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-7xl">
            {renderActiveView()}
          </div>
        </main>
      </div>
    </div>
  );
}
