import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface CRMStoreState {
  // Active entity IDs
  activeClientId: string | null;
  activeInvoiceId: string | null;
  activeOpportunityId: string | null;
  activeTaskId: string | null;
  activeProductId: string | null;

  // Active view
  activeView: 'dashboard' | 'clients' | 'invoices' | 'opportunities' | 'tasks' | 'products' | 'reports';

  // Filters
  clientFilters: {
    status?: string;
    searchTerm?: string;
  };
  invoiceFilters: {
    status?: string;
    clientId?: string;
    searchTerm?: string;
  };
  opportunityFilters: {
    status?: string;
    clientId?: string;
    searchTerm?: string;
  };
  taskFilters: {
    status?: string;
    priority?: string;
    clientId?: string;
    assignedToMe?: boolean;
    searchTerm?: string;
  };
  productFilters: {
    status?: string;
    searchTerm?: string;
    categoryId?: string;
  };

  // Actions
  setActiveClientId: (id: string | null) => void;
  setActiveInvoiceId: (id: string | null) => void;
  setActiveOpportunityId: (id: string | null) => void;
  setActiveTaskId: (id: string | null) => void;
  setActiveView: (view: 'dashboard' | 'clients' | 'invoices' | 'opportunities' | 'tasks' | 'products' | 'reports') => void;
  setClientFilters: (filters: Partial<CRMStoreState['clientFilters']>) => void;
  setInvoiceFilters: (filters: Partial<CRMStoreState['invoiceFilters']>) => void;
  setOpportunityFilters: (filters: Partial<CRMStoreState['opportunityFilters']>) => void;
  setTaskFilters: (filters: Partial<CRMStoreState['taskFilters']>) => void;
  setProductFilters: (filters: Partial<CRMStoreState['productFilters']>) => void;
  setActiveProductId: (id: string | null) => void;
  resetFilters: () => void;
}

export const useCRMStore = create<CRMStoreState>()(
  persist(
    (set) => ({
      // Initial state
      activeClientId: null,
      activeInvoiceId: null,
      activeOpportunityId: null,
      activeTaskId: null,
      activeProductId: null,
      activeView: 'dashboard',
      clientFilters: {},
      invoiceFilters: {},
      opportunityFilters: {},
      taskFilters: {},
      productFilters: {},

      // Actions
      setActiveClientId: (id) => set({ activeClientId: id }),
      setActiveInvoiceId: (id) => set({ activeInvoiceId: id }),
      setActiveOpportunityId: (id) => set({ activeOpportunityId: id }),
      setActiveTaskId: (id) => set({ activeTaskId: id }),
      setActiveProductId: (id) => set({ activeProductId: id }),
      setActiveView: (view) => set({ activeView: view }),
      setClientFilters: (filters) => set((state) => ({
        clientFilters: { ...state.clientFilters, ...filters }
      })),
      setInvoiceFilters: (filters) => set((state) => ({
        invoiceFilters: { ...state.invoiceFilters, ...filters }
      })),
      setOpportunityFilters: (filters) => set((state) => ({
        opportunityFilters: { ...state.opportunityFilters, ...filters }
      })),
      setTaskFilters: (filters) => set((state) => ({
        taskFilters: { ...state.taskFilters, ...filters }
      })),
      setProductFilters: (filters) => set((state) => ({
        productFilters: { ...state.productFilters, ...filters }
      })),
      resetFilters: () => set({
        clientFilters: {},
        invoiceFilters: {},
        opportunityFilters: {},
        taskFilters: {},
        productFilters: {}
      }),
    }),
    {
      name: 'crm-store',
    }
  )
);
