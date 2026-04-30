"use client";

import { useMemo, useState, useTransition } from "react";

import { submitGovernedRequest } from "../lib/platform-api";
import type { GovernedRequestSummary, ProjectSummary, RunResponse } from "../lib/sample-data";
import { useAuth } from "./auth-provider";
import { StatusPill } from "./status-pill";

export function RequestConsole({
  project,
  initialResponse,
}: {
  project: ProjectSummary;
  initialResponse: RunResponse;
}) {
  const [text, setText] = useState("Run WP-001 now");
  const [response, setResponse] = useState<RunResponse>(initialResponse);
  const [shouldExecute, setShouldExecute] = useState(true);
  const [dryRun, setDryRun] = useState(false);
  const [governedRequest, setGovernedRequest] = useState<GovernedRequestSummary | null>(null);
  const [isPending, startTransition] = useTransition();
  const { token } = useAuth();

  const trace = useMemo(() => response.decision.decision_trace ?? [], [response]);

  const tone =
    response.decision.outcome === "dispatch"
      ? "success"
      : response.decision.outcome === "clarify"
        ? "warning"
        : response.decision.outcome === "escalate" || response.decision.outcome === "refuse"
          ? "danger"
          : "neutral";

  function submit() {
    startTransition(async () => {
      const result = await submitGovernedRequest({
        project_id: project.project_id,
        text,
        execute: shouldExecute,
        persist: true,
        dry_run: dryRun,
        token,
      });
      setGovernedRequest(result);
      setResponse((current) => ({
        ...current,
        decision: {
          ...current.decision,
          raw_input: result.request_text,
          restored_input: result.request_text,
          normalized_input: result.request_text,
          outcome: (result.outcome ?? "dispatch") as RunResponse["decision"]["outcome"],
          rationale:
            result.status === "PENDING_APPROVAL"
              ? "Dispatch paused at the HITL gate. Human approval is required before Layer 4 execution."
              : result.failure_summary ?? current.decision.rationale,
          case_id: result.case_id,
          decision_trace: result.decision_trace,
        },
        context: result.request_context,
      }));
    });
  }

  return (
    <div className="rounded-[1.4rem] border border-slate/10 bg-white/80 p-4 shadow-sm">
      <p className="mb-3 text-sm text-slate/70">
        Submit a request. The platform will clarify, refuse, dispatch, or escalate before any model acts.
      </p>

      <textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        className="min-h-[112px] w-full rounded-[1.2rem] border border-dashed border-slate/18 bg-cloud px-4 py-4 text-sm text-slate outline-none transition focus:border-moss/35"
      />

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <button
          onClick={submit}
          disabled={isPending || project.is_processing}
          className="rounded-full bg-ink px-4 py-2 text-sm font-semibold text-cloud disabled:opacity-60"
        >
          {isPending ? "Running..." : project.is_processing ? "Project locked" : shouldExecute ? "Interpret and execute" : "Interpret only"}
        </button>
        <button
          onClick={() => setShouldExecute((value) => !value)}
          className="rounded-full border border-slate/12 bg-white px-4 py-2 text-sm font-semibold text-slate"
        >
          {shouldExecute ? "Execution enabled" : "Execution disabled"}
        </button>
        <button
          onClick={() => setDryRun((value) => !value)}
          className="rounded-full border border-slate/12 bg-white px-4 py-2 text-sm font-semibold text-slate"
        >
          {dryRun ? "Dry-run enabled" : "Dry-run disabled"}
        </button>
        <StatusPill label={response.decision.outcome} tone={tone} />
        {project.is_processing ? <StatusPill label="single request lock" tone="warning" /> : null}
      </div>

      <div className="mt-5 rounded-[1.2rem] border border-black/6 bg-parchment px-4 py-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <p className="font-semibold text-ink">{response.decision.case_id ?? "Unclassified request"}</p>
          {response.execution ? <StatusPill label={response.execution.status} tone="neutral" /> : null}
        </div>
        <p className="text-sm leading-6 text-slate/76">{response.decision.rationale}</p>
        {governedRequest ? (
          <div className="mt-3 rounded-[1rem] border border-black/6 bg-white px-4 py-3">
            <div className="mb-2 flex items-center justify-between gap-3">
              <p className="text-sm font-semibold text-ink">{governedRequest.request_id}</p>
              <StatusPill label={governedRequest.status} tone={governedRequest.status === "PENDING_APPROVAL" ? "warning" : "neutral"} />
            </div>
            <p className="text-sm leading-6 text-slate/76">Risk: {governedRequest.risk_level}</p>
            {governedRequest.intended_actions.length > 0 ? (
              <p className="mt-1 text-sm leading-6 text-slate/76">Intended actions: {governedRequest.intended_actions.join(", ")}</p>
            ) : null}
          </div>
        ) : null}
        {response.decision.clarification_question ? (
          <p className="mt-3 text-sm leading-6 text-amber">Clarification: {response.decision.clarification_question}</p>
        ) : null}
        {response.decision.refusal_reason ? (
          <p className="mt-3 text-sm leading-6 text-ember">Refusal reason: {response.decision.refusal_reason}</p>
        ) : null}
        {response.decision.escalation_reason ? (
          <p className="mt-3 text-sm leading-6 text-ember">Escalation reason: {response.decision.escalation_reason}</p>
        ) : null}
      </div>

      <div className="mt-4 grid gap-3">
        {trace.map((event, index) => (
          <div key={`${event.stage}-${index}`} className="rounded-[1.1rem] border border-black/6 bg-cloud/80 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">{event.stage}</p>
            <p className="mt-2 text-sm leading-6 text-slate/78">{event.detail}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
