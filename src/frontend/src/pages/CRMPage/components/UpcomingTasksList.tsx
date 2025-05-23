import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useGetTasksQuery } from "@/controllers/API/queries/crm";
import { Task } from "@/types/crm";
import { format } from "date-fns";

interface UpcomingTasksListProps {
  workspaceId: string | null;
}

export function UpcomingTasksList({ workspaceId }: UpcomingTasksListProps) {
  const { data: tasks, isLoading } = useGetTasksQuery(
    workspaceId
      ? {
          workspace_id: workspaceId,
          status: "open",
        }
      : undefined,
    {
      enabled: !!workspaceId,
    }
  );

  // Sort tasks by due date (closest first)
  const sortedTasks = tasks
    ? [...tasks]
        .filter((task) => task.due_date)
        .sort(
          (a, b) =>
            new Date(a.due_date!).getTime() - new Date(b.due_date!).getTime()
        )
        .slice(0, 5)
    : [];

  // Function to get priority badge color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "destructive";
      case "medium":
        return "warning";
      case "low":
        return "secondary";
      default:
        return "secondary";
    }
  };

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Upcoming Tasks</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="space-y-1">
                  <Skeleton className="h-4 w-[200px]" />
                  <Skeleton className="h-3 w-[150px]" />
                </div>
                <Skeleton className="h-5 w-16" />
              </div>
            ))}
          </div>
        ) : sortedTasks.length > 0 ? (
          <div className="space-y-4">
            {sortedTasks.map((task) => (
              <div key={task.id} className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium">{task.title}</p>
                  <p className="text-xs text-muted-foreground">
                    Due: {format(new Date(task.due_date!), "MMM d, yyyy")}
                  </p>
                </div>
                <Badge variant={getPriorityColor(task.priority)}>
                  {task.priority}
                </Badge>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-center text-sm text-muted-foreground">No upcoming tasks</p>
        )}
      </CardContent>
    </Card>
  );
}
