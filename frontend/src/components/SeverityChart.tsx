import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface SeverityChartProps {
  critical: number;
  high: number;
  medium: number;
  low: number;
  unknown: number;
}

const COLORS = [
  "#ef4444",
  "#f97316",
  "#facc15",
  "#22c55e",
  "#64748b",
];

function SeverityChart({
  critical,
  high,
  medium,
  low,
  unknown,
}: SeverityChartProps) {
  const data = [
    { name: "Critical", value: critical },
    { name: "High", value: high },
    { name: "Medium", value: medium },
    { name: "Low", value: low },
    { name: "Unknown", value: unknown },
  ];

  return (
    <div
      className="chart-wrapper"
      role="img"
      aria-label="Advisory counts grouped by severity"
    >
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={2}
          >
            {data.map((item, index) => (
              <Cell
                key={item.name}
                fill={COLORS[index]}
              />
            ))}
          </Pie>

          <Tooltip
            contentStyle={{
              background: "#111827",
              border: "1px solid #334155",
              borderRadius: "8px",
            }}
          />

          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default SeverityChart;
