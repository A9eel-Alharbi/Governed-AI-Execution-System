type StatusTone = "success" | "warning" | "danger" | "neutral";

const toneClasses: Record<StatusTone, string> = {
  success: "border-moss/20 bg-moss/10 text-moss",
  warning: "border-amber/30 bg-amber/15 text-amber",
  danger: "border-ember/25 bg-blush text-ember",
  neutral: "border-slate/15 bg-slate/5 text-slate",
};

export function StatusPill({ label, tone = "neutral" }: { label: string; tone?: StatusTone }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${toneClasses[tone]}`}
    >
      {label}
    </span>
  );
}
