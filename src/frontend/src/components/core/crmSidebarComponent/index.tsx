import { useCRMStore } from "@/stores/crmStore";
import { cn } from "@/lib/utils";
import { useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  FileText,
  TrendingUp,
  CheckSquare,
  Settings,
  BarChart,
  Package,
} from "lucide-react";

/**
 * CRM Sidebar Component
 *
 * Provides navigation for the CRM module with links to dashboard, clients, invoices, etc.
 */
export default function CRMSidebarComponent() {
  const navigate = useNavigate();
  const location = useLocation();
  const activeView = useCRMStore((state) => state.activeView);
  const setActiveView = useCRMStore((state) => state.setActiveView);

  // Navigation items
  const navItems = [
    {
      name: "Dashboard",
      path: "/crm/dashboard",
      icon: <LayoutDashboard className="h-5 w-5" />,
      view: "dashboard" as const,
    },
    {
      name: "Clients",
      path: "/crm/clients",
      icon: <Users className="h-5 w-5" />,
      view: "clients" as const,
    },
    {
      name: "Invoices",
      path: "/crm/invoices",
      icon: <FileText className="h-5 w-5" />,
      view: "invoices" as const,
    },
    {
      name: "Opportunities",
      path: "/crm/opportunities",
      icon: <TrendingUp className="h-5 w-5" />,
      view: "opportunities" as const,
    },
    {
      name: "Tasks",
      path: "/crm/tasks",
      icon: <CheckSquare className="h-5 w-5" />,
      view: "tasks" as const,
    },
    {
      name: "Products",
      path: "/crm/products",
      icon: <Package className="h-5 w-5" />,
      view: "products" as const,
    },
    {
      name: "Reports",
      path: "/crm/reports",
      icon: <BarChart className="h-5 w-5" />,
      view: "reports" as const,
    },
  ];

  // Handle navigation
  const handleNavigation = (path: string, view: typeof activeView) => {
    navigate(path);
    setActiveView(view);
  };

  // Check if a path is active
  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  return (
    <div className="flex h-full w-64 flex-col border-r bg-background">
      <div className="flex h-14 items-center border-b px-4">
        <h2 className="text-lg font-semibold">CRM</h2>
      </div>
      <div className="flex-1 overflow-auto py-2">
        <nav className="grid gap-1 px-2">
          {navItems.map((item) => (
            <button
              key={item.path}
              onClick={() => handleNavigation(item.path, item.view)}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium",
                isActive(item.path)
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              {item.icon}
              {item.name}
            </button>
          ))}
        </nav>
      </div>
      <div className="mt-auto border-t p-4">
        <button
          onClick={() => navigate("/settings")}
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        >
          <Settings className="h-5 w-5" />
          Settings
        </button>
      </div>
    </div>
  );
}
