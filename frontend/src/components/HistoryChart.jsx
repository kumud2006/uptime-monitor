
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

function HistoryChart({ history = [], range = 1 }) {
  const data = history.map((item) => ({
    time: new Date(item.timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
    latency: item.latency_ms,
    ok: item.ok,
  }));

  return (
    <div className="chart-container">
      <div className="chart-heading">
        <div>
          <h3>Response time</h3>
          <p>Website latency over the last {range} hour(s)</p>
        </div>
      </div>

      {data.length === 0 ? (
        <div className="empty-state">
          No response-time history available yet.
        </div>
      ) : (
        <div className="chart-area">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart
              data={data}
              margin={{ top: 10, right: 20, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="time" tick={{ fontSize: 12 }} />
              <YAxis
                tick={{ fontSize: 12 }}
                label={{
                  value: "Milliseconds",
                  angle: -90,
                  position: "insideLeft",
                }}
              />
              <Tooltip
                formatter={(value) => [`${value} ms`, "Response time"]}
              />
              <Line
                type="monotone"
                dataKey="latency"
                stroke="#4f46e5"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 5 }}
                connectNulls={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export default HistoryChart;
