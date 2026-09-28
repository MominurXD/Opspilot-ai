export type DashboardPayload = {
  metrics: {
    revenue: number;
    expenses: number;
    profit: number;
    orders: number;
    margin_percent: number;
    average_order_value: number;
    revenue_change_percent: number;
  };
  timeline: Array<{ date: string; revenue: number; expenses: number; profit: number; orders: number }>;
  forecast: Array<{ date: string; predicted_revenue: number }>;
  anomalies: Array<{ date: string; metric: string; value: number; severity: string; message: string }>;
  insights: Array<{ type: string; title: string; detail: string }>;
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export async function getDashboard(): Promise<DashboardPayload> {
  const response = await fetch(`${API_URL}/dashboard`);
  if (!response.ok) throw new Error("Failed to load dashboard");
  return response.json();
}

export async function uploadCsv(file: File): Promise<DashboardPayload> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${API_URL}/dashboard/upload`, { method: "POST", body: form });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? "Failed to analyse CSV");
  }
  return response.json();
}
