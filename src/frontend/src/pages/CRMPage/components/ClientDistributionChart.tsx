import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ClientDistribution } from "@/types/crm";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

interface ClientDistributionChartProps {
  data?: ClientDistribution;
  isLoading: boolean;
}

export function ClientDistributionChart({ data, isLoading }: ClientDistributionChartProps) {
  // Colors for the chart
  const COLORS = ["#10b981", "#6b7280", "#f59e0b"];

  // Format data for the chart
  const chartData = data
    ? [
        { name: "Active", value: data.active },
        { name: "Inactive", value: data.inactive },
        { name: "Lead", value: data.lead },
      ]
    : [];

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Client Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex h-[200px] items-center justify-center">
            <Skeleton className="h-[200px] w-full" />
          </div>
        ) : (
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => [`${value} clients`, "Count"]}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
