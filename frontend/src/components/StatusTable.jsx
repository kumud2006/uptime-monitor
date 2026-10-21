
function StatusTable({ targets = [] }) {
  if (targets.length === 0) {
    return (
      <div className="empty-state">
        No websites to display yet.
      </div>
    );
  }

  return (
    <div className="table-container">
      <table className="status-table">
        <thead>
          <tr>
            <th>Website</th>
            <th>Status</th>
            <th>HTTP Code</th>
            <th>Response Time</th>
            <th>Uptime (24h)</th>
            <th>Last Checked</th>
          </tr>
        </thead>

        <tbody>
          {targets.map((target) => {
            const isUp = target.ok === true;

            return (
              <tr key={target.id ?? target.url}>
                <td>
                  <div className="website-name">
                    {target.name || target.url}
                  </div>
                  <div className="website-url">
                    {target.url}
                  </div>
                </td>

                <td>
                  <span className={`status-badge ${isUp ? "up" : "down"}`}>
                    <span className="status-dot" />
                    {isUp ? "UP" : "DOWN"}
                  </span>
                </td>

                <td>{target.status_code ?? "—"}</td>

                <td>
                  {target.latency_ms != null
                    ? `${target.latency_ms} ms`
                    : "—"}
                </td>

                <td>
                  {target.uptime_24h != null
                    ? `${Number(target.uptime_24h).toFixed(2)}%`
                    : "—"}
                </td>

                <td>
                  {target.last_checked
                    ? new Date(target.last_checked).toLocaleString()
                    : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default StatusTable;
