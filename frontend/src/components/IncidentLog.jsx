
function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "—";

  return date.toLocaleString();
}

function IncidentLog({ incidents = [] }) {
  const sortedIncidents = [...incidents].sort(
    (a, b) => new Date(b.started_at) - new Date(a.started_at)
  );

  return (
    <div className="incident-container">
      <div className="incident-heading">
        <div>
          <h3>Incident log</h3>
          <p>Website failures and recoveries</p>
        </div>

        <span className="incident-count">
          {incidents.length} incident{incidents.length === 1 ? "" : "s"}
        </span>
      </div>

      {sortedIncidents.length === 0 ? (
        <div className="empty-state">
          No incidents recorded. All quiet!
        </div>
      ) : (
        <div className="incident-list">
          {sortedIncidents.map((incident, index) => {
            const isResolved = Boolean(incident.resolved_at);

            return (
              <div
                className="incident-item"
                key={incident.id ?? `${incident.started_at}-${index}`}
              >
                <div
                  className={`incident-indicator ${
                    isResolved ? "resolved" : "ongoing"
                  }`}
                />

                <div className="incident-details">
                  <div className="incident-title">
                    {incident.name || "Website incident"}
                  </div>

                  <div className="incident-time">
                    Started: {formatDate(incident.started_at)}
                  </div>

                  {isResolved && (
                    <div className="incident-time">
                      Resolved: {formatDate(incident.resolved_at)}
                    </div>
                  )}
                </div>

                <span
                  className={`incident-status ${
                    isResolved ? "resolved" : "ongoing"
                  }`}
                >
                  {isResolved ? "Resolved" : "Ongoing"}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default IncidentLog;
