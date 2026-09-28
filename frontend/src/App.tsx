import { useEffect, useMemo, useRef, useState } from "react";
import { AlertTriangle, ArrowUpRight, BrainCircuit, PoundSterling, ShoppingBag, Upload, WalletCards } from "lucide-react";
import { Area, AreaChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { MetricCard } from "./components/MetricCard";
import { DashboardPayload, getDashboard, uploadCsv } from "./lib/api";

const money = new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP", maximumFractionDigits: 0 });

export default function App() {
  const [data, setData] = useState<DashboardPayload | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getDashboard().then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, []);

  const combined = useMemo(() => {
    if (!data) return [];
    return [
      ...data.timeline.slice(-10).map((row) => ({ date: row.date.slice(5), actual: row.revenue, forecast: null })),
      ...data.forecast.map((row) => ({ date: row.date.slice(5), actual: null, forecast: row.predicted_revenue })),
    ];
  }, [data]);

  async function handleFile(file?: File) {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      setData(await uploadCsv(file));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  if (loading && !data) return <main className="center">Analysing business performance…</main>;
  if (!data) return <main className="center">{error || "Dashboard unavailable"}</main>;

  const m = data.metrics;
  return (
    <main className="shell">
      <header className="hero">
        <div>
          <div className="brand"><BrainCircuit size={26} /> OpsPilot AI</div>
          <h1>Turn daily operations into decisions.</h1>
          <p>Revenue intelligence, anomaly detection and forecasting for small businesses.</p>
        </div>
        <div>
          <input ref={inputRef} hidden type="file" accept=".csv" onChange={(e) => handleFile(e.target.files?.[0])} />
          <button onClick={() => inputRef.current?.click()}><Upload size={18} /> Analyse CSV</button>
        </div>
      </header>

      {error && <div className="error">{error}</div>}

      <section className="metrics-grid">
        <MetricCard label="7-day revenue" value={money.format(m.revenue)} detail={`${m.revenue_change_percent >= 0 ? "+" : ""}${m.revenue_change_percent}% vs previous week`} icon={<PoundSterling />} />
        <MetricCard label="Operating profit" value={money.format(m.profit)} detail={`${m.margin_percent}% margin`} icon={<WalletCards />} />
        <MetricCard label="Orders" value={m.orders.toLocaleString()} detail={`${money.format(m.average_order_value)} average order`} icon={<ShoppingBag />} />
        <MetricCard label="Detected anomalies" value={String(data.anomalies.length)} detail="Last 30 days" icon={<AlertTriangle />} />
      </section>

      <section className="panel wide">
        <div className="panel-title"><div><p className="eyebrow">Revenue outlook</p><h2>Actual vs 7-day forecast</h2></div><ArrowUpRight /></div>
        <div className="chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={combined}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="date"/><YAxis/><Tooltip formatter={(v) => money.format(Number(v))}/><Line type="monotone" dataKey="actual" strokeWidth={3} connectNulls/><Line type="monotone" dataKey="forecast" strokeWidth={3} strokeDasharray="6 4" connectNulls/></LineChart></ResponsiveContainer></div>
      </section>

      <section className="two-col">
        <article className="panel">
          <p className="eyebrow">Decision support</p><h2>AI-style business insights</h2>
          <div className="stack">{data.insights.map((item) => <div className={`insight ${item.type}`} key={item.title}><strong>{item.title}</strong><p>{item.detail}</p></div>)}</div>
        </article>
        <article className="panel">
          <p className="eyebrow">Risk radar</p><h2>Operational anomalies</h2>
          <div className="stack">{data.anomalies.length ? data.anomalies.map((item, i) => <div className="anomaly" key={`${item.date}-${item.metric}-${i}`}><span>{item.severity}</span><strong>{item.metric} · {item.date}</strong><p>{item.message}</p></div>) : <p className="muted">No unusual activity detected.</p>}</div>
        </article>
      </section>

      <section className="panel wide">
        <p className="eyebrow">Unit economics</p><h2>Revenue and expenses</h2>
        <div className="chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={data.timeline}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="date" tickFormatter={(v) => String(v).slice(5)}/><YAxis/><Tooltip formatter={(v) => money.format(Number(v))}/><Area type="monotone" dataKey="revenue" fillOpacity={0.15} strokeWidth={2}/><Area type="monotone" dataKey="expenses" fillOpacity={0.08} strokeWidth={2}/></AreaChart></ResponsiveContainer></div>
      </section>
    </main>
  );
}
