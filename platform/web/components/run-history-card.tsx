import Link from "next/link";

import type { RunSummary } from "../lib/sample-data";
import { StatusPill } from "./status-pill";

function tone(outcome: RunSummary["outcome"]) {
  if (outcome === "dispatch") return "success" as const;
  if (outcome === "clarify") return "warning" as const;
  if (outcome === "refuse" || outcome === "escalate") return "danger" as const;
  return "neutral" as const;
}

export function RunHistoryCard({ run }: { run: RunSummary }) {
  return (
    <Link
      href={`/runs/${run.run_id}`}
      className="block rounded-[1.4rem] border border-black/6 bg-cloud/85 px-4 py-4 transition hover:border-moss/30 hover:bg-white"
    >
      <div className="mb-2 flex items-center justify-between gap-3">
        <div>
          <p className="font-semibold text-ink">{run.run_id}</p>
          <p className="text-sm text-slate/68">
            {run.case_id ?? "unclassified"} · {run.created_at}
          </p>
        </div>
        <StatusPill label={run.outcome} tone={tone(run.outcome)} />
      </div>
      <p className="text-sm leading-6 text-slate/78">{run.text}</p>
      {run.execution_status ? (
        <p className="mt-2 text-xs uppercase tracking-[0.18em] text-slate/55">Execution: {run.execution_status}</p>
      ) : null}
    </Link>
  );
}
