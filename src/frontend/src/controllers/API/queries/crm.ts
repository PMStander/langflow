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
  RecentActivityItem,
  Product,
  ProductCreate,
  ProductUpdate
} from "../../../types/crm";
import {
  PaginatedClients,
  PaginatedInvoices,
  PaginatedOpportunities,
  PaginatedTasks,
  PaginatedResponse,
  PaginationParams,
  extractItems,
  isPaginated
} from "../../../types/crm/pagination";
import { api as apiClient } from "../api";

// Type alias for paginated products
export type PaginatedProducts = PaginatedResponse<Product>;

// Client API
export const useGetClients = (params?: { workspace_id?: string; status?: string } & PaginationParams) => {
  return useQuery<PaginatedClients | Client[]>({
    queryKey: ['clients', params],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/clients', { params });
      return response.data;
    },
    select: (data) => {
      // Handle both paginated and non-paginated responses for backward compatibility
      if (isPaginated(data)) {
        return data;
      }
      // If it's an array, it's the old format
      return {
        items: data,
        metadata: {
          total: data.length,
          page: 1,
          size: data.length,
          pages: 1,
          has_next: false,
          has_prev: false,
          next_page: null,
          prev_page: null
        }
      };
    }
  });
};

export const useGetClientsQuery = useGetClients;

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

export const useGetClientQuery = useGetClient;

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

export const useCreateClientMutation = useCreateClient;

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

export const useUpdateClientMutation = useUpdateClient;

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

export const useDeleteClientMutation = useDeleteClient;

// Invoice API
export const useGetInvoices = (params?: { workspace_id?: string; client_id?: string; status?: string } & PaginationParams) => {
  return useQuery<PaginatedInvoices | Invoice[]>({
    queryKey: ['invoices', params],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/invoices', { params });
      return response.data;
    },
    select: (data) => {
      // Handle both paginated and non-paginated responses for backward compatibility
      if (isPaginated(data)) {
        return data;
      }
      // If it's an array, it's the old format
      return {
        items: data,
        metadata: {
          total: data.length,
          page: 1,
          size: data.length,
          pages: 1,
          has_next: false,
          has_prev: false,
          next_page: null,
          prev_page: null
        }
      };
    }
  });
};

export const useGetInvoicesQuery = useGetInvoices;

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

export const useGetInvoiceQuery = useGetInvoice;

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

export const useCreateInvoiceMutation = useCreateInvoice;

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

export const useUpdateInvoiceMutation = useUpdateInvoice;

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

export const useDeleteInvoiceMutation = useDeleteInvoice;

// Opportunity API
export const useGetOpportunities = (params?: { workspace_id?: string; client_id?: string; status?: string } & PaginationParams) => {
  return useQuery<PaginatedOpportunities | Opportunity[]>({
    queryKey: ['opportunities', params],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/opportunities', { params });
      return response.data;
    },
    select: (data) => {
      // Handle both paginated and non-paginated responses for backward compatibility
      if (isPaginated(data)) {
        return data;
      }
      // If it's an array, it's the old format
      return {
        items: data,
        metadata: {
          total: data.length,
          page: 1,
          size: data.length,
          pages: 1,
          has_next: false,
          has_prev: false,
          next_page: null,
          prev_page: null
        }
      };
    }
  });
};

export const useGetOpportunitiesQuery = useGetOpportunities;

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

export const useGetOpportunityQuery = useGetOpportunity;

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

export const useCreateOpportunityMutation = useCreateOpportunity;

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

export const useUpdateOpportunityMutation = useUpdateOpportunity;

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

export const useDeleteOpportunityMutation = useDeleteOpportunity;

// Task API
export const useGetTasks = (params?: {
  workspace_id?: string;
  client_id?: string;
  invoice_id?: string;
  opportunity_id?: string;
  assigned_to?: string;
  status?: string;
  priority?: string;
} & PaginationParams) => {
  return useQuery<PaginatedTasks | Task[]>({
    queryKey: ['tasks', params],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/tasks', { params });
      return response.data;
    },
    select: (data) => {
      // Handle both paginated and non-paginated responses for backward compatibility
      if (isPaginated(data)) {
        return data;
      }
      // If it's an array, it's the old format
      return {
        items: data,
        metadata: {
          total: data.length,
          page: 1,
          size: data.length,
          pages: 1,
          has_next: false,
          has_prev: false,
          next_page: null,
          prev_page: null
        }
      };
    }
  });
};

export const useGetTasksQuery = useGetTasks;

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

export const useGetTaskQuery = useGetTask;

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

export const useCreateTaskMutation = useCreateTask;

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

export const useUpdateTaskMutation = useUpdateTask;

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

export const useDeleteTaskMutation = useDeleteTask;

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

export const useGetWorkspaceStatsQuery = useGetWorkspaceStats;

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

export const useGetClientDistributionQuery = useGetClientDistribution;

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

export const useGetRecentActivityQuery = useGetRecentActivity;

// Product API
export const useGetProducts = (params?: { workspace_id?: string; status?: string } & PaginationParams) => {
  return useQuery<PaginatedProducts | Product[]>({
    queryKey: ['products', params],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/products', { params });
      return response.data;
    },
    select: (data) => {
      // Handle both paginated and non-paginated responses for backward compatibility
      if (isPaginated(data)) {
        return data;
      }
      // If it's an array, it's the old format
      return {
        items: data,
        metadata: {
          total: data.length,
          page: 1,
          size: data.length,
          pages: 1,
          has_next: false,
          has_prev: false,
          next_page: null,
          prev_page: null
        }
      };
    }
  });
};

export const useGetProductsQuery = useGetProducts;

export const useGetProduct = (id: string) => {
  return useQuery<Product>({
    queryKey: ['product', id],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/products/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useGetProductQuery = useGetProduct;

export const useCreateProduct = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (product: ProductCreate) => {
      const response = await apiClient.post('/api/v1/products', product);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useCreateProductMutation = useCreateProduct;

export const useUpdateProduct = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, product }: { id: string; product: ProductUpdate }) => {
      const response = await apiClient.patch(`/api/v1/products/${id}`, product);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['product', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useUpdateProductMutation = useUpdateProduct;

export const useDeleteProduct = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/products/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useDeleteProductMutation = useDeleteProduct;
