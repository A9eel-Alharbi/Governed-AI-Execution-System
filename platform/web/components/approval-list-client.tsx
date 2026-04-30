"use client";

import { useEffect, useState, useTransition } from "react";

import { createApproval, getApprovals, updateApproval } from "../lib/platform-api";
import type { ApprovalSummary } from "../lib/sample-data";
import { useAuth } from "./auth-provider";
import { StatusPill } from "./status-pill";

function tone(status: ApprovalSummary["status"]) {
  if (status === "approved") return "success" as const;
  if (status === "draft") return "warning" as const;
  if (status === "rejected" || status === "expired") return "danger" as const;
  return "neutral" as const;
}

export function ApprovalListClient({
  projectId,
  initialApprovals,
}: {
  projectId: string;
  initialApprovals: ApprovalSummary[];
}) {
  const [approvals, setApprovals] = useState<ApprovalSummary[]>(initialApprovals);
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [createForm, setCreateForm] = useState({
    title: "",
    target_class: "general" as ApprovalSummary["target_class"],
    environment: "dev" as ApprovalSummary["environment"],
    case_ids: "",
    notes: "",
  });
  const { token } = useAuth();

  function refreshApprovals() {
    void getApprovals({ token, project_id: projectId }).then(setApprovals);
  }

  useEffect(() => {
    refreshApprovals();
  }, [token, projectId]);

  function submitCreate() {
    startTransition(async () => {
      try {
        await createApproval({
          project_id: projectId,
          title: createForm.title,
          target_class: createForm.target_class,
          environment: createForm.environment,
          case_ids: createForm.case_ids
            .split(",")
            .map((value) => value.trim())
            .filter(Boolean),
          notes: createForm.notes
            .split("\n")
            .map((value) => value.trim())
            .filter(Boolean),
          token,
        });
        setCreateForm({
          title: "",
          target_class: "general",
          environment: "dev",
          case_ids: "",
          notes: "",
        });
        setMessage("Approval record created.");
        refreshApprovals();
      } catch {
        setMessage("Approval creation failed.");
      }
    });
  }

  function setApprovalStatus(approval: ApprovalSummary, status: ApprovalSummary["status"]) {
    startTransition(async () => {
      try {
        const approvedBy =
          status === "approved" && approval.approved_by.length === 0 ? ["platform.owner"] : approval.approved_by;
        await updateApproval({
          approval_id: approval.approval_id,
          status,
          approved_by: approvedBy,
          notes: approval.notes,
          token,
        });
        setMessage(`Approval ${approval.approval_id} updated to ${status}.`);
        refreshApprovals();
      } catch {
        setMessage("Approval update failed.");
      }
    });
  }

  return (
    <div className="space-y-3">
      <div className="rounded-[1.3rem] border border-black/6 bg-white px-4 py-4">
        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Create approval</p>
        <div className="grid gap-3 md:grid-cols-2">
          <input
            value={createForm.title}
            onChange={(event) => setCreateForm((current) => ({ ...current, title: event.target.value }))}
            placeholder="Production security validation approval"
            className="w-full rounded-2xl border border-slate/12 bg-cloud px-4 py-3 text-sm outline-none focus:border-moss/40 md:col-span-2"
          />
          <select
            value={createForm.target_class}
            onChange={(event) =>
              setCreateForm((current) => ({
                ...current,
                target_class: event.target.value as ApprovalSummary["target_class"],
              }))
            }
            className="w-full rounded-2xl border border-slate/12 bg-cloud px-4 py-3 text-sm outline-none focus:border-moss/40"
          >
            <option value="general">general</option>
            <option value="security">security</option>
            <option value="production">production</option>
            <option value="infrastructure">infrastructure</option>
          </select>
          <select
            value={createForm.environment}
            onChange={(event) =>
              setCreateForm((current) => ({
                ...current,
                environment: event.target.value as ApprovalSummary["environment"],
              }))
            }
            className="w-full rounded-2xl border border-slate/12 bg-cloud px-4 py-3 text-sm outline-none focus:border-moss/40"
          >
            <option value="dev">dev</option>
            <option value="staging">staging</option>
            <option value="prod">prod</option>
          </select>
          <input
            value={createForm.case_ids}
            onChange={(event) => setCreateForm((current) => ({ ...current, case_ids: event.target.value }))}
            placeholder="ops.run_validation, security.protected_resource_change"
            className="w-full rounded-2xl border border-slate/12 bg-cloud px-4 py-3 text-sm outline-none focus:border-moss/40 md:col-span-2"
          />
          <textarea
            value={createForm.notes}
            onChange={(event) => setCreateForm((current) => ({ ...current, notes: event.target.value }))}
            placeholder="One note per line"
            className="min-h-28 w-full rounded-2xl border border-slate/12 bg-cloud px-4 py-3 text-sm outline-none focus:border-moss/40 md:col-span-2"
          />
        </div>
        <div className="mt-3 flex items-center justify-between gap-3">
          <p className="text-sm text-slate/72">{message ?? "Author approvals directly from the project governance view."}</p>
          <button
            onClick={submitCreate}
            disabled={isPending || !createForm.title.trim()}
            className="rounded-full bg-ink px-4 py-2 text-sm font-semibold text-cloud disabled:opacity-50"
          >
            {isPending ? "Saving..." : "Create approval"}
          </button>
        </div>
      </div>

      {approvals.length === 0 ? <p className="text-sm text-slate/72">No approval records have been defined for this project yet.</p> : null}

      {approvals.map((approval) => (
        <div key={approval.approval_id} className="rounded-[1.3rem] border border-black/6 bg-cloud/85 px-4 py-4">
          <div className="mb-2 flex items-center justify-between gap-3">
            <div>
              <p className="font-semibold text-ink">{approval.title}</p>
              <p className="text-sm text-slate/68">
                {approval.approval_id} · {approval.target_class} · {approval.environment}
              </p>
            </div>
            <StatusPill label={approval.status} tone={tone(approval.status)} />
          </div>
          {approval.case_ids.length > 0 ? (
            <p className="text-sm leading-6 text-slate/76">Cases: {approval.case_ids.join(", ")}</p>
          ) : null}
          {approval.approved_by.length > 0 ? (
            <p className="mt-1 text-sm leading-6 text-slate/76">Approved by: {approval.approved_by.join(", ")}</p>
          ) : null}
          {approval.notes.length > 0 ? (
            <ul className="mt-2 space-y-1 text-sm leading-6 text-slate/76">
              {approval.notes.map((note) => (
                <li key={note}>- {note}</li>
              ))}
            </ul>
          ) : null}
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              onClick={() => setApprovalStatus(approval, "approved")}
              disabled={isPending}
              className="rounded-full border border-moss/20 bg-moss/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-moss disabled:opacity-50"
            >
              Approve
            </button>
            <button
              onClick={() => setApprovalStatus(approval, "rejected")}
              disabled={isPending}
              className="rounded-full border border-ember/20 bg-blush px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-ember disabled:opacity-50"
            >
              Reject
            </button>
            <button
              onClick={() => setApprovalStatus(approval, "expired")}
              disabled={isPending}
              className="rounded-full border border-slate/12 bg-white px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-slate disabled:opacity-50"
            >
              Expire
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
