# Workspace Dashboard & CRM Frontend Implementation Plan

## Frontend Component Structure

### 1. Dashboard Components

#### File: `src/frontend/src/components/core/dashboardComponents/index.tsx`
```tsx
import { useEffect, useState } from "react";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { useDashboardStore } from "@/stores/dashboardStore";
import { useGetWorkspaceStatsQuery } from "@/api/dashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import WorkspaceStatsCard from "./workspaceStatsCard";
import ClientDistributionChart from "./clientDistributionChart";
import RevenueTimelineChart from "./revenueTimelineChart";
import TaskPriorityChart from "./taskPriorityChart";
import RecentActivityList from "./recentActivityList";
import UpcomingTasksList from "./upcomingTasksList";

export default function DashboardComponent() {
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);
  const { data: workspaceStats, isLoading: isLoadingStats } = useGetWorkspaceStatsQuery(
    currentWorkspaceId!,
    { skip: !currentWorkspaceId }
  );

  if (!currentWorkspaceId) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <p className="text-muted-foreground">Please select a workspace to view the dashboard.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="mb-6 text-2xl font-bold">Dashboard</h1>
      
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Workspace Stats Card */}
        <Card className="col-span-1 md:col-span-2 lg:col-span-1">
          <CardHeader>
            <CardTitle>Workspace Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <WorkspaceStatsCard stats={workspaceStats} isLoading={isLoadingStats} />
          </CardContent>
        </Card>
        
        {/* Client Distribution Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Client Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ClientDistributionChart workspaceId={currentWorkspaceId} />
          </CardContent>
        </Card>
        
        {/* Revenue Timeline Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Revenue Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <RevenueTimelineChart workspaceId={currentWorkspaceId} />
          </CardContent>
        </Card>
      </div>
      
      <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <RecentActivityList workspaceId={currentWorkspaceId} />
          </CardContent>
        </Card>
        
        {/* Upcoming Tasks */}
        <Card>
          <CardHeader>
            <CardTitle>Upcoming Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <UpcomingTasksList workspaceId={currentWorkspaceId} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

#### File: `src/frontend/src/components/core/dashboardComponents/workspaceStatsCard.tsx`
```tsx
import { Skeleton } from "@/components/ui/skeleton";
import { WorkspaceStats } from "@/types/dashboard";

interface WorkspaceStatsCardProps {
  stats?: WorkspaceStats;
  isLoading: boolean;
}

export default function WorkspaceStatsCard({ stats, isLoading }: WorkspaceStatsCardProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-4">
        <StatSkeleton />
        <StatSkeleton />
        <StatSkeleton />
        <StatSkeleton />
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center text-muted-foreground">
        No statistics available
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      <StatItem
        label="Clients"
        value={stats.clients.total}
        subValue={`${stats.clients.active} active`}
      />
      <StatItem
        label="Revenue"
        value={`$${stats.invoices.revenue.toLocaleString()}`}
        subValue={`${stats.invoices.total} invoices`}
      />
      <StatItem
        label="Opportunities"
        value={stats.opportunities.total}
        subValue={`$${stats.opportunities.open_value.toLocaleString()} open value`}
      />
      <StatItem
        label="Tasks"
        value={stats.tasks.open + stats.tasks.in_progress}
        subValue={`${stats.tasks.completed} completed`}
      />
    </div>
  );
}

interface StatItemProps {
  label: string;
  value: string | number;
  subValue?: string;
}

function StatItem({ label, value, subValue }: StatItemProps) {
  return (
    <div className="flex flex-col">
      <span className="text-sm font-medium text-muted-foreground">{label}</span>
      <span className="text-2xl font-bold">{value}</span>
      {subValue && <span className="text-xs text-muted-foreground">{subValue}</span>}
    </div>
  );
}

function StatSkeleton() {
  return (
    <div className="flex flex-col space-y-2">
      <Skeleton className="h-4 w-20" />
      <Skeleton className="h-8 w-16" />
      <Skeleton className="h-3 w-24" />
    </div>
  );
}
```

#### File: `src/frontend/src/components/core/dashboardComponents/clientDistributionChart.tsx`
```tsx
import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { useGetClientDistributionQuery } from "@/api/dashboard";
import { Skeleton } from "@/components/ui/skeleton";

interface ClientDistributionChartProps {
  workspaceId: string;
}

export default function ClientDistributionChart({ workspaceId }: ClientDistributionChartProps) {
  const { data, isLoading } = useGetClientDistributionQuery(workspaceId);
  const chartRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || !chartRef.current) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll("*").remove();

    // Prepare data for pie chart
    const pieData = [
      { label: "Active", value: data.active, color: "#10b981" },
      { label: "Inactive", value: data.inactive, color: "#6b7280" },
      { label: "Lead", value: data.lead, color: "#3b82f6" },
    ];

    // Set up dimensions
    const width = chartRef.current.clientWidth;
    const height = 200;
    const radius = Math.min(width, height) / 2;

    // Create SVG
    const svg = d3
      .select(chartRef.current)
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2}, ${height / 2})`);

    // Create pie chart
    const pie = d3.pie<any>().value((d: any) => d.value);
    const arc = d3.arc().innerRadius(0).outerRadius(radius);

    // Draw pie segments
    svg
      .selectAll("path")
      .data(pie(pieData))
      .enter()
      .append("path")
      .attr("d", arc as any)
      .attr("fill", (d: any) => d.data.color)
      .attr("stroke", "white")
      .style("stroke-width", "2px");

    // Add legend
    const legend = svg
      .selectAll(".legend")
      .data(pieData)
      .enter()
      .append("g")
      .attr("class", "legend")
      .attr("transform", (d, i) => `translate(${radius + 10}, ${-radius + 20 + i * 20})`);

    legend
      .append("rect")
      .attr("width", 12)
      .attr("height", 12)
      .attr("fill", (d) => d.color);

    legend
      .append("text")
      .attr("x", 20)
      .attr("y", 10)
      .text((d) => `${d.label} (${d.value})`)
      .style("font-size", "12px");
  }, [data]);

  if (isLoading) {
    return <Skeleton className="h-[200px] w-full" />;
  }

  if (!data || (data.active === 0 && data.inactive === 0 && data.lead === 0)) {
    return (
      <div className="flex h-[200px] w-full items-center justify-center">
        <p className="text-sm text-muted-foreground">No client data available</p>
      </div>
    );
  }

  return <svg ref={chartRef} className="w-full" />;
}
```

### 2. CRM Components

#### File: `src/frontend/src/components/core/crmComponents/clientsTable.tsx`
```tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  useGetClientsQuery, 
  useDeleteClientMutation 
} from "@/api/clients";
import { Client } from "@/types/crm";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { 
  MoreHorizontal, 
  Plus, 
  Search, 
  Edit, 
  Trash2 
} from "lucide-react";
import { formatDate } from "@/utils/date";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { useToast } from "@/hooks/use-toast";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";

export default function ClientsTable() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);
  
  const { data: clients, isLoading, refetch } = useGetClientsQuery(
    { workspaceId: currentWorkspaceId! },
    { skip: !currentWorkspaceId }
  );
  
  const [deleteClient] = useDeleteClientMutation();

  const filteredClients = clients?.filter((client) =>
    client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (client.company && client.company.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleCreateClient = () => {
    navigate("/crm/clients/new");
  };

  const handleEditClient = (clientId: string) => {
    navigate(`/crm/clients/${clientId}/edit`);
  };

  const handleViewClient = (clientId: string) => {
    navigate(`/crm/clients/${clientId}`);
  };

  const handleDeleteClient = async (clientId: string) => {
    try {
      await deleteClient(clientId).unwrap();
      toast({
        title: "Client deleted",
        description: "The client has been successfully deleted.",
      });
      refetch();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete client. Please try again.",
        variant: "destructive",
      });
    }
  };

  if (!currentWorkspaceId) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <p className="text-muted-foreground">Please select a workspace to view clients.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Clients</h1>
        <Button onClick={handleCreateClient}>
          <Plus className="mr-2 h-4 w-4" />
          New Client
        </Button>
      </div>

      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search clients..."
            className="pl-8"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="flex h-40 items-center justify-center">
          <p className="text-muted-foreground">Loading clients...</p>
        </div>
      ) : filteredClients && filteredClients.length > 0 ? (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Company</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-[80px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredClients.map((client) => (
              <TableRow key={client.id} onClick={() => handleViewClient(client.id)} className="cursor-pointer">
                <TableCell className="font-medium">{client.name}</TableCell>
                <TableCell>{client.company || "-"}</TableCell>
                <TableCell>{client.email || "-"}</TableCell>
                <TableCell>
                  <ClientStatusBadge status={client.status} />
                </TableCell>
                <TableCell>{formatDate(client.created_at)}</TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" className="h-8 w-8 p-0">
                        <span className="sr-only">Open menu</span>
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={(e) => {
                        e.stopPropagation();
                        handleEditClient(client.id);
                      }}>
                        <Edit className="mr-2 h-4 w-4" />
                        Edit
                      </DropdownMenuItem>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <DropdownMenuItem
                            onSelect={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                            }}
                            className="text-destructive focus:text-destructive"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </AlertDialogTrigger>
                        <AlertDialogContent onClick={(e) => e.stopPropagation()}>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                            <AlertDialogDescription>
                              This will permanently delete the client and all associated data.
                              This action cannot be undone.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteClient(client.id);
                              }}
                              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            >
                              Delete
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <div className="flex h-40 flex-col items-center justify-center rounded-md border border-dashed p-8 text-center">
          <p className="mb-2 text-sm text-muted-foreground">
            {searchTerm ? "No clients found matching your search." : "No clients found."}
          </p>
          <Button onClick={handleCreateClient} variant="outline" size="sm">
            <Plus className="mr-2 h-4 w-4" />
            Add your first client
          </Button>
        </div>
      )}
    </div>
  );
}

function ClientStatusBadge({ status }: { status: string }) {
  const getStatusStyles = () => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300";
      case "inactive":
        return "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300";
      case "lead":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300";
    }
  };

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusStyles()}`}
    >
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
```

### 3. API Hooks

#### File: `src/frontend/src/api/dashboard.ts`
```tsx
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { API_BASE_URL } from "@/constants/constants";
import { WorkspaceStats, ClientDistribution } from "@/types/dashboard";

export const dashboardApi = createApi({
  reducerPath: "dashboardApi",
  baseQuery: fetchBaseQuery({
    baseUrl: API_BASE_URL,
    prepareHeaders: (headers) => {
      const token = localStorage.getItem("access_token");
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ["WorkspaceStats", "ClientDistribution"],
  endpoints: (builder) => ({
    getWorkspaceStats: builder.query<WorkspaceStats, string>({
      query: (workspaceId) => `/api/v1/dashboard/workspace/${workspaceId}/stats`,
      providesTags: ["WorkspaceStats"],
    }),
    getClientDistribution: builder.query<ClientDistribution, string>({
      query: (workspaceId) => `/api/v1/dashboard/workspace/${workspaceId}/client-distribution`,
      providesTags: ["ClientDistribution"],
    }),
  }),
});

export const { useGetWorkspaceStatsQuery, useGetClientDistributionQuery } = dashboardApi;
```

#### File: `src/frontend/src/api/clients.ts`
```tsx
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { API_BASE_URL } from "@/constants/constants";
import { Client, ClientCreate, ClientUpdate } from "@/types/crm";

export const clientsApi = createApi({
  reducerPath: "clientsApi",
  baseQuery: fetchBaseQuery({
    baseUrl: API_BASE_URL,
    prepareHeaders: (headers) => {
      const token = localStorage.getItem("access_token");
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ["Clients"],
  endpoints: (builder) => ({
    getClients: builder.query<Client[], { workspaceId: string; status?: string }>({
      query: ({ workspaceId, status }) => {
        let url = `/api/v1/clients?workspace_id=${workspaceId}`;
        if (status) {
          url += `&status=${status}`;
        }
        return url;
      },
      providesTags: ["Clients"],
    }),
    getClient: builder.query<Client, string>({
      query: (clientId) => `/api/v1/clients/${clientId}`,
      providesTags: (result, error, id) => [{ type: "Clients", id }],
    }),
    createClient: builder.mutation<Client, ClientCreate>({
      query: (client) => ({
        url: "/api/v1/clients",
        method: "POST",
        body: client,
      }),
      invalidatesTags: ["Clients"],
    }),
    updateClient: builder.mutation<Client, { id: string; client: ClientUpdate }>({
      query: ({ id, client }) => ({
        url: `/api/v1/clients/${id}`,
        method: "PATCH",
        body: client,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Clients", id },
        "Clients",
      ],
    }),
    deleteClient: builder.mutation<void, string>({
      query: (id) => ({
        url: `/api/v1/clients/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Clients"],
    }),
  }),
});

export const {
  useGetClientsQuery,
  useGetClientQuery,
  useCreateClientMutation,
  useUpdateClientMutation,
  useDeleteClientMutation,
} = clientsApi;
```

### 4. Type Definitions

#### File: `src/frontend/src/types/dashboard.ts`
```tsx
export interface WorkspaceStats {
  clients: {
    total: number;
    active: number;
  };
  invoices: {
    total: number;
    revenue: number;
  };
  opportunities: {
    total: number;
    open_value: number;
  };
  tasks: {
    open: number;
    in_progress: number;
    completed: number;
  };
}

export interface ClientDistribution {
  active: number;
  inactive: number;
  lead: number;
}
```

#### File: `src/frontend/src/types/crm.ts`
```tsx
export interface Client {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  company: string | null;
  description: string | null;
  status: string;
  workspace_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface ClientCreate {
  name: string;
  email?: string | null;
  phone?: string | null;
  company?: string | null;
  description?: string | null;
  status?: string;
  workspace_id: string;
}

export interface ClientUpdate {
  name?: string;
  email?: string | null;
  phone?: string | null;
  company?: string | null;
  description?: string | null;
  status?: string;
}

export interface Invoice {
  id: string;
  invoice_number: string;
  amount: number;
  status: string;
  issue_date: string;
  due_date: string | null;
  description: string | null;
  workspace_id: string;
  client_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Opportunity {
  id: string;
  name: string;
  value: number | null;
  status: string;
  description: string | null;
  expected_close_date: string | null;
  workspace_id: string;
  client_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: string;
  priority: string;
  due_date: string | null;
  workspace_id: string;
  created_by: string;
  assigned_to: string | null;
  client_id: string | null;
  invoice_id: string | null;
  opportunity_id: string | null;
  created_at: string;
  updated_at: string;
}
```

### 5. Store Configuration

#### File: `src/frontend/src/stores/dashboardStore.ts`
```tsx
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface DashboardStoreType {
  // Dashboard view preferences
  activeTab: string;
  setActiveTab: (tab: string) => void;
  
  // Dashboard filters
  dateRange: [Date | null, Date | null];
  setDateRange: (range: [Date | null, Date | null]) => void;
  
  // Reset store
  resetStore: () => void;
}

const useDashboardStore = create<DashboardStoreType>()(
  persist(
    (set) => ({
      // Dashboard view preferences
      activeTab: "overview",
      setActiveTab: (tab) => set({ activeTab: tab }),
      
      // Dashboard filters
      dateRange: [null, null],
      setDateRange: (range) => set({ dateRange: range }),
      
      // Reset store
      resetStore: () =>
        set({
          activeTab: "overview",
          dateRange: [null, null],
        }),
    }),
    {
      name: "dashboard-store",
    }
  )
);

export default useDashboardStore;
```

### 6. Routing Configuration

#### File: `src/frontend/src/routes.tsx` (Update)
```tsx
// Add new imports
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const ClientsPage = lazy(() => import("./pages/CRM/ClientsPage"));
const ClientDetailsPage = lazy(() => import("./pages/CRM/ClientDetailsPage"));
const ClientFormPage = lazy(() => import("./pages/CRM/ClientFormPage"));
const InvoicesPage = lazy(() => import("./pages/CRM/InvoicesPage"));
const InvoiceDetailsPage = lazy(() => import("./pages/CRM/InvoiceDetailsPage"));
const InvoiceFormPage = lazy(() => import("./pages/CRM/InvoiceFormPage"));

// Add new routes inside the authenticated routes section
<Route path="" element={<AppAuthenticatedPage />}>
  <Route path="" element={<CustomDashboardWrapperPage />}>
    {/* Existing routes */}
    
    {/* New Dashboard route */}
    <Route path="dashboard" element={<DashboardPage />} />
    
    {/* New CRM routes */}
    <Route path="crm">
      <Route path="clients" element={<ClientsPage />} />
      <Route path="clients/new" element={<ClientFormPage />} />
      <Route path="clients/:clientId" element={<ClientDetailsPage />} />
      <Route path="clients/:clientId/edit" element={<ClientFormPage />} />
      
      <Route path="invoices" element={<InvoicesPage />} />
      <Route path="invoices/new" element={<InvoiceFormPage />} />
      <Route path="invoices/:invoiceId" element={<InvoiceDetailsPage />} />
      <Route path="invoices/:invoiceId/edit" element={<InvoiceFormPage />} />
      
      {/* Add similar routes for opportunities and tasks */}
    </Route>
  </Route>
</Route>
```

### 7. Sidebar Navigation Update

#### File: `src/frontend/src/components/core/sidebarComponent/index.tsx` (Update)
```tsx
// Add new imports
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  TrendingUp, 
  CheckSquare 
} from "lucide-react";

// Update the items array in SideBarButtonsComponent
const items = [
  {
    href: "/dashboard",
    title: "Dashboard",
    icon: <LayoutDashboard className="h-5 w-5" />,
  },
  {
    href: "/flows",
    title: "Flows",
    icon: <Flow className="h-5 w-5" />,
  },
  {
    href: "/crm/clients",
    title: "Clients",
    icon: <Users className="h-5 w-5" />,
  },
  {
    href: "/crm/invoices",
    title: "Invoices",
    icon: <FileText className="h-5 w-5" />,
  },
  {
    href: "/crm/opportunities",
    title: "Opportunities",
    icon: <TrendingUp className="h-5 w-5" />,
  },
  {
    href: "/crm/tasks",
    title: "Tasks",
    icon: <CheckSquare className="h-5 w-5" />,
  },
  // ... other existing items
];
```

This frontend implementation plan provides a comprehensive approach to building the Dashboard and CRM UI components, with proper API integration, state management, and routing configuration.
