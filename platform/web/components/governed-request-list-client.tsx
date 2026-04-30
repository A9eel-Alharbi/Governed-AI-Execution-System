"use client";

import { useEffect, useState, useTransition } from "react";

import { actOnGovernedRequest, getGovernedRequests, resubmitGovernedRequest } from "../lib/platform-api";
import type { GovernedRequestSummary } from "../lib/sample-data";
import { useAuth } from "./auth-provider";
import { StatusPill } from "./status-pill";

function toneForStatus(status: GovernedRequestSummary["status"]) {
  if (status === "PENDING_APPROVAL" || status === "PENDING_REVIEW") return "warning" as const;
  if (status === "FAILED" || status === "TERMINATED" || status === "REJECTED" || status === "EXECUTION_FAILED") return "danger" as const;
  if (status === "COMPLETED" || status === "DISPATCHED" || status === "APPROVED") return "success" as const;
  return "neutral" as const;
}

function toneForRisk(risk: GovernedRequestSummary["risk_level"]) {
  if (risk === "high") return "danger" as const;
  if (risk === "medium") return "warning" as const;
  return "success" as const;
}

export function GovernedRequestListClient({
  initialRequests,
  projectId,
}: {
  initialRequests: GovernedRequestSummary[];
  projectId?: string;
}) {
  const { token } = useAuth();
  const [requests, setRequests] = useState<GovernedRequestSummary[]>(initialRequests);
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  function refresh() {
    void getGovernedRequests({ token, project_id: projectId }).then(setRequests);
  }

  useEffect(() => {
    refresh();
  }, [token, projectId]);

  function act(requestId: string, action: "approve" | "reject" | "escalate") {
    startTransition(async () => {
      try {
        await actOnGovernedRequest({
          request_id: requestId,
          action,
          token,
          reason:
            action === "approve"
              ? "Approved from HITL queue"
              : action === "reject"
                ? "Rejected from HITL queue"
                : "Escalated from HITL queue",
        });
        setMessage(`Request ${requestId} ${action}d.`);
        refresh();
      } catch {
        setMessage(`Request ${requestId} ${action} failed.`);
      }
    });
  }

  function resubmit(requestId: string) {
    startTransition(async () => {
      try {
        await resubmitGovernedRequest({
          request_id: requestId,
          token,
        });
        setMessage(`Request ${requestId} resubmitted.`);
        refresh();
      } catch {
        setMessage(`Request ${requestId} resubmit failed.`);
      }
    });
  }

  if (requests.length === 0) {
    return <p className="text-sm text-slate/72">No governed requests have been submitted yet.</p>;
  }

  return (
    <div className="space-y-3">
      {message ? <p className="text-sm text-slate/72">{message}</p> : null}
      {requests.map((request) => (
        <div key={request.request_id} className="rounded-[1.3rem] border border-black/6 bg-cloud/85 px-4 py-4">
          <div className="mb-2 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="font-semibold text-ink">{request.request_text}</p>
              <p className="text-sm text-slate/68">
                {request.request_id} · {request.case_id ?? "unclassified"}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <StatusPill label={request.risk_level} tone={toneForRisk(request.risk_level)} />
              <StatusPill label={request.status} tone={toneForStatus(request.status)} />
            </div>
          </div>

          {request.intended_actions.length > 0 ? (
            <p className="text-sm leading-6 text-slate/76">Intended actions: {request.intended_actions.join(", ")}</p>
          ) : null}
          {request.policy_triggers.length > 0 ? (
            <ul className="mt-2 space-y-1 text-sm leading-6 text-slate/76">
              {request.policy_triggers.map((trigger) => (
                <li key={trigger}>- {trigger}</li>
              ))}
            </ul>
          ) : null}
          {request.failure_summary ? <p className="mt-2 text-sm leading-6 text-ember">Failure: {request.failure_summary}</p> : null}
          {request.failure_detail ? (
            <div className="mt-2 rounded-[1rem] border border-ember/15 bg-blush px-3 py-3 text-sm leading-6 text-slate/78">
              <p className="font-semibold text-ember">Execution trace summary</p>
              <p className="mt-1">{request.failure_detail}</p>
              {request.last_successful_step ? <p className="mt-1 text-xs text-slate/58">Last successful step: {request.last_successful_step}</p> : null}
              {request.partial_artifacts.length > 0 ? (
                <div className="mt-2">
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate/56">Partial artifacts</p>
                  <ul className="mt-1 space-y-1 text-xs text-slate/68">
                    {request.partial_artifacts.map((artifact) => (
                      <li key={artifact}>{artifact}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {request.tool_call_log.length > 0 ? (
                <div className="mt-2">
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate/56">Tool call log</p>
                  <ul className="mt-1 space-y-1 text-xs text-slate/68">
                    {request.tool_call_log.map((entry, index) => (
                      <li key={`${request.request_id}-tool-log-${index}`}>
                        {String(entry.step ?? entry.operation ?? "step")} · {String(entry.status ?? "unknown")}
                        {entry.target ? ` · ${String(entry.target)}` : ""}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          ) : null}
          {request.expires_at ? <p className="mt-2 text-xs text-slate/58">Expires at: {request.expires_at}</p> : null}

          {request.status === "PENDING_APPROVAL" ? (
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                onClick={() => act(request.request_id, "approve")}
                disabled={isPending}
                className="rounded-full border border-moss/20 bg-moss/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-moss disabled:opacity-50"
              >
                Approve
              </button>
              <button
                onClick={() => act(request.request_id, "reject")}
                disabled={isPending}
                className="rounded-full border border-ember/20 bg-blush px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-ember disabled:opacity-50"
              >
                Reject
              </button>
              <button
                onClick={() => act(request.request_id, "escalate")}
                disabled={isPending}
                className="rounded-full border border-amber/20 bg-amber/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-amber disabled:opacity-50"
              >
                Escalate
              </button>
            </div>
          ) : null}

          {request.status === "FAILED" ? (
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                onClick={() => resubmit(request.request_id)}
                disabled={isPending}
                className="rounded-full border border-slate/12 bg-white px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-slate disabled:opacity-50"
              >
                Resubmit
              </button>
            </div>
          ) : null}
        </div>
      ))}
    </div>
  );
}
