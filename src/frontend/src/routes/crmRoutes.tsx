import { Route } from "react-router-dom";
import CRMPage from "../pages/CRMPage";
import DashboardPage from "../pages/CRMPage/DashboardPage";
import ClientsPage from "../pages/CRMPage/ClientsPage";
import InvoicesPage from "../pages/CRMPage/InvoicesPage";
import OpportunitiesPage from "../pages/CRMPage/OpportunitiesPage";
import TasksPage from "../pages/CRMPage/TasksPage";
import ReportsPage from "../pages/CRMPage/ReportsPage";

/**
 * CRM Routes definition
 *
 * This function returns the route definitions for the CRM module
 * including the main CRM page and its sub-pages (dashboard, clients, etc.)
 */
export const CRMRoutes = () => {
  return (
    <Route path="crm" element={<CRMPage />}>
      <Route index element={<DashboardPage />} />
      <Route path="dashboard" element={<DashboardPage />} />
      <Route path="clients" element={<ClientsPage />} />
      <Route path="invoices" element={<InvoicesPage />} />
      <Route path="opportunities" element={<OpportunitiesPage />} />
      <Route path="tasks" element={<TasksPage />} />
      <Route path="reports" element={<ReportsPage />} />
    </Route>
  );
};
