
import { mockTargets, mockHistory, mockIncidents } from "./mock";

const API_URL = (
  import.meta.env.VITE_API_URL ||
  "https://func-uptimemon-c14h3w.azurewebsites.net"
).replace(/\/+$/, "");

export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";

async function getJson(endpoint) {
  const response = await fetch(`${API_URL}/api/${endpoint}`);

  if (!response.ok) {
    throw new Error(
      `Could not load ${endpoint}: HTTP ${response.status}`
    );
  }

  return response.json();
}

export async function getStatus() {
  if (USE_MOCK) return mockTargets;
  return getJson("status");
}

export async function getHistory() {
  if (USE_MOCK) return mockHistory;
  return getJson("history");
}

export async function getIncidents() {
  if (USE_MOCK) return mockIncidents;
  return getJson("incidents");
}

export async function addTarget(target) {
  if (USE_MOCK) {
    return {
      ...target,
      id: target.id || `mock-${Date.now()}`,
    };
  }

  throw new Error(
    "Adding websites through the live API is disabled until the backend is confirmed ready."
  );
}
