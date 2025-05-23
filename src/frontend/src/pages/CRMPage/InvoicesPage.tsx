import { useState } from "react";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { useGetInvoicesQuery, useCreateInvoiceMutation, useDeleteInvoiceMutation, useGetClientsQuery } from "@/controllers/API/queries/crm";
import { Invoice, InvoiceCreate, InvoiceStatus } from "@/types/crm";
import CRMSidebarComponent from "@/components/core/crmSidebarComponent";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import { MoreHorizontal, Plus, Search, Trash, Edit, Eye } from "lucide-react";
import { useCRMStore } from "@/stores/crmStore";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function InvoicesPage() {
  // Get current workspace ID
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);
  
  // Invoice filters from CRM store
  const { invoiceFilters, setInvoiceFilters } = useCRMStore((state) => ({
    invoiceFilters: state.invoiceFilters,
    setInvoiceFilters: state.setInvoiceFilters,
  }));
  
  // Local state
  const [searchTerm, setSearchTerm] = useState(invoiceFilters.searchTerm || "");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newInvoice, setNewInvoice] = useState<Partial<InvoiceCreate>>({
    invoice_number: "",
    amount: 0,
    status: "draft",
    description: "",
  });

  // Fetch invoices
  const { data: invoices, isLoading } = useGetInvoicesQuery(
    currentWorkspaceId
      ? {
          workspace_id: currentWorkspaceId,
          status: invoiceFilters.status,
          client_id: invoiceFilters.clientId,
        }
      : undefined,
    {
      enabled: !!currentWorkspaceId,
    }
  );

  // Fetch clients for the dropdown
  const { data: clients } = useGetClientsQuery(
    currentWorkspaceId
      ? {
          workspace_id: currentWorkspaceId,
        }
      : undefined,
    {
      enabled: !!currentWorkspaceId,
    }
  );

  // Mutations
  const { mutate: createInvoice } = useCreateInvoiceMutation();
  const { mutate: deleteInvoice } = useDeleteInvoiceMutation();

  // Filter invoices by search term
  const filteredInvoices = invoices
    ? invoices.filter((invoice) =>
        invoice.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (invoice.description && invoice.description.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : [];

  // Handle search
  const handleSearch = () => {
    setInvoiceFilters({ ...invoiceFilters, searchTerm });
  };

  // Handle create invoice
  const handleCreateInvoice = () => {
    if (!currentWorkspaceId || !newInvoice.invoice_number || !newInvoice.client_id) return;
    
    createInvoice({
      ...newInvoice as InvoiceCreate,
      workspace_id: currentWorkspaceId,
    });
    
    setIsCreateDialogOpen(false);
    setNewInvoice({
      invoice_number: "",
      amount: 0,
      status: "draft",
      description: "",
    });
  };

  // Handle delete invoice
  const handleDeleteInvoice = (id: string) => {
    deleteInvoice(id);
  };

  // Get status badge
  const getStatusBadge = (status: InvoiceStatus) => {
    switch (status) {
      case "paid":
        return <Badge className="bg-green-500">Paid</Badge>;
      case "sent":
        return <Badge className="bg-blue-500">Sent</Badge>;
      case "overdue":
        return <Badge className="bg-red-500">Overdue</Badge>;
      default:
        return <Badge variant="outline">Draft</Badge>;
    }
  };

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  return (
    <div className="flex h-full">
      <CRMSidebarComponent />
      <div className="flex-1 overflow-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Invoices</h1>
            <p className="text-muted-foreground">
              Manage your invoices and payments
            </p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Invoice
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Invoice</DialogTitle>
                <DialogDescription>
                  Create a new invoice in your CRM system.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="invoice_number">Invoice Number *</Label>
                  <Input
                    id="invoice_number"
                    value={newInvoice.invoice_number}
                    onChange={(e) => setNewInvoice({ ...newInvoice, invoice_number: e.target.value })}
                    placeholder="INV-001"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="client">Client *</Label>
                  <Select
                    value={newInvoice.client_id}
                    onValueChange={(value) => setNewInvoice({ ...newInvoice, client_id: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a client" />
                    </SelectTrigger>
                    <SelectContent>
                      {clients?.map((client) => (
                        <SelectItem key={client.id} value={client.id}>
                          {client.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="amount">Amount *</Label>
                  <Input
                    id="amount"
                    type="number"
                    value={newInvoice.amount?.toString() || ""}
                    onChange={(e) => setNewInvoice({ ...newInvoice, amount: parseFloat(e.target.value) })}
                    placeholder="0.00"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="status">Status</Label>
                  <Select
                    value={newInvoice.status}
                    onValueChange={(value) => setNewInvoice({ ...newInvoice, status: value as InvoiceStatus })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="sent">Sent</SelectItem>
                      <SelectItem value="paid">Paid</SelectItem>
                      <SelectItem value="overdue">Overdue</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={newInvoice.description || ""}
                    onChange={(e) => setNewInvoice({ ...newInvoice, description: e.target.value })}
                    placeholder="Invoice description"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateInvoice} disabled={!newInvoice.invoice_number || !newInvoice.client_id}>
                  Create
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <div className="mb-6 flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
          <div className="flex w-full max-w-sm items-center space-x-2">
            <Input
              placeholder="Search invoices..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
            <Button type="submit" size="icon" onClick={handleSearch}>
              <Search className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex space-x-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  {invoiceFilters.status ? `Status: ${invoiceFilters.status}` : "All Statuses"}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Filter by Status</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setInvoiceFilters({ ...invoiceFilters, status: undefined })}>
                  All Statuses
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setInvoiceFilters({ ...invoiceFilters, status: "draft" })}>
                  Draft
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setInvoiceFilters({ ...invoiceFilters, status: "sent" })}>
                  Sent
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setInvoiceFilters({ ...invoiceFilters, status: "paid" })}>
                  Paid
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setInvoiceFilters({ ...invoiceFilters, status: "overdue" })}>
                  Overdue
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  {invoiceFilters.clientId ? `Client: ${clients?.find(c => c.id === invoiceFilters.clientId)?.name || 'Selected'}` : "All Clients"}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Filter by Client</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setInvoiceFilters({ ...invoiceFilters, clientId: undefined })}>
                  All Clients
                </DropdownMenuItem>
                {clients?.map((client) => (
                  <DropdownMenuItem 
                    key={client.id}
                    onClick={() => setInvoiceFilters({ ...invoiceFilters, clientId: client.id })}
                  >
                    {client.name}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center justify-between rounded-md border p-4">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-[200px]" />
                  <Skeleton className="h-3 w-[150px]" />
                </div>
                <Skeleton className="h-8 w-[100px]" />
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice #</TableHead>
                  <TableHead>Client</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Issue Date</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead className="w-[80px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredInvoices.length > 0 ? (
                  filteredInvoices.map((invoice) => (
                    <TableRow key={invoice.id}>
                      <TableCell className="font-medium">{invoice.invoice_number}</TableCell>
                      <TableCell>{clients?.find(c => c.id === invoice.client_id)?.name || 'Unknown'}</TableCell>
                      <TableCell>{formatCurrency(invoice.amount)}</TableCell>
                      <TableCell>{getStatusBadge(invoice.status)}</TableCell>
                      <TableCell>{format(new Date(invoice.issue_date), "MMM d, yyyy")}</TableCell>
                      <TableCell>{invoice.due_date ? format(new Date(invoice.due_date), "MMM d, yyyy") : "-"}</TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                              <Eye className="mr-2 h-4 w-4" />
                              View
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleDeleteInvoice(invoice.id)}>
                              <Trash className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={7} className="h-24 text-center">
                      No invoices found.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
}
