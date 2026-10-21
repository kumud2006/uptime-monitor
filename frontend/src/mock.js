
const mockTargets = [
  {
    id: "1",
    name: "Google",
    url: "https://www.google.com",
    ok: true,
    status_code: 200,
    latency_ms: 118,
    uptime_24h: 100,
    last_checked: new Date().toISOString(),
  },
  {
    id: "2",
    name: "Example Website",
    url: "https://example.com",
    ok: true,
    status_code: 200,
    latency_ms: 245,
    uptime_24h: 99.95,
    last_checked: new Date().toISOString(),
  },
  {
    id: "3",
    name: "Demo Failure",
    url: "https://httpbin.org/status/500",
    ok: false,
    status_code: 500,
    latency_ms: 310,
    uptime_24h: 96.5,
    last_checked: new Date().toISOString(),
  },
];


const mockHistory = Array.from({ length: 144 }, (_, index) => ({
  timestamp: new Date(Date.now() - (143 - index) * 10 * 60 * 1000).toISOString(),
  latency_ms: 100 + Math.round(Math.random() * 100),
  ok: true,
}));


const mockIncidents = [
  {
    id: "incident-1",
    name: "Demo Failure",
    started_at: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
    resolved_at: null,
  },
  {
    id: "incident-2",
    name: "Example Website",
    started_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    resolved_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
  },
];

export { mockTargets, mockHistory, mockIncidents };
