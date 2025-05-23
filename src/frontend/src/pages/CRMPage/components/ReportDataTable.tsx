import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { format } from "date-fns";

interface ReportDataTableProps {
  reportType: string;
  data: any;
}

export function ReportDataTable({ reportType, data }: ReportDataTableProps) {
  // Format currency
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(value);
  };

  // Format percentage
  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  // Get table data based on report type
  const getTableData = () => {
    if (reportType === "sales_overview") {
      return [
        {
          metric: "Total Revenue",
          value: formatCurrency(data.metrics?.total_revenue || 0),
        },
        {
          metric: "Total Invoices",
          value: data.metrics?.total_invoices || 0,
        },
        {
          metric: "Average Deal Size",
          value: formatCurrency(data.metrics?.average_deal_size || 0),
        },
        {
          metric: "Win Rate",
          value: formatPercentage(data.metrics?.win_rate || 0),
        },
        {
          metric: "Draft Invoices",
          value: data.metrics?.invoices_by_status?.draft || 0,
        },
        {
          metric: "Sent Invoices",
          value: data.metrics?.invoices_by_status?.sent || 0,
        },
        {
          metric: "Paid Invoices",
          value: data.metrics?.invoices_by_status?.paid || 0,
        },
        {
          metric: "Overdue Invoices",
          value: data.metrics?.invoices_by_status?.overdue || 0,
        },
      ];
    } else if (reportType === "opportunity_pipeline") {
      return [
        {
          metric: "Total Opportunities",
          value: data.metrics?.total_opportunities || 0,
        },
        {
          metric: "Open Opportunity Value",
          value: formatCurrency(data.metrics?.open_value || 0),
        },
        {
          metric: "New Opportunities",
          value: data.metrics?.opportunities_by_status?.new || 0,
        },
        {
          metric: "Qualified Opportunities",
          value: data.metrics?.opportunities_by_status?.qualified || 0,
        },
        {
          metric: "Proposal Stage",
          value: data.metrics?.opportunities_by_status?.proposal || 0,
        },
        {
          metric: "Negotiation Stage",
          value: data.metrics?.opportunities_by_status?.negotiation || 0,
        },
        {
          metric: "Won Opportunities",
          value: data.metrics?.opportunities_by_status?.won || 0,
        },
        {
          metric: "Lost Opportunities",
          value: data.metrics?.opportunities_by_status?.lost || 0,
        },
      ];
    } else if (reportType === "client_activity") {
      // This would be implemented based on the actual data structure
      return [
        { metric: "Total Clients", value: data.metrics?.clients?.total || 0 },
        { metric: "Active Clients", value: data.metrics?.clients?.active || 0 },
        { metric: "New Clients (Period)", value: data.metrics?.new_clients || 0 },
        { metric: "Client Conversion Rate", value: formatPercentage(data.metrics?.conversion_rate || 0) },
      ];
    } else if (reportType === "invoice_aging") {
      // This would be implemented based on the actual data structure
      return [
        { metric: "Current Invoices", value: formatCurrency(10000) },
        { metric: "1-30 Days Overdue", value: formatCurrency(5000) },
        { metric: "31-60 Days Overdue", value: formatCurrency(3000) },
        { metric: "61-90 Days Overdue", value: formatCurrency(2000) },
        { metric: "90+ Days Overdue", value: formatCurrency(1000) },
        { metric: "Total Outstanding", value: formatCurrency(21000) },
      ];
    } else if (reportType === "task_completion") {
      // This would be implemented based on the actual data structure
      return [
        { metric: "Open Tasks", value: data.metrics?.tasks?.open || 0 },
        { metric: "In Progress Tasks", value: data.metrics?.tasks?.in_progress || 0 },
        { metric: "Completed Tasks", value: data.metrics?.tasks?.completed || 0 },
        { metric: "Completion Rate", value: formatPercentage(60) },
        { metric: "Average Completion Time", value: "3.2 days" },
      ];
    } else if (reportType === "revenue_forecast") {
      // This would be implemented based on the actual data structure
      return [
        { metric: "Projected Revenue (Next 30 Days)", value: formatCurrency(25000) },
        { metric: "Projected Revenue (Next 90 Days)", value: formatCurrency(75000) },
        { metric: "Projected Revenue (Next 12 Months)", value: formatCurrency(300000) },
        { metric: "Growth Rate (YoY)", value: formatPercentage(15) },
        { metric: "Forecast Accuracy", value: formatPercentage(85) },
      ];
    }

    // Default empty data
    return [];
  };

  const tableData = getTableData();

  // Get table title based on report type
  const getTableTitle = () => {
    switch (reportType) {
      case "sales_overview":
        return "Sales Metrics";
      case "client_activity":
        return "Client Metrics";
      case "opportunity_pipeline":
        return "Opportunity Metrics";
      case "invoice_aging":
        return "Invoice Aging Metrics";
      case "task_completion":
        return "Task Metrics";
      case "revenue_forecast":
        return "Revenue Forecast Metrics";
      default:
        return "Report Metrics";
    }
  };

  return (
    <div>
      <h3 className="mb-4 text-lg font-medium">{getTableTitle()}</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Metric</TableHead>
            <TableHead className="text-right">Value</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tableData.map((row, index) => (
            <TableRow key={index}>
              <TableCell className="font-medium">{row.metric}</TableCell>
              <TableCell className="text-right">{row.value}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      
      <div className="mt-4 text-xs text-muted-foreground">
        <p>Report generated on {format(new Date(), 'MMM d, yyyy, h:mm a')}</p>
        <p>Time period: {data.time_period?.start_date ? format(new Date(data.time_period.start_date), 'MMM d, yyyy') : ''} to {data.time_period?.end_date ? format(new Date(data.time_period.end_date), 'MMM d, yyyy') : ''}</p>
      </div>
    </div>
  );
}
