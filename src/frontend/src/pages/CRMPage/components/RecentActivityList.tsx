import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { RecentActivityItem } from "@/types/crm";
import { formatDistanceToNow } from "date-fns";
import { CheckSquare, FileText, TrendingUp, User } from "lucide-react";

interface RecentActivityListProps {
  data?: RecentActivityItem[];
  isLoading: boolean;
}

export function RecentActivityList({ data, isLoading }: RecentActivityListProps) {
  // Function to get icon based on activity type
  const getActivityIcon = (type: string) => {
    switch (type) {
      case "client":
        return <User className="h-4 w-4" />;
      case "invoice":
        return <FileText className="h-4 w-4" />;
      case "opportunity":
        return <TrendingUp className="h-4 w-4" />;
      case "task":
        return <CheckSquare className="h-4 w-4" />;
      default:
        return null;
    }
  };

  // Function to get activity description
  const getActivityDescription = (item: RecentActivityItem) => {
    switch (item.type) {
      case "client":
        return `Client "${item.name}" was created`;
      case "invoice":
        return `Invoice #${item.invoice_number} was created`;
      case "opportunity":
        return `Opportunity "${item.name}" was created`;
      case "task":
        return `Task "${item.title}" was created`;
      default:
        return "Unknown activity";
    }
  };

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center gap-4">
                <Skeleton className="h-8 w-8 rounded-full" />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-[200px]" />
                  <Skeleton className="h-3 w-[150px]" />
                </div>
              </div>
            ))}
          </div>
        ) : data && data.length > 0 ? (
          <div className="space-y-4">
            {data.map((item) => (
              <div key={item.id} className="flex items-start gap-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                  {getActivityIcon(item.type)}
                </div>
                <div>
                  <p className="text-sm font-medium">{getActivityDescription(item)}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-center text-sm text-muted-foreground">No recent activity</p>
        )}
      </CardContent>
    </Card>
  );
}
