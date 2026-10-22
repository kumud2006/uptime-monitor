import { mockTargets, mockHistory, mockIncidents } from "./mock";

const API_URL = (
  import.meta.env.VITE_API_URL ||
  "https://func-uptimemon-c14h3w.azurewebsites.net"
).replace(/\/+$/, "");

// Demo data is used ONLY when VITE_USE_MOCK is exactly "true".
// Any other value (or no value at all) means the live Azure API is used.
export const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

async function request(path, options) {
  const isPost = options && options.method === "POST";
  const response = await fetch(`${API_URL}/api/${path}`, options);

  let data;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const detail = data && data.error ? data.error : `HTTP ${response.status}`;
    throw new Error(
      isPost ? detail : `Could not load ${path.split("?")[0]}: ${detail}`
    );
  }

  return data;
}

export async function getStatus() {
  if (USE_MOCK) return mockTargets;
  return request("status");
}

export async function getHistory(targetId, hours = 24) {
  if (USE_MOCK) return mockHistory;
  if (!targetId) return [];
  return request(
    `history?target_id=${encodeURIComponent(targetId)}&hours=${hours}`
  );
}

export async function getIncidents() {
  if (USE_MOCK) return mockIncidents;
  return request("incidents");
}

export async function addTarget(target) {
  if (USE_MOCK) {
    return {
      id: `mock-${Date.now()}`,
      name: target.name,
      url: target.url,
      ok: true,
      status_code: 200,
      latency_ms: 120,
      uptime_24h: 100,
      last_checked: new Date().toISOString(),
    };
  }

  return request("targets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: target.name,
      url: target.url,
      alert_email: target.email,
      latency_threshold_ms: 1000,
    }),
  });
}
