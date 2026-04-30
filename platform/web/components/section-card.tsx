import type { ReactNode } from "react";

export function SectionCard({
  eyebrow,
  title,
  children,
  action,
  tone = "light",
}: {
  eyebrow: string;
  title: string;
  children: ReactNode;
  action?: ReactNode;
  tone?: "light" | "dark";
}) {
  const shell =
    tone === "dark"
      ? "border-transparent bg-ink text-cloud shadow-[0_24px_70px_rgba(15,29,38,0.24)]"
      : "border-black/8 bg-white/72 text-ink shadow-[0_20px_50px_rgba(15,29,38,0.08)]";

  const eyebrowColor = tone === "dark" ? "text-sage/75" : "text-slate/55";

  return (
    <section className={`rounded-[1.6rem] border p-6 backdrop-blur ${shell}`}>
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <p className={`mb-2 text-xs font-semibold uppercase tracking-[0.2em] ${eyebrowColor}`}>{eyebrow}</p>
          <h2 className="font-display text-2xl leading-tight">{title}</h2>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
