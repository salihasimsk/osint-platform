import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface OrganizationChartProps {
  organizations: Record<string, number>;
}

function OrganizationChart({
  organizations,
}: OrganizationChartProps) {
  const data = Object.entries(organizations).map(
    ([name, value]) => ({
      name,
      value,
    }),
  );

  return (
    <div
      className="chart-wrapper"
      role="img"
      aria-label="Advisory counts grouped by organization"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{
            top: 10,
            right: 25,
            bottom: 10,
            left: 5,
          }}
        >
          <CartesianGrid
            stroke="#263244"
            horizontal={false}
          />

          <XAxis
            type="number"
            stroke="#94a3b8"
          />

          <YAxis
            type="category"
            dataKey="name"
            width={75}
            stroke="#94a3b8"
          />

          <Tooltip
            contentStyle={{
              background: "#111827",
              border: "1px solid #334155",
              borderRadius: "8px",
            }}
          />

          <Bar
            dataKey="value"
            fill="#22d3ee"
            radius={[0, 6, 6, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default OrganizationChart;
