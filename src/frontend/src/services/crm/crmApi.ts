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
  RecentActivityItem,
  Product,
  ProductCreate,
  ProductUpdate,
  ProductCategory,
  ProductCategoryCreate,
  ProductCategoryUpdate,
  ProductAttribute,
  ProductAttributeCreate,
  ProductAttributeUpdate,
  ProductAttributeTerm,
  ProductAttributeTermCreate,
  ProductAttributeTermUpdate,
  ProductVariation,
  ProductVariationCreate,
  ProductVariationUpdate,
  ProductMeta,
  ProductMetaCreate,
  ProductMetaUpdate,
  ProductReview,
  ProductReviewCreate,
  ProductReviewUpdate
} from '../../types/crm';

export const crmApi = createApi({
  reducerPath: 'crmApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/v1/',
    credentials: 'include',
  }),
  tagTypes: ['Client', 'Invoice', 'Opportunity', 'Task', 'Dashboard', 'Product', 'ProductCategory', 'ProductAttribute', 'ProductVariation', 'ProductMeta', 'ProductReview'],
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

    // Product endpoints
    getProducts: builder.query<Product[], { workspace_id?: string, status?: string }>({
      query: (params) => ({
        url: 'products',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Product' as const, id })),
              { type: 'Product', id: 'LIST' },
            ]
          : [{ type: 'Product', id: 'LIST' }],
    }),
    getProduct: builder.query<Product, string>({
      query: (id) => `products/${id}`,
      providesTags: (_, __, id) => [{ type: 'Product', id }],
    }),
    createProduct: builder.mutation<Product, ProductCreate>({
      query: (product) => ({
        url: 'products',
        method: 'POST',
        body: product,
      }),
      invalidatesTags: [
        { type: 'Product', id: 'LIST' },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),
    updateProduct: builder.mutation<Product, { id: string; product: ProductUpdate }>({
      query: ({ id, product }) => ({
        url: `products/${id}`,
        method: 'PATCH',
        body: product,
      }),
      invalidatesTags: (_, __, { id }) => [
        { type: 'Product', id },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),
    deleteProduct: builder.mutation<void, string>({
      query: (id) => ({
        url: `products/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: [
        { type: 'Product', id: 'LIST' },
        { type: 'Dashboard', id: 'STATS' },
      ],
    }),

    // Product Category endpoints
    getProductCategories: builder.query<ProductCategory[], { workspace_id?: string, parent_id?: string }>({
      query: (params) => ({
        url: 'product-categories',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'ProductCategory' as const, id })),
              { type: 'ProductCategory', id: 'LIST' },
            ]
          : [{ type: 'ProductCategory', id: 'LIST' }],
    }),
    getProductCategory: builder.query<ProductCategory, string>({
      query: (id) => `product-categories/${id}`,
      providesTags: (_, __, id) => [{ type: 'ProductCategory', id }],
    }),
    createProductCategory: builder.mutation<ProductCategory, ProductCategoryCreate>({
      query: (category) => ({
        url: 'product-categories',
        method: 'POST',
        body: category,
      }),
      invalidatesTags: [{ type: 'ProductCategory', id: 'LIST' }],
    }),
    updateProductCategory: builder.mutation<ProductCategory, { id: string; category: ProductCategoryUpdate }>({
      query: ({ id, category }) => ({
        url: `product-categories/${id}`,
        method: 'PATCH',
        body: category,
      }),
      invalidatesTags: (_, __, { id }) => [{ type: 'ProductCategory', id }],
    }),
    deleteProductCategory: builder.mutation<void, string>({
      query: (id) => ({
        url: `product-categories/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: [{ type: 'ProductCategory', id: 'LIST' }],
    }),

    // Product Attribute endpoints
    getProductAttributes: builder.query<ProductAttribute[], { workspace_id?: string }>({
      query: (params) => ({
        url: 'product-attributes',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'ProductAttribute' as const, id })),
              { type: 'ProductAttribute', id: 'LIST' },
            ]
          : [{ type: 'ProductAttribute', id: 'LIST' }],
    }),
    getProductAttribute: builder.query<ProductAttribute, string>({
      query: (id) => `product-attributes/${id}`,
      providesTags: (_, __, id) => [{ type: 'ProductAttribute', id }],
    }),
    createProductAttribute: builder.mutation<ProductAttribute, ProductAttributeCreate>({
      query: (attribute) => ({
        url: 'product-attributes',
        method: 'POST',
        body: attribute,
      }),
      invalidatesTags: [{ type: 'ProductAttribute', id: 'LIST' }],
    }),
    updateProductAttribute: builder.mutation<ProductAttribute, { id: string; attribute: ProductAttributeUpdate }>({
      query: ({ id, attribute }) => ({
        url: `product-attributes/${id}`,
        method: 'PATCH',
        body: attribute,
      }),
      invalidatesTags: (_, __, { id }) => [{ type: 'ProductAttribute', id }],
    }),
    deleteProductAttribute: builder.mutation<void, string>({
      query: (id) => ({
        url: `product-attributes/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: [{ type: 'ProductAttribute', id: 'LIST' }],
    }),

    // Product Attribute Term endpoints
    getAttributeTerms: builder.query<ProductAttributeTerm[], { attribute_id: string }>({
      query: ({ attribute_id }) => `product-attributes/${attribute_id}/terms`,
      providesTags: (result, _, { attribute_id }) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'ProductAttribute' as const, id })),
              { type: 'ProductAttribute', id: attribute_id },
            ]
          : [{ type: 'ProductAttribute', id: attribute_id }],
    }),
    getAttributeTerm: builder.query<ProductAttributeTerm, { attribute_id: string, term_id: string }>({
      query: ({ attribute_id, term_id }) => `product-attributes/${attribute_id}/terms/${term_id}`,
      providesTags: (_, __, { attribute_id, term_id }) => [
        { type: 'ProductAttribute', id: attribute_id },
        { type: 'ProductAttribute', id: `term-${term_id}` },
      ],
    }),
    createAttributeTerm: builder.mutation<ProductAttributeTerm, { attribute_id: string, term: ProductAttributeTermCreate }>({
      query: ({ attribute_id, term }) => ({
        url: `product-attributes/${attribute_id}/terms`,
        method: 'POST',
        body: term,
      }),
      invalidatesTags: (_, __, { attribute_id }) => [{ type: 'ProductAttribute', id: attribute_id }],
    }),
    updateAttributeTerm: builder.mutation<ProductAttributeTerm, { attribute_id: string, term_id: string, term: ProductAttributeTermUpdate }>({
      query: ({ attribute_id, term_id, term }) => ({
        url: `product-attributes/${attribute_id}/terms/${term_id}`,
        method: 'PATCH',
        body: term,
      }),
      invalidatesTags: (_, __, { attribute_id, term_id }) => [
        { type: 'ProductAttribute', id: attribute_id },
        { type: 'ProductAttribute', id: `term-${term_id}` },
      ],
    }),
    deleteAttributeTerm: builder.mutation<void, { attribute_id: string, term_id: string }>({
      query: ({ attribute_id, term_id }) => ({
        url: `product-attributes/${attribute_id}/terms/${term_id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (_, __, { attribute_id }) => [{ type: 'ProductAttribute', id: attribute_id }],
    }),

    // Product Variation endpoints
    getProductVariations: builder.query<ProductVariation[], { product_id?: string }>({
      query: (params) => ({
        url: 'product-variations',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'ProductVariation' as const, id })),
              { type: 'ProductVariation', id: 'LIST' },
            ]
          : [{ type: 'ProductVariation', id: 'LIST' }],
    }),
    getProductVariation: builder.query<ProductVariation, string>({
      query: (id) => `product-variations/${id}`,
      providesTags: (_, __, id) => [{ type: 'ProductVariation', id }],
    }),
    createProductVariation: builder.mutation<ProductVariation, ProductVariationCreate>({
      query: (variation) => ({
        url: 'product-variations',
        method: 'POST',
        body: variation,
      }),
      invalidatesTags: [
        { type: 'ProductVariation', id: 'LIST' },
        { type: 'Product', id: 'LIST' },
      ],
    }),
    updateProductVariation: builder.mutation<ProductVariation, { id: string; variation: ProductVariationUpdate }>({
      query: ({ id, variation }) => ({
        url: `product-variations/${id}`,
        method: 'PATCH',
        body: variation,
      }),
      invalidatesTags: (_, __, { id }) => [{ type: 'ProductVariation', id }],
    }),
    deleteProductVariation: builder.mutation<void, string>({
      query: (id) => ({
        url: `product-variations/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: [
        { type: 'ProductVariation', id: 'LIST' },
        { type: 'Product', id: 'LIST' },
      ],
    }),

    // Product Meta endpoints
    getProductMeta: builder.query<ProductMeta[], { product_id: string }>({
      query: ({ product_id }) => ({
        url: 'product-meta',
        params: { product_id },
      }),
      providesTags: (result, _, { product_id }) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'ProductMeta' as const, id })),
              { type: 'ProductMeta', id: `product-${product_id}` },
            ]
          : [{ type: 'ProductMeta', id: `product-${product_id}` }],
    }),
    getProductMetaItem: builder.query<ProductMeta, string>({
      query: (id) => `product-meta/${id}`,
      providesTags: (_, __, id) => [{ type: 'ProductMeta', id }],
    }),
    createProductMeta: builder.mutation<ProductMeta, ProductMetaCreate>({
      query: (meta) => ({
        url: 'product-meta',
        method: 'POST',
        body: meta,
      }),
      invalidatesTags: (_, __, { product_id }) => [{ type: 'ProductMeta', id: `product-${product_id}` }],
    }),
    updateProductMeta: builder.mutation<ProductMeta, { id: string; meta: ProductMetaUpdate }>({
      query: ({ id, meta }) => ({
        url: `product-meta/${id}`,
        method: 'PATCH',
        body: meta,
      }),
      invalidatesTags: (_, __, { id }) => [{ type: 'ProductMeta', id }],
    }),
    deleteProductMeta: builder.mutation<void, string>({
      query: (id) => ({
        url: `product-meta/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (_, __, id) => [{ type: 'ProductMeta', id }],
    }),

    // Product Import/Export endpoints
    importProducts: builder.mutation<any, { workspace_id: string, file: File, format: 'csv' | 'json' }>({
      query: ({ workspace_id, file, format }) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('workspace_id', workspace_id);

        return {
          url: `product-import-export/import?format=${format}`,
          method: 'POST',
          body: formData,
        };
      },
      invalidatesTags: [{ type: 'Product', id: 'LIST' }],
    }),

    exportProducts: builder.query<Blob, { workspace_id?: string, format: 'csv' | 'json' }>({
      query: ({ workspace_id, format }) => ({
        url: `product-import-export/export`,
        params: { workspace_id, format },
        responseHandler: (response) => response.blob(),
      }),
    }),

    // Product Images endpoints
    uploadProductImage: builder.mutation<any, { product_id: string, image: File, is_primary?: boolean }>({
      query: ({ product_id, image, is_primary = false }) => {
        const formData = new FormData();
        formData.append('image', image);
        formData.append('is_primary', is_primary.toString());

        return {
          url: `product-images/${product_id}`,
          method: 'POST',
          body: formData,
        };
      },
      invalidatesTags: (_, __, { product_id }) => [
        { type: 'Product', id: product_id },
        { type: 'Product', id: 'LIST' },
      ],
    }),

    deleteProductImage: builder.mutation<any, { product_id: string, image_id: string }>({
      query: ({ product_id, image_id }) => ({
        url: `product-images/${product_id}/${image_id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (_, __, { product_id }) => [
        { type: 'Product', id: product_id },
        { type: 'Product', id: 'LIST' },
      ],
    }),

    reorderProductImages: builder.mutation<any, { product_id: string, image_ids: string[] }>({
      query: ({ product_id, image_ids }) => ({
        url: `product-images/${product_id}/reorder`,
        method: 'PUT',
        body: { image_ids },
      }),
      invalidatesTags: (_, __, { product_id }) => [
        { type: 'Product', id: product_id },
        { type: 'Product', id: 'LIST' },
      ],
    }),

    // Product Reviews endpoints
    getProductReviews: builder.query<ProductReview[], { product_id?: string, status?: string, page?: number, size?: number }>({
      query: (params) => ({
        url: 'product-reviews',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'ProductReview' as const, id })),
              { type: 'ProductReview', id: 'LIST' },
            ]
          : [{ type: 'ProductReview', id: 'LIST' }],
    }),

    getProductReview: builder.query<ProductReview, string>({
      query: (id) => `product-reviews/${id}`,
      providesTags: (_, __, id) => [{ type: 'ProductReview', id }],
    }),

    createProductReview: builder.mutation<ProductReview, ProductReviewCreate>({
      query: (review) => ({
        url: 'product-reviews',
        method: 'POST',
        body: review,
      }),
      invalidatesTags: [
        { type: 'ProductReview', id: 'LIST' },
        { type: 'Product', id: 'LIST' },
      ],
    }),

    updateProductReview: builder.mutation<ProductReview, { id: string; review: ProductReviewUpdate }>({
      query: ({ id, review }) => ({
        url: `product-reviews/${id}`,
        method: 'PATCH',
        body: review,
      }),
      invalidatesTags: (_, __, { id }) => [{ type: 'ProductReview', id }],
    }),

    deleteProductReview: builder.mutation<void, string>({
      query: (id) => ({
        url: `product-reviews/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: [
        { type: 'ProductReview', id: 'LIST' },
        { type: 'Product', id: 'LIST' },
      ],
    }),

    // E-commerce Integration endpoints
    importWooCommerceProducts: builder.mutation<any, { workspace_id: string, site_url: string, consumer_key: string, consumer_secret: string, limit?: number }>({
      query: (data) => ({
        url: 'ecommerce-integration/import-woocommerce',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: [{ type: 'Product', id: 'LIST' }],
    }),

    importShopifyProducts: builder.mutation<any, { workspace_id: string, shop_url: string, access_token: string, limit?: number }>({
      query: (data) => ({
        url: 'ecommerce-integration/import-shopify',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: [{ type: 'Product', id: 'LIST' }],
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
