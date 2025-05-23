import { useWorkspaceStore } from "@/stores/workspaceStore";
import { useGetClientDistributionQuery, useGetRecentActivityQuery, useGetWorkspaceStatsQuery } from "@/controllers/API/queries/crm";
import { StatCard } from "./components/StatCard";
import { ClientDistributionChart } from "./components/ClientDistributionChart";
import { RecentActivityList } from "./components/RecentActivityList";
import { UpcomingTasksList } from "./components/UpcomingTasksList";
import { Users, FileText, TrendingUp, CheckSquare, DollarSign, BarChart } from "lucide-react";
import CRMSidebarComponent from "@/components/core/crmSidebarComponent";

export default function DashboardPage() {
  // Get current workspace ID
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);

  // Fetch workspace stats
  const { data: stats, isLoading: isLoadingStats } = useGetWorkspaceStatsQuery(
    currentWorkspaceId || "",
    {
      enabled: !!currentWorkspaceId,
    }
  );

  // Fetch client distribution
  const { data: clientDistribution, isLoading: isLoadingDistribution } = useGetClientDistributionQuery(
    currentWorkspaceId || "",
    {
      enabled: !!currentWorkspaceId,
    }
  );

  // Fetch recent activity
  const { data: recentActivity, isLoading: isLoadingActivity } = useGetRecentActivityQuery(
    currentWorkspaceId || "",
    {
      enabled: !!currentWorkspaceId,
    }
  );

  // Format currency
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="flex h-full">
      <CRMSidebarComponent />
      <div className="flex-1 overflow-auto p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Overview of your CRM metrics and activities
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          <StatCard
            title="Total Clients"
            value={stats?.clients.total || 0}
            icon={<Users className="h-4 w-4" />}
            description={`${stats?.clients.active || 0} active clients`}
            isLoading={isLoadingStats}
          />
          <StatCard
            title="Total Invoices"
            value={stats?.invoices.total || 0}
            icon={<FileText className="h-4 w-4" />}
            isLoading={isLoadingStats}
          />
          <StatCard
            title="Revenue"
            value={formatCurrency(stats?.invoices.revenue || 0)}
            icon={<DollarSign className="h-4 w-4" />}
            isLoading={isLoadingStats}
          />
          <StatCard
            title="Open Opportunities"
            value={stats?.opportunities.total || 0}
            icon={<TrendingUp className="h-4 w-4" />}
            description={`Potential value: ${formatCurrency(stats?.opportunities.open_value || 0)}`}
            isLoading={isLoadingStats}
          />
          <StatCard
            title="Open Tasks"
            value={stats?.tasks.open || 0}
            icon={<CheckSquare className="h-4 w-4" />}
            description={`${stats?.tasks.in_progress || 0} in progress, ${stats?.tasks.completed || 0} completed`}
            isLoading={isLoadingStats}
          />
          <StatCard
            title="Conversion Rate"
            value={stats && stats.opportunities.total > 0
              ? `${Math.round((stats.clients.active / stats.clients.total) * 100)}%`
              : "0%"
            }
            icon={<BarChart className="h-4 w-4" />}
            isLoading={isLoadingStats}
          />
        </div>

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <ClientDistributionChart
            data={clientDistribution}
            isLoading={isLoadingDistribution}
          />
          <RecentActivityList
            data={recentActivity}
            isLoading={isLoadingActivity}
          />
        </div>

        <div className="mt-6">
          <UpcomingTasksList workspaceId={currentWorkspaceId} />
        </div>
      </div>
    </div>
  );
}
