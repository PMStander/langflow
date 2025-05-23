import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
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
} from '../../types/crm';

export const crmApi = createApi({
  reducerPath: 'crmApi',
  baseQuery: fetchBaseQuery({ 
    baseUrl: '/api/v1/',
    credentials: 'include',
  }),
  tagTypes: ['Client', 'Invoice', 'Opportunity', 'Task', 'Dashboard'],
  endpoints: (builder) => ({
    // Client endpoints
    getClients: builder.query<Client[], { workspace_id?: string, status?: string }>({
      query: (params) => ({
        url: 'clients',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Client' as const, id })),
              { type: 'Client', id: 'LIST' },
            ]
          : [{ type: 'Client', id: 'LIST' }],
    }),
    getClient: builder.query<Client, string>({
      query: (id) => `clients/${id}`,
      providesTags: (_, __, id) => [{ type: 'Client', id }],
    }),
    createClient: builder.mutation<Client, ClientCreate>({
      query: (client) => ({
        url: 'clients',
        method: 'POST',
        body: client,
      }),
      invalidatesTags: [{ type: 'Client', id: 'LIST' }, { type: 'Dashboard', id: 'STATS' }],
    }),
    updateClient: builder.mutation<Client, { id: string; client: ClientUpdate }>({
      query: ({ id, client }) => ({
        url: `clients/${id}`,
        method: 'PATCH',
        body: client,
      }),
      invalidatesTags: (_, __, { id }) => [
        { type: 'Client', id },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),
    deleteClient: builder.mutation<void, string>({
      query: (id) => ({
        url: `clients/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: [
        { type: 'Client', id: 'LIST' },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),

    // Invoice endpoints
    getInvoices: builder.query<Invoice[], { workspace_id?: string, client_id?: string, status?: string }>({
      query: (params) => ({
        url: 'invoices',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Invoice' as const, id })),
              { type: 'Invoice', id: 'LIST' },
            ]
          : [{ type: 'Invoice', id: 'LIST' }],
    }),
    getInvoice: builder.query<Invoice, string>({
      query: (id) => `invoices/${id}`,
      providesTags: (_, __, id) => [{ type: 'Invoice', id }],
    }),
    createInvoice: builder.mutation<Invoice, InvoiceCreate>({
      query: (invoice) => ({
        url: 'invoices',
        method: 'POST',
        body: invoice,
      }),
      invalidatesTags: [
        { type: 'Invoice', id: 'LIST' },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),
    updateInvoice: builder.mutation<Invoice, { id: string; invoice: InvoiceUpdate }>({
      query: ({ id, invoice }) => ({
        url: `invoices/${id}`,
        method: 'PATCH',
        body: invoice,
      }),
      invalidatesTags: (_, __, { id }) => [
        { type: 'Invoice', id },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),
    deleteInvoice: builder.mutation<void, string>({
      query: (id) => ({
        url: `invoices/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: [
        { type: 'Invoice', id: 'LIST' },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),

    // Opportunity endpoints
    getOpportunities: builder.query<Opportunity[], { workspace_id?: string, client_id?: string, status?: string }>({
      query: (params) => ({
        url: 'opportunities',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Opportunity' as const, id })),
              { type: 'Opportunity', id: 'LIST' },
            ]
          : [{ type: 'Opportunity', id: 'LIST' }],
    }),
    getOpportunity: builder.query<Opportunity, string>({
      query: (id) => `opportunities/${id}`,
      providesTags: (_, __, id) => [{ type: 'Opportunity', id }],
    }),
    createOpportunity: builder.mutation<Opportunity, OpportunityCreate>({
      query: (opportunity) => ({
        url: 'opportunities',
        method: 'POST',
        body: opportunity,
      }),
      invalidatesTags: [
        { type: 'Opportunity', id: 'LIST' },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),
    updateOpportunity: builder.mutation<Opportunity, { id: string; opportunity: OpportunityUpdate }>({
      query: ({ id, opportunity }) => ({
        url: `opportunities/${id}`,
        method: 'PATCH',
        body: opportunity,
      }),
      invalidatesTags: (_, __, { id }) => [
        { type: 'Opportunity', id },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),
    deleteOpportunity: builder.mutation<void, string>({
      query: (id) => ({
        url: `opportunities/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: [
        { type: 'Opportunity', id: 'LIST' },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),

    // Task endpoints
    getTasks: builder.query<Task[], { 
      workspace_id?: string, 
      client_id?: string, 
      invoice_id?: string,
      opportunity_id?: string,
      assigned_to?: string,
      status?: string,
      priority?: string
    }>({
      query: (params) => ({
        url: 'tasks',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Task' as const, id })),
              { type: 'Task', id: 'LIST' },
            ]
          : [{ type: 'Task', id: 'LIST' }],
    }),
    getTask: builder.query<Task, string>({
      query: (id) => `tasks/${id}`,
      providesTags: (_, __, id) => [{ type: 'Task', id }],
    }),
    createTask: builder.mutation<Task, TaskCreate>({
      query: (task) => ({
        url: 'tasks',
        method: 'POST',
        body: task,
      }),
      invalidatesTags: [
        { type: 'Task', id: 'LIST' },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),
    updateTask: builder.mutation<Task, { id: string; task: TaskUpdate }>({
      query: ({ id, task }) => ({
        url: `tasks/${id}`,
        method: 'PATCH',
        body: task,
      }),
      invalidatesTags: (_, __, { id }) => [
        { type: 'Task', id },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),
    deleteTask: builder.mutation<void, string>({
      query: (id) => ({
        url: `tasks/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: [
        { type: 'Task', id: 'LIST' },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),

    // Dashboard endpoints
    getWorkspaceStats: builder.query<DashboardStats, string>({
      query: (workspaceId) => `dashboard/workspace/${workspaceId}/stats`,
      providesTags: [{ type: 'Dashboard', id: 'STATS' }],
    }),
    getClientDistribution: builder.query<ClientDistribution, string>({
      query: (workspaceId) => `dashboard/workspace/${workspaceId}/client-distribution`,
      providesTags: [{ type: 'Dashboard', id: 'CLIENT_DISTRIBUTION' }],
    }),
    getRecentActivity: builder.query<RecentActivityItem[], { workspaceId: string, limit?: number }>({
      query: ({ workspaceId, limit = 10 }) => ({
        url: `dashboard/workspace/${workspaceId}/recent-activity`,
        params: { limit },
      }),
      providesTags: [{ type: 'Dashboard', id: 'RECENT_ACTIVITY' }],
    }),
  }),
});

export const {
  // Client hooks
  useGetClientsQuery,
  useGetClientQuery,
  useCreateClientMutation,
  useUpdateClientMutation,
  useDeleteClientMutation,
  
  // Invoice hooks
  useGetInvoicesQuery,
  useGetInvoiceQuery,
  useCreateInvoiceMutation,
  useUpdateInvoiceMutation,
  useDeleteInvoiceMutation,
  
  // Opportunity hooks
  useGetOpportunitiesQuery,
  useGetOpportunityQuery,
  useCreateOpportunityMutation,
  useUpdateOpportunityMutation,
  useDeleteOpportunityMutation,
  
  // Task hooks
  useGetTasksQuery,
  useGetTaskQuery,
  useCreateTaskMutation,
  useUpdateTaskMutation,
  useDeleteTaskMutation,
  
  // Dashboard hooks
  useGetWorkspaceStatsQuery,
  useGetClientDistributionQuery,
  useGetRecentActivityQuery,
} = crmApi;
