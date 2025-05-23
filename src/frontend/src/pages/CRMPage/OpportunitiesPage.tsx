import { useState } from "react";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { useGetOpportunitiesQuery, useCreateOpportunityMutation, useDeleteOpportunityMutation, useGetClientsQuery } from "@/controllers/API/queries/crm";
import { Opportunity, OpportunityCreate, OpportunityStatus } from "@/types/crm";
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

export default function OpportunitiesPage() {
  // Get current workspace ID
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);
  
  // Opportunity filters from CRM store
  const { opportunityFilters, setOpportunityFilters } = useCRMStore((state) => ({
    opportunityFilters: state.opportunityFilters,
    setOpportunityFilters: state.setOpportunityFilters,
  }));
  
  // Local state
  const [searchTerm, setSearchTerm] = useState(opportunityFilters.searchTerm || "");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newOpportunity, setNewOpportunity] = useState<Partial<OpportunityCreate>>({
    name: "",
    value: 0,
    status: "new",
    description: "",
  });

  // Fetch opportunities
  const { data: opportunities, isLoading } = useGetOpportunitiesQuery(
    currentWorkspaceId
      ? {
          workspace_id: currentWorkspaceId,
          status: opportunityFilters.status,
          client_id: opportunityFilters.clientId,
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
  const { mutate: createOpportunity } = useCreateOpportunityMutation();
  const { mutate: deleteOpportunity } = useDeleteOpportunityMutation();

  // Filter opportunities by search term
  const filteredOpportunities = opportunities
    ? opportunities.filter((opportunity) =>
        opportunity.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (opportunity.description && opportunity.description.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : [];

  // Handle search
  const handleSearch = () => {
    setOpportunityFilters({ ...opportunityFilters, searchTerm });
  };

  // Handle create opportunity
  const handleCreateOpportunity = () => {
    if (!currentWorkspaceId || !newOpportunity.name || !newOpportunity.client_id) return;
    
    createOpportunity({
      ...newOpportunity as OpportunityCreate,
      workspace_id: currentWorkspaceId,
    });
    
    setIsCreateDialogOpen(false);
    setNewOpportunity({
      name: "",
      value: 0,
      status: "new",
      description: "",
    });
  };

  // Handle delete opportunity
  const handleDeleteOpportunity = (id: string) => {
    deleteOpportunity(id);
  };

  // Get status badge
  const getStatusBadge = (status: OpportunityStatus) => {
    switch (status) {
      case "new":
        return <Badge variant="outline">New</Badge>;
      case "qualified":
        return <Badge className="bg-blue-500">Qualified</Badge>;
      case "proposal":
        return <Badge className="bg-purple-500">Proposal</Badge>;
      case "negotiation":
        return <Badge className="bg-orange-500">Negotiation</Badge>;
      case "won":
        return <Badge className="bg-green-500">Won</Badge>;
      case "lost":
        return <Badge className="bg-red-500">Lost</Badge>;
      default:
        return <Badge variant="outline">New</Badge>;
    }
  };

  // Format currency
  const formatCurrency = (value: number | undefined) => {
    if (value === undefined) return "-";
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
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Opportunities</h1>
            <p className="text-muted-foreground">
              Manage your sales opportunities
            </p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Opportunity
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Opportunity</DialogTitle>
                <DialogDescription>
                  Create a new sales opportunity in your CRM system.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="name">Name *</Label>
                  <Input
                    id="name"
                    value={newOpportunity.name}
                    onChange={(e) => setNewOpportunity({ ...newOpportunity, name: e.target.value })}
                    placeholder="New product sale"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="client">Client *</Label>
                  <Select
                    value={newOpportunity.client_id}
                    onValueChange={(value) => setNewOpportunity({ ...newOpportunity, client_id: value })}
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
                  <Label htmlFor="value">Value</Label>
                  <Input
                    id="value"
                    type="number"
                    value={newOpportunity.value?.toString() || ""}
                    onChange={(e) => setNewOpportunity({ ...newOpportunity, value: parseFloat(e.target.value) })}
                    placeholder="0"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="status">Status</Label>
                  <Select
                    value={newOpportunity.status}
                    onValueChange={(value) => setNewOpportunity({ ...newOpportunity, status: value as OpportunityStatus })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="new">New</SelectItem>
                      <SelectItem value="qualified">Qualified</SelectItem>
                      <SelectItem value="proposal">Proposal</SelectItem>
                      <SelectItem value="negotiation">Negotiation</SelectItem>
                      <SelectItem value="won">Won</SelectItem>
                      <SelectItem value="lost">Lost</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={newOpportunity.description || ""}
                    onChange={(e) => setNewOpportunity({ ...newOpportunity, description: e.target.value })}
                    placeholder="Opportunity description"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateOpportunity} disabled={!newOpportunity.name || !newOpportunity.client_id}>
                  Create
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <div className="mb-6 flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
          <div className="flex w-full max-w-sm items-center space-x-2">
            <Input
              placeholder="Search opportunities..."
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
                  {opportunityFilters.status ? `Status: ${opportunityFilters.status}` : "All Statuses"}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Filter by Status</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setOpportunityFilters({ ...opportunityFilters, status: undefined })}>
                  All Statuses
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setOpportunityFilters({ ...opportunityFilters, status: "new" })}>
                  New
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setOpportunityFilters({ ...opportunityFilters, status: "qualified" })}>
                  Qualified
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setOpportunityFilters({ ...opportunityFilters, status: "proposal" })}>
                  Proposal
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setOpportunityFilters({ ...opportunityFilters, status: "negotiation" })}>
                  Negotiation
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setOpportunityFilters({ ...opportunityFilters, status: "won" })}>
                  Won
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setOpportunityFilters({ ...opportunityFilters, status: "lost" })}>
                  Lost
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  {opportunityFilters.clientId ? `Client: ${clients?.find(c => c.id === opportunityFilters.clientId)?.name || 'Selected'}` : "All Clients"}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Filter by Client</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setOpportunityFilters({ ...opportunityFilters, clientId: undefined })}>
                  All Clients
                </DropdownMenuItem>
                {clients?.map((client) => (
                  <DropdownMenuItem 
                    key={client.id}
                    onClick={() => setOpportunityFilters({ ...opportunityFilters, clientId: client.id })}
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
                  <TableHead>Name</TableHead>
                  <TableHead>Client</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Expected Close</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="w-[80px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredOpportunities.length > 0 ? (
                  filteredOpportunities.map((opportunity) => (
                    <TableRow key={opportunity.id}>
                      <TableCell className="font-medium">{opportunity.name}</TableCell>
                      <TableCell>{clients?.find(c => c.id === opportunity.client_id)?.name || 'Unknown'}</TableCell>
                      <TableCell>{formatCurrency(opportunity.value)}</TableCell>
                      <TableCell>{getStatusBadge(opportunity.status)}</TableCell>
                      <TableCell>{opportunity.expected_close_date ? format(new Date(opportunity.expected_close_date), "MMM d, yyyy") : "-"}</TableCell>
                      <TableCell>{format(new Date(opportunity.created_at), "MMM d, yyyy")}</TableCell>
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
                            <DropdownMenuItem onClick={() => handleDeleteOpportunity(opportunity.id)}>
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
                      No opportunities found.
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
