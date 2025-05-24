// CRM Entity Types
export type ClientStatus = 'active' | 'inactive' | 'lead';
export type InvoiceStatus = 'draft' | 'sent' | 'paid' | 'overdue';
export type OpportunityStatus = 'new' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost';
export type TaskStatus = 'open' | 'in_progress' | 'completed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high';
export type ProductStatus = 'publish' | 'draft' | 'pending' | 'private';
export type ProductStockStatus = 'instock' | 'outofstock' | 'onbackorder';
export type ProductBackorderStatus = 'no' | 'notify' | 'yes';
export type ProductCatalogVisibility = 'visible' | 'catalog' | 'search' | 'hidden';
export type ProductTaxStatus = 'taxable' | 'shipping' | 'none';

// Import product types
export * from './product';

// Base Client interface
export interface Client {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  description?: string;
  status: ClientStatus;
  workspace_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

// Base Invoice interface
export interface Invoice {
  id: string;
  invoice_number: string;
  amount: number;
  status: InvoiceStatus;
  issue_date: string;
  due_date?: string;
  description?: string;
  workspace_id: string;
  client_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

// Base Opportunity interface
export interface Opportunity {
  id: string;
  name: string;
  value?: number;
  status: OpportunityStatus;
  description?: string;
  expected_close_date?: string;
  workspace_id: string;
  client_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

// Base Task interface
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string;
  workspace_id: string;
  created_by: string;
  assigned_to?: string;
  client_id?: string;
  invoice_id?: string;
  opportunity_id?: string;
  created_at: string;
  updated_at: string;
}

// Dashboard Statistics
export interface DashboardStats {
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

// Client Distribution
export interface ClientDistribution {
  active: number;
  inactive: number;
  lead: number;
}

// Recent Activity Item
export interface RecentActivityItem {
  type: 'client' | 'invoice' | 'opportunity' | 'task';
  id: string;
  created_at: string;
  created_by: string;
  [key: string]: any; // Additional properties based on type
}

// Create/Update Types
export type ClientCreate = Omit<Client, 'id' | 'created_by' | 'created_at' | 'updated_at'>;
export type ClientUpdate = Partial<Omit<Client, 'id' | 'workspace_id' | 'created_by' | 'created_at' | 'updated_at'>>;

export type InvoiceCreate = Omit<Invoice, 'id' | 'created_by' | 'created_at' | 'updated_at'>;
export type InvoiceUpdate = Partial<Omit<Invoice, 'id' | 'workspace_id' | 'client_id' | 'created_by' | 'created_at' | 'updated_at'>>;

export type OpportunityCreate = Omit<Opportunity, 'id' | 'created_by' | 'created_at' | 'updated_at'>;
export type OpportunityUpdate = Partial<Omit<Opportunity, 'id' | 'workspace_id' | 'client_id' | 'created_by' | 'created_at' | 'updated_at'>>;

export type TaskCreate = Omit<Task, 'id' | 'created_by' | 'created_at' | 'updated_at'>;
export type TaskUpdate = Partial<Omit<Task, 'id' | 'workspace_id' | 'created_by' | 'created_at' | 'updated_at'>>;
