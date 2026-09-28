import type { ReactNode } from "react";

type Props = { label: string; value: string; detail?: string; icon: ReactNode };

export function MetricCard({ label, value, detail, icon }: Props) {
  return (
    <article className="metric-card">
      <div className="metric-icon">{icon}</div>
      <div>
        <p className="eyebrow">{label}</p>
        <h3>{value}</h3>
        {detail && <p className="muted">{detail}</p>}
      </div>
    </article>
  );
}
