import { useState } from "react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart2, PieChart as PieChartIcon, LineChart as LineChartIcon } from "lucide-react";

interface ReportChartProps {
  reportType: string;
  data: any;
}

export function ReportChart({ reportType, data }: ReportChartProps) {
  const [chartType, setChartType] = useState("bar");

  // Define colors for charts
  const COLORS = ["#10b981", "#6b7280", "#f59e0b", "#ef4444", "#3b82f6", "#8b5cf6"];

  // Format data for charts based on report type
  const getChartData = () => {
    if (reportType === "sales_overview") {
      // For sales overview, show invoice counts by status
      if (data.metrics?.invoices_by_status) {
        return Object.entries(data.metrics.invoices_by_status).map(([status, count]) => ({
          name: status.charAt(0).toUpperCase() + status.slice(1),
          value: count,
        }));
      }
    } else if (reportType === "opportunity_pipeline") {
      // For opportunity pipeline, show opportunity counts by status
      if (data.metrics?.opportunities_by_status) {
        return Object.entries(data.metrics.opportunities_by_status).map(([status, count]) => ({
          name: status.charAt(0).toUpperCase() + status.slice(1),
          value: count,
        }));
      }
    } else if (reportType === "client_activity") {
      // For client activity, this would be implemented based on the actual data structure
      return [
        { name: "Active", value: data.metrics?.active_clients || 0 },
        { name: "Inactive", value: data.metrics?.inactive_clients || 0 },
        { name: "New", value: data.metrics?.new_clients || 0 },
      ];
    } else if (reportType === "invoice_aging") {
      // For invoice aging, this would be implemented based on the actual data structure
      return [
        { name: "Current", value: 10 },
        { name: "1-30 Days", value: 5 },
        { name: "31-60 Days", value: 3 },
        { name: "61-90 Days", value: 2 },
        { name: "90+ Days", value: 1 },
      ];
    } else if (reportType === "task_completion") {
      // For task completion, this would be implemented based on the actual data structure
      return [
        { name: "Completed", value: data.metrics?.tasks?.completed || 0 },
        { name: "In Progress", value: data.metrics?.tasks?.in_progress || 0 },
        { name: "Open", value: data.metrics?.tasks?.open || 0 },
      ];
    } else if (reportType === "revenue_forecast") {
      // For revenue forecast, this would be implemented based on the actual data structure
      return [
        { name: "Jan", value: 5000 },
        { name: "Feb", value: 7000 },
        { name: "Mar", value: 6000 },
        { name: "Apr", value: 8000 },
        { name: "May", value: 9000 },
        { name: "Jun", value: 11000 },
      ];
    }

    // Default empty data
    return [];
  };

  const chartData = getChartData();

  // Get chart title based on report type
  const getChartTitle = () => {
    switch (reportType) {
      case "sales_overview":
        return "Invoices by Status";
      case "client_activity":
        return "Client Distribution";
      case "opportunity_pipeline":
        return "Opportunities by Stage";
      case "invoice_aging":
        return "Invoice Aging Analysis";
      case "task_completion":
        return "Task Completion Status";
      case "revenue_forecast":
        return "Revenue Forecast";
      default:
        return "Chart Data";
    }
  };

  // Format currency for tooltips
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(value);
  };

  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border rounded p-2 shadow-md">
          <p className="font-medium">{`${label}`}</p>
          <p className="text-sm">{`Value: ${payload[0].value}`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-medium">{getChartTitle()}</h3>
        <Tabs value={chartType} onValueChange={setChartType} className="w-auto">
          <TabsList className="grid w-auto grid-cols-3">
            <TabsTrigger value="bar" className="px-3">
              <BarChart2 className="h-4 w-4" />
            </TabsTrigger>
            <TabsTrigger value="pie" className="px-3">
              <PieChartIcon className="h-4 w-4" />
            </TabsTrigger>
            <TabsTrigger value="line" className="px-3">
              <LineChartIcon className="h-4 w-4" />
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div className="h-80">
        {chartType === "bar" && (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="value" fill="#10b981">
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}

        {chartType === "pie" && (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value}`, "Value"]} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )}

        {chartType === "line" && (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#10b981" activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
