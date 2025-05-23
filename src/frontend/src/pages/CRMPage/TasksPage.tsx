import { useState } from "react";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { 
  useGetTasksQuery, 
  useCreateTaskMutation, 
  useDeleteTaskMutation, 
  useGetClientsQuery,
  useGetInvoicesQuery,
  useGetOpportunitiesQuery
} from "@/controllers/API/queries/crm";
import { Task, TaskCreate, TaskStatus, TaskPriority } from "@/types/crm";
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
import { MoreHorizontal, Plus, Search, Trash, Edit, Eye, Calendar } from "lucide-react";
import { useCRMStore } from "@/stores/crmStore";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function TasksPage() {
  // Get current workspace ID
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);
  
  // Task filters from CRM store
  const { taskFilters, setTaskFilters } = useCRMStore((state) => ({
    taskFilters: state.taskFilters,
    setTaskFilters: state.setTaskFilters,
  }));
  
  // Local state
  const [searchTerm, setSearchTerm] = useState(taskFilters.searchTerm || "");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newTask, setNewTask] = useState<Partial<TaskCreate>>({
    title: "",
    description: "",
    status: "open",
    priority: "medium",
  });

  // Fetch tasks
  const { data: tasks, isLoading } = useGetTasksQuery(
    currentWorkspaceId
      ? {
          workspace_id: currentWorkspaceId,
          status: taskFilters.status,
          priority: taskFilters.priority,
          client_id: taskFilters.clientId,
          invoice_id: taskFilters.invoiceId,
          opportunity_id: taskFilters.opportunityId,
        }
      : undefined,
    {
      enabled: !!currentWorkspaceId,
    }
  );

  // Fetch related entities for dropdowns
  const { data: clients } = useGetClientsQuery(
    currentWorkspaceId ? { workspace_id: currentWorkspaceId } : undefined,
    { enabled: !!currentWorkspaceId }
  );
  
  const { data: invoices } = useGetInvoicesQuery(
    currentWorkspaceId ? { workspace_id: currentWorkspaceId } : undefined,
    { enabled: !!currentWorkspaceId }
  );
  
  const { data: opportunities } = useGetOpportunitiesQuery(
    currentWorkspaceId ? { workspace_id: currentWorkspaceId } : undefined,
    { enabled: !!currentWorkspaceId }
  );

  // Mutations
  const { mutate: createTask } = useCreateTaskMutation();
  const { mutate: deleteTask } = useDeleteTaskMutation();

  // Filter tasks by search term
  const filteredTasks = tasks
    ? tasks.filter((task) =>
        task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (task.description && task.description.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : [];

  // Handle search
  const handleSearch = () => {
    setTaskFilters({ ...taskFilters, searchTerm });
  };

  // Handle create task
  const handleCreateTask = () => {
    if (!currentWorkspaceId || !newTask.title) return;
    
    createTask({
      ...newTask as TaskCreate,
      workspace_id: currentWorkspaceId,
    });
    
    setIsCreateDialogOpen(false);
    setNewTask({
      title: "",
      description: "",
      status: "open",
      priority: "medium",
    });
  };

  // Handle delete task
  const handleDeleteTask = (id: string) => {
    deleteTask(id);
  };

  // Get status badge
  const getStatusBadge = (status: TaskStatus) => {
    switch (status) {
      case "open":
        return <Badge variant="outline">Open</Badge>;
      case "in_progress":
        return <Badge className="bg-blue-500">In Progress</Badge>;
      case "completed":
        return <Badge className="bg-green-500">Completed</Badge>;
      case "cancelled":
        return <Badge className="bg-red-500">Cancelled</Badge>;
      default:
        return <Badge variant="outline">Open</Badge>;
    }
  };

  // Get priority badge
  const getPriorityBadge = (priority: TaskPriority) => {
    switch (priority) {
      case "high":
        return <Badge className="bg-red-500">High</Badge>;
      case "medium":
        return <Badge className="bg-yellow-500">Medium</Badge>;
      case "low":
        return <Badge className="bg-green-500">Low</Badge>;
      default:
        return <Badge className="bg-yellow-500">Medium</Badge>;
    }
  };

  return (
    <div className="flex h-full">
      <CRMSidebarComponent />
      <div className="flex-1 overflow-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Tasks</h1>
            <p className="text-muted-foreground">
              Manage your tasks and activities
            </p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Task
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Task</DialogTitle>
                <DialogDescription>
                  Create a new task in your CRM system.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="title">Title *</Label>
                  <Input
                    id="title"
                    value={newTask.title}
                    onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                    placeholder="Task title"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={newTask.description || ""}
                    onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                    placeholder="Task description"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="status">Status</Label>
                  <Select
                    value={newTask.status}
                    onValueChange={(value) => setNewTask({ ...newTask, status: value as TaskStatus })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="open">Open</SelectItem>
                      <SelectItem value="in_progress">In Progress</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="cancelled">Cancelled</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="priority">Priority</Label>
                  <Select
                    value={newTask.priority}
                    onValueChange={(value) => setNewTask({ ...newTask, priority: value as TaskPriority })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="due_date">Due Date</Label>
                  <div className="flex items-center">
                    <Input
                      id="due_date"
                      type="date"
                      value={newTask.due_date ? new Date(newTask.due_date).toISOString().split('T')[0] : ""}
                      onChange={(e) => setNewTask({ ...newTask, due_date: e.target.value ? new Date(e.target.value) : undefined })}
                    />
                    <Calendar className="ml-2 h-4 w-4 text-muted-foreground" />
                  </div>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="client">Related Client</Label>
                  <Select
                    value={newTask.client_id}
                    onValueChange={(value) => setNewTask({ ...newTask, client_id: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a client" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">None</SelectItem>
                      {clients?.map((client) => (
                        <SelectItem key={client.id} value={client.id}>
                          {client.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="invoice">Related Invoice</Label>
                  <Select
                    value={newTask.invoice_id}
                    onValueChange={(value) => setNewTask({ ...newTask, invoice_id: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select an invoice" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">None</SelectItem>
                      {invoices?.map((invoice) => (
                        <SelectItem key={invoice.id} value={invoice.id}>
                          {invoice.invoice_number}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="opportunity">Related Opportunity</Label>
                  <Select
                    value={newTask.opportunity_id}
                    onValueChange={(value) => setNewTask({ ...newTask, opportunity_id: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select an opportunity" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">None</SelectItem>
                      {opportunities?.map((opportunity) => (
                        <SelectItem key={opportunity.id} value={opportunity.id}>
                          {opportunity.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateTask} disabled={!newTask.title}>
                  Create
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <div className="mb-6 flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
          <div className="flex w-full max-w-sm items-center space-x-2">
            <Input
              placeholder="Search tasks..."
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
                  {taskFilters.status ? `Status: ${taskFilters.status}` : "All Statuses"}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Filter by Status</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setTaskFilters({ ...taskFilters, status: undefined })}>
                  All Statuses
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTaskFilters({ ...taskFilters, status: "open" })}>
                  Open
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTaskFilters({ ...taskFilters, status: "in_progress" })}>
                  In Progress
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTaskFilters({ ...taskFilters, status: "completed" })}>
                  Completed
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTaskFilters({ ...taskFilters, status: "cancelled" })}>
                  Cancelled
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  {taskFilters.priority ? `Priority: ${taskFilters.priority}` : "All Priorities"}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Filter by Priority</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setTaskFilters({ ...taskFilters, priority: undefined })}>
                  All Priorities
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTaskFilters({ ...taskFilters, priority: "high" })}>
                  High
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTaskFilters({ ...taskFilters, priority: "medium" })}>
                  Medium
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTaskFilters({ ...taskFilters, priority: "low" })}>
                  Low
                </DropdownMenuItem>
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
                  <TableHead>Title</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Related To</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="w-[80px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTasks.length > 0 ? (
                  filteredTasks.map((task) => (
                    <TableRow key={task.id}>
                      <TableCell className="font-medium">{task.title}</TableCell>
                      <TableCell>{getStatusBadge(task.status)}</TableCell>
                      <TableCell>{getPriorityBadge(task.priority)}</TableCell>
                      <TableCell>{task.due_date ? format(new Date(task.due_date), "MMM d, yyyy") : "-"}</TableCell>
                      <TableCell>
                        {task.client_id ? (
                          <span className="text-sm">
                            Client: {clients?.find(c => c.id === task.client_id)?.name || 'Unknown'}
                          </span>
                        ) : task.invoice_id ? (
                          <span className="text-sm">
                            Invoice: {invoices?.find(i => i.id === task.invoice_id)?.invoice_number || 'Unknown'}
                          </span>
                        ) : task.opportunity_id ? (
                          <span className="text-sm">
                            Opportunity: {opportunities?.find(o => o.id === task.opportunity_id)?.name || 'Unknown'}
                          </span>
                        ) : (
                          "-"
                        )}
                      </TableCell>
                      <TableCell>{format(new Date(task.created_at), "MMM d, yyyy")}</TableCell>
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
                            <DropdownMenuItem onClick={() => handleDeleteTask(task.id)}>
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
                      No tasks found.
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
