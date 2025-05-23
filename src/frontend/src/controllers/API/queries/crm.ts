import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { 
  Client, 
  ClientCreate, 
  ClientUpdate, 
  Invoice, 
  InvoiceCreate, 
  InvoiceUpdate, 
  Opportunity, 
  OpportunityCreate, 
  OpportunityUpdate, 
  Task, 
  TaskCreate, 
  TaskUpdate,
  DashboardStats,
  ClientDistribution,
  RecentActivityItem
} from "../../../types/crm";
import { apiClient } from "../api";

// Client API
export const useGetClients = (params?: { workspace_id?: string; status?: string }) => {
  return useQuery<Client[]>({
    queryKey: ['clients', params],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/clients', { params });
      return response.data;
    },
  });
};

export const useGetClient = (id: string) => {
  return useQuery<Client>({
    queryKey: ['client', id],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/clients/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateClient = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (client: ClientCreate) => {
      const response = await apiClient.post('/api/v1/clients', client);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useUpdateClient = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, client }: { id: string; client: ClientUpdate }) => {
      const response = await apiClient.patch(`/api/v1/clients/${id}`, client);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['client', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useDeleteClient = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/clients/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

// Invoice API
export const useGetInvoices = (params?: { workspace_id?: string; client_id?: string; status?: string }) => {
  return useQuery<Invoice[]>({
    queryKey: ['invoices', params],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/invoices', { params });
      return response.data;
    },
  });
};

export const useGetInvoice = (id: string) => {
  return useQuery<Invoice>({
    queryKey: ['invoice', id],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/invoices/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateInvoice = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (invoice: InvoiceCreate) => {
      const response = await apiClient.post('/api/v1/invoices', invoice);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useUpdateInvoice = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, invoice }: { id: string; invoice: InvoiceUpdate }) => {
      const response = await apiClient.patch(`/api/v1/invoices/${id}`, invoice);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['invoice', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useDeleteInvoice = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/invoices/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

// Opportunity API
export const useGetOpportunities = (params?: { workspace_id?: string; client_id?: string; status?: string }) => {
  return useQuery<Opportunity[]>({
    queryKey: ['opportunities', params],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/opportunities', { params });
      return response.data;
    },
  });
};

export const useGetOpportunity = (id: string) => {
  return useQuery<Opportunity>({
    queryKey: ['opportunity', id],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/opportunities/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateOpportunity = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (opportunity: OpportunityCreate) => {
      const response = await apiClient.post('/api/v1/opportunities', opportunity);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useUpdateOpportunity = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, opportunity }: { id: string; opportunity: OpportunityUpdate }) => {
      const response = await apiClient.patch(`/api/v1/opportunities/${id}`, opportunity);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
      queryClient.invalidateQueries({ queryKey: ['opportunity', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useDeleteOpportunity = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/opportunities/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

// Task API
export const useGetTasks = (params?: { 
  workspace_id?: string; 
  client_id?: string; 
  invoice_id?: string;
  opportunity_id?: string;
  assigned_to?: string;
  status?: string;
  priority?: string;
}) => {
  return useQuery<Task[]>({
    queryKey: ['tasks', params],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/tasks', { params });
      return response.data;
    },
  });
};

export const useGetTask = (id: string) => {
  return useQuery<Task>({
    queryKey: ['task', id],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/tasks/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateTask = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (task: TaskCreate) => {
      const response = await apiClient.post('/api/v1/tasks', task);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useUpdateTask = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, task }: { id: string; task: TaskUpdate }) => {
      const response = await apiClient.patch(`/api/v1/tasks/${id}`, task);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['task', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useDeleteTask = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/tasks/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

// Dashboard API
export const useGetWorkspaceStats = (workspaceId: string) => {
  return useQuery<DashboardStats>({
    queryKey: ['dashboard', 'stats', workspaceId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/dashboard/workspace/${workspaceId}/stats`);
      return response.data;
    },
    enabled: !!workspaceId,
  });
};

export const useGetClientDistribution = (workspaceId: string) => {
  return useQuery<ClientDistribution>({
    queryKey: ['dashboard', 'client-distribution', workspaceId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/dashboard/workspace/${workspaceId}/client-distribution`);
      return response.data;
    },
    enabled: !!workspaceId,
  });
};

export const useGetRecentActivity = (workspaceId: string, limit: number = 10) => {
  return useQuery<RecentActivityItem[]>({
    queryKey: ['dashboard', 'recent-activity', workspaceId, limit],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/dashboard/workspace/${workspaceId}/recent-activity`, {
        params: { limit },
      });
      return response.data;
    },
    enabled: !!workspaceId,
  });
};
