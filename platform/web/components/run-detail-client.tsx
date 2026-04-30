"use client";

import { useEffect, useState } from "react";

import { getRunDetail } from "../lib/platform-api";
import type { RunDetail } from "../lib/sample-data";
import { useAuth } from "./auth-provider";
import { StatusPill } from "./status-pill";

function tone(outcome: RunDetail["decision"]["outcome"]) {
  if (outcome === "dispatch") return "success" as const;
  if (outcome === "clarify") return "warning" as const;
  if (outcome === "refuse" || outcome === "escalate") return "danger" as const;
  return "neutral" as const;
}

export function RunDetailClient({
  runId,
  initialRun,
}: {
  runId: string;
  initialRun: RunDetail | null;
}) {
  const [run, setRun] = useState<RunDetail | null>(initialRun);
  const { token } = useAuth();

  useEffect(() => {
    void getRunDetail(runId, token).then(setRun);
  }, [runId, token]);

  if (!run) {
    return (
      <main className="min-h-screen px-4 py-6 md:px-6">
        <div className="mx-auto max-w-5xl rounded-[2rem] border border-black/8 bg-white/72 px-6 py-8 shadow-[0_25px_70px_rgba(15,29,38,0.08)] backdrop-blur">
          <p className="text-lg text-slate/76">Run not found or access denied.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-4 py-6 md:px-6">
      <div className="mx-auto max-w-5xl space-y-4">
        <div className="rounded-[2rem] border border-black/8 bg-white/72 px-6 py-5 shadow-[0_25px_70px_rgba(15,29,38,0.08)] backdrop-blur">
          <div className="mb-3 flex items-center justify-between gap-3">
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate/55">Run detail</p>
              <h1 className="font-display text-3xl text-ink">{run.run_id}</h1>
            </div>
            <StatusPill label={run.decision.outcome} tone={tone(run.decision.outcome)} />
          </div>
          <p className="text-sm text-slate/72">{run.created_at}</p>
        </div>

        <div className="rounded-[1.6rem] border border-black/8 bg-white/80 p-5 shadow-sm">
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Request</p>
          <p className="text-sm leading-7 text-slate/82">{run.request_text}</p>
        </div>

        <div className="rounded-[1.6rem] border border-black/8 bg-white/80 p-5 shadow-sm">
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Decision</p>
          <p className="text-lg font-semibold text-ink">{run.decision.case_id ?? "Unclassified request"}</p>
          <p className="mt-2 text-sm leading-7 text-slate/78">{run.decision.rationale}</p>
          <div className="mt-4 space-y-3">
            {(run.decision.decision_trace ?? []).map((event, index) => (
              <div key={`${event.stage}-${index}`} className="rounded-[1.1rem] border border-black/6 bg-cloud/80 px-4 py-3">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">{event.stage}</p>
                <p className="mt-2 text-sm leading-6 text-slate/78">{event.detail}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[1.6rem] border border-black/8 bg-white/80 p-5 shadow-sm">
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Execution</p>
          {run.execution ? (
            <>
              <p className="text-lg font-semibold text-ink">{run.execution.procedure}</p>
              <p className="mt-2 text-sm leading-7 text-slate/78">{run.execution.target}</p>
              <pre className="mt-4 overflow-x-auto rounded-[1.1rem] border border-black/6 bg-cloud/80 p-4 text-xs leading-6 text-slate/78">
                {JSON.stringify(run.execution.details ?? {}, null, 2)}
              </pre>
            </>
          ) : (
            <p className="text-sm leading-7 text-slate/78">This run did not execute a governed procedure.</p>
          )}
        </div>
      </div>
    </main>
  );
}
