import { useState, useEffect } from "react";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { useGetClientsQuery } from "@/controllers/API/queries/crm";
import { extractItems } from "@/types/crm/pagination";
import CRMSidebarComponent from "@/components/core/crmSidebarComponent";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import {
  BarChart,
  PieChart,
  LineChart,
  Download,
  Calendar,
  Filter,
  Save,
  Share,
  Plus,
  FileText,
  Users,
  TrendingUp,
  DollarSign
} from "lucide-react";
import { format } from "date-fns";
import { api as apiClient } from "@/controllers/API/api";
import { useCRMStore } from "@/stores/crmStore";
import { ReportChart } from "./components/ReportChart";
import { ReportDataTable } from "./components/ReportDataTable";
import { DateRangePicker } from "./components/DateRangePicker";

// Report types and time frames from the API
const REPORT_TYPES = [
  { id: "sales_overview", name: "Sales Overview", icon: <DollarSign className="h-4 w-4" /> },
  { id: "client_activity", name: "Client Activity", icon: <Users className="h-4 w-4" /> },
  { id: "opportunity_pipeline", name: "Opportunity Pipeline", icon: <TrendingUp className="h-4 w-4" /> },
  { id: "invoice_aging", name: "Invoice Aging", icon: <FileText className="h-4 w-4" /> },
  { id: "task_completion", name: "Task Completion", icon: <FileText className="h-4 w-4" /> },
  { id: "revenue_forecast", name: "Revenue Forecast", icon: <TrendingUp className="h-4 w-4" /> },
  { id: "custom", name: "Custom Report", icon: <Plus className="h-4 w-4" /> }
];

const TIME_FRAMES = [
  { id: "last_7_days", name: "Last 7 Days" },
  { id: "last_30_days", name: "Last 30 Days" },
  { id: "last_90_days", name: "Last 90 Days" },
  { id: "last_12_months", name: "Last 12 Months" },
  { id: "year_to_date", name: "Year to Date" },
  { id: "custom", name: "Custom Date Range" }
];

const EXPORT_FORMATS = [
  { id: "json", name: "JSON" },
  { id: "csv", name: "CSV" },
  { id: "excel", name: "Excel" }
];

export default function ReportsPage() {
  // Get current workspace ID
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);

  // Local state
  const [activeTab, setActiveTab] = useState("standard");
  const [selectedReportType, setSelectedReportType] = useState("sales_overview");
  const [selectedTimeFrame, setSelectedTimeFrame] = useState("last_30_days");
  const [selectedClient, setSelectedClient] = useState<string | null>(null);
  const [customDateRange, setCustomDateRange] = useState<{ from: Date | null; to: Date | null }>({
    from: null,
    to: null
  });
  const [reportData, setReportData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableMetrics, setAvailableMetrics] = useState<string[]>([]);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [showDateRangePicker, setShowDateRangePicker] = useState(false);
  const [exportFormat, setExportFormat] = useState<string | null>(null);

  // Fetch clients for filtering
  const { data: clientsResponse } = useGetClientsQuery(
    currentWorkspaceId
      ? {
          workspace_id: currentWorkspaceId,
        }
      : undefined,
    {
      enabled: !!currentWorkspaceId,
    }
  );

  // Extract clients from response (handle both paginated and non-paginated)
  const clients = clientsResponse ? extractItems(clientsResponse) : [];

  // Fetch report types and available metrics
  useEffect(() => {
    const fetchReportTypes = async () => {
      try {
        const response = await apiClient.get('/api/v1/reports/types');
        const reportType = response.data.report_types.find(rt => rt.id === selectedReportType);
        if (reportType) {
          setAvailableMetrics(reportType.metrics);
          setSelectedMetrics(reportType.metrics.slice(0, 2)); // Select first two metrics by default
        }
      } catch (error) {
        console.error("Error fetching report types:", error);
      }
    };

    fetchReportTypes();
  }, [selectedReportType]);

  // Generate report
  const generateReport = async () => {
    if (!currentWorkspaceId) return;

    setIsLoading(true);
    setError(null);

    try {
      let url = `/api/v1/reports/${selectedReportType}?workspace_id=${currentWorkspaceId}&time_frame=${selectedTimeFrame}`;

      // Add client filter if selected
      if (selectedClient) {
        url += `&client_id=${selectedClient}`;
      }

      // Add custom date range if selected
      if (selectedTimeFrame === 'custom' && customDateRange.from && customDateRange.to) {
        url += `&start_date=${customDateRange.from.toISOString()}&end_date=${customDateRange.to.toISOString()}`;
      }

      // Add metrics for custom reports
      if (selectedReportType === 'custom' && selectedMetrics.length > 0) {
        selectedMetrics.forEach(metric => {
          url += `&metrics=${metric}`;
        });
      }

      // Add export format if selected
      if (exportFormat) {
        url += `&export_format=${exportFormat}`;

        // For export, use window.open to trigger download
        window.open(url, '_blank');
        setExportFormat(null);
        setIsLoading(false);
        return;
      }

      const response = await apiClient.get(url);
      setReportData(response.data);
    } catch (error: any) {
      console.error("Error generating report:", error);
      setError(error.response?.data?.detail || "Failed to generate report");
    } finally {
      setIsLoading(false);
    }
  };

  // Handle time frame change
  const handleTimeFrameChange = (value: string) => {
    setSelectedTimeFrame(value);
    if (value !== 'custom') {
      setShowDateRangePicker(false);
    } else {
      setShowDateRangePicker(true);
    }
  };

  // Format currency
  const formatCurrency = (value: number) => {
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
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Reports & Analytics</h1>
          <p className="text-muted-foreground">
            Generate and analyze reports for your CRM data
          </p>
        </div>

        <Tabs defaultValue="standard" value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="standard">Standard Reports</TabsTrigger>
            <TabsTrigger value="custom">Custom Reports</TabsTrigger>
            <TabsTrigger value="saved">Saved Reports</TabsTrigger>
          </TabsList>

          <TabsContent value="standard" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Report Configuration</CardTitle>
                <CardDescription>
                  Select report type and parameters to generate a report
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                  <div className="space-y-2">
                    <Label htmlFor="report-type">Report Type</Label>
                    <Select value={selectedReportType} onValueChange={setSelectedReportType}>
                      <SelectTrigger id="report-type">
                        <SelectValue placeholder="Select report type" />
                      </SelectTrigger>
                      <SelectContent>
                        {REPORT_TYPES.filter(rt => rt.id !== 'custom').map((type) => (
                          <SelectItem key={type.id} value={type.id}>
                            <div className="flex items-center">
                              {type.icon}
                              <span className="ml-2">{type.name}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="time-frame">Time Frame</Label>
                    <Select value={selectedTimeFrame} onValueChange={handleTimeFrameChange}>
                      <SelectTrigger id="time-frame">
                        <SelectValue placeholder="Select time frame" />
                      </SelectTrigger>
                      <SelectContent>
                        {TIME_FRAMES.map((timeFrame) => (
                          <SelectItem key={timeFrame.id} value={timeFrame.id}>
                            {timeFrame.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="client-filter">Client Filter (Optional)</Label>
                    <Select value={selectedClient || "all"} onValueChange={(value) => setSelectedClient(value === "all" ? null : value)}>
                      <SelectTrigger id="client-filter">
                        <SelectValue placeholder="All Clients" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Clients</SelectItem>
                        {clients?.map((client) => (
                          <SelectItem key={client.id} value={client.id}>
                            {client.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {showDateRangePicker && (
                  <div className="mt-4">
                    <Label>Custom Date Range</Label>
                    <DateRangePicker
                      dateRange={customDateRange}
                      onDateRangeChange={setCustomDateRange}
                    />
                  </div>
                )}

                <div className="mt-6 flex items-center justify-between">
                  <div className="flex space-x-2">
                    <Button onClick={generateReport} disabled={isLoading}>
                      {isLoading ? "Generating..." : "Generate Report"}
                    </Button>

                    <Select value={exportFormat || "none"} onValueChange={(value) => setExportFormat(value === "none" ? null : value)}>
                      <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Export Report" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">Export Report</SelectItem>
                        {EXPORT_FORMATS.map((format) => (
                          <SelectItem key={format.id} value={format.id}>
                            <div className="flex items-center">
                              <Download className="mr-2 h-4 w-4" />
                              <span>Export as {format.name}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <Button variant="outline" onClick={() => setReportData(null)}>
                    Clear
                  </Button>
                </div>
              </CardContent>
            </Card>

            {error && (
              <Card className="border-red-500">
                <CardContent className="pt-6">
                  <p className="text-red-500">{error}</p>
                </CardContent>
              </Card>
            )}

            {isLoading ? (
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    <Skeleton className="h-8 w-full" />
                    <Skeleton className="h-64 w-full" />
                    <Skeleton className="h-8 w-full" />
                    <Skeleton className="h-32 w-full" />
                  </div>
                </CardContent>
              </Card>
            ) : reportData ? (
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>
                      {REPORT_TYPES.find(rt => rt.id === selectedReportType)?.name || "Report"} - {
                        selectedTimeFrame === 'custom' && customDateRange.from && customDateRange.to
                          ? `${format(customDateRange.from, 'MMM d, yyyy')} to ${format(customDateRange.to, 'MMM d, yyyy')}`
                          : TIME_FRAMES.find(tf => tf.id === selectedTimeFrame)?.name
                      }
                    </CardTitle>
                    <CardDescription>
                      Generated on {format(new Date(), 'MMM d, yyyy, h:mm a')}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ReportChart
                      reportType={selectedReportType}
                      data={reportData}
                    />

                    <Separator className="my-6" />

                    <ReportDataTable
                      reportType={selectedReportType}
                      data={reportData}
                    />
                  </CardContent>
                </Card>
              </div>
            ) : null}
          </TabsContent>

          <TabsContent value="custom" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Custom Report Builder</CardTitle>
                <CardDescription>
                  Build a custom report by selecting metrics and dimensions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-center text-muted-foreground">
                  Custom report builder will be implemented in the next phase.
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="saved" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Saved Reports</CardTitle>
                <CardDescription>
                  Access your saved reports
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-center text-muted-foreground">
                  Saved reports functionality will be implemented in the next phase.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
