"use client";

import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";

import { getPolicyProfile, getPolicyProfileHistory, updatePolicyProfile } from "../lib/platform-api";
import type { PolicyProfile, PolicyProfileVersion } from "../lib/sample-data";
import { useAuth } from "./auth-provider";
import { StatusPill } from "./status-pill";

function toneForApproval(state: PolicyProfile["approval_state"]) {
  return state === "approved" ? ("success" as const) : ("warning" as const);
}

type PolicyFormState = {
  environment: PolicyProfile["environment"];
  approval_state: PolicyProfile["approval_state"];
  target_class: PolicyProfile["target_class"];
  destructive_action: boolean;
  path_privilege: string;
  human_review_required: boolean;
};

export function PolicyProfileClient({
  projectId,
  initialProfile,
}: {
  projectId: string;
  initialProfile: PolicyProfile | null;
}) {
  const { token } = useAuth();
  const [profile, setProfile] = useState<PolicyProfile | null>(initialProfile);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notesText, setNotesText] = useState(initialProfile?.notes.join("\n") ?? "");
  const [reason, setReason] = useState("");
  const [history, setHistory] = useState<PolicyProfileVersion[]>([]);
  const [form, setForm] = useState<PolicyFormState>({
    environment: initialProfile?.environment ?? "dev",
    approval_state: initialProfile?.approval_state ?? "unapproved",
    target_class: initialProfile?.target_class ?? "general",
    destructive_action: initialProfile?.destructive_action ?? false,
    path_privilege: initialProfile?.path_privilege ?? "",
    human_review_required: initialProfile?.human_review_required ?? false,
  });

  useEffect(() => {
    void getPolicyProfile(projectId, token).then((nextProfile) => {
      if (!nextProfile) {
        return;
      }
      setProfile(nextProfile);
      setNotesText(nextProfile.notes.join("\n"));
      setForm({
        environment: nextProfile.environment,
        approval_state: nextProfile.approval_state,
        target_class: nextProfile.target_class,
        destructive_action: nextProfile.destructive_action,
        path_privilege: nextProfile.path_privilege ?? "",
        human_review_required: nextProfile.human_review_required,
      });
    });
    void getPolicyProfileHistory(projectId, token).then(setHistory);
  }, [projectId, token]);

  const summary = useMemo(
    () => [
      `Env: ${form.environment}`,
      `Scope: ${form.target_class}`,
      form.destructive_action ? "Destructive enabled" : "Non-destructive default",
      form.human_review_required ? "Human review required" : "No human review gate",
    ],
    [form],
  );

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedReason = reason.trim();
    if (!trimmedReason) {
      setError("A policy-change reason is required.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const nextProfile = await updatePolicyProfile({
        project_id: projectId,
        token,
        environment: form.environment,
        approval_state: form.approval_state,
        target_class: form.target_class,
        destructive_action: form.destructive_action,
        path_privilege: form.path_privilege.trim() || null,
        human_review_required: form.human_review_required,
        notes: notesText
          .split("\n")
          .map((note) => note.trim())
          .filter(Boolean),
        reason: trimmedReason,
      });
      setProfile(nextProfile);
      setNotesText(nextProfile.notes.join("\n"));
      setReason("");
      const nextHistory = await getPolicyProfileHistory(projectId, token);
      setHistory(nextHistory);
    } catch {
      setError("Policy profile update failed. Check auth or backend availability.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <StatusPill label={form.approval_state} tone={toneForApproval(form.approval_state)} />
        <StatusPill label={form.target_class} tone="neutral" />
        <StatusPill label={form.environment} tone="neutral" />
      </div>

      <div className="rounded-[1.3rem] border border-black/6 bg-cloud/85 px-4 py-4">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Effective posture</p>
        <p className="mt-2 text-sm leading-6 text-slate/78">{summary.join(" · ")}</p>
        <p className="mt-2 text-xs text-slate/58">Last updated: {profile?.updated_at ?? "Not saved yet"}</p>
      </div>

      <form className="grid gap-4 md:grid-cols-2" onSubmit={onSubmit}>
        <label className="space-y-2">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Environment</span>
          <select
            className="w-full rounded-[1rem] border border-black/8 bg-white px-4 py-3 text-sm text-ink outline-none"
            value={form.environment}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                environment: event.target.value as PolicyProfile["environment"],
              }))
            }
          >
            <option value="dev">dev</option>
            <option value="staging">staging</option>
            <option value="prod">prod</option>
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Approval state</span>
          <select
            className="w-full rounded-[1rem] border border-black/8 bg-white px-4 py-3 text-sm text-ink outline-none"
            value={form.approval_state}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                approval_state: event.target.value as PolicyProfile["approval_state"],
              }))
            }
          >
            <option value="unapproved">unapproved</option>
            <option value="approved">approved</option>
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Target class</span>
          <select
            className="w-full rounded-[1rem] border border-black/8 bg-white px-4 py-3 text-sm text-ink outline-none"
            value={form.target_class}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                target_class: event.target.value as PolicyProfile["target_class"],
              }))
            }
          >
            <option value="general">general</option>
            <option value="security">security</option>
            <option value="production">production</option>
            <option value="infrastructure">infrastructure</option>
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Path privilege</span>
          <input
            className="w-full rounded-[1rem] border border-black/8 bg-white px-4 py-3 text-sm text-ink outline-none placeholder:text-slate/40"
            placeholder="security-approved"
            value={form.path_privilege}
            onChange={(event) => setForm((current) => ({ ...current, path_privilege: event.target.value }))}
          />
        </label>

        <label className="flex items-center gap-3 rounded-[1rem] border border-black/8 bg-white px-4 py-3 text-sm text-slate">
          <input
            type="checkbox"
            checked={form.destructive_action}
            onChange={(event) => setForm((current) => ({ ...current, destructive_action: event.target.checked }))}
          />
          Destructive actions allowed by default
        </label>

        <label className="flex items-center gap-3 rounded-[1rem] border border-black/8 bg-white px-4 py-3 text-sm text-slate">
          <input
            type="checkbox"
            checked={form.human_review_required}
            onChange={(event) => setForm((current) => ({ ...current, human_review_required: event.target.checked }))}
          />
          Require human review before dispatch
        </label>

        <label className="space-y-2 md:col-span-2">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Policy notes</span>
          <textarea
            className="min-h-32 w-full rounded-[1rem] border border-black/8 bg-white px-4 py-3 text-sm leading-6 text-ink outline-none placeholder:text-slate/40"
            placeholder="One note per line"
            value={notesText}
            onChange={(event) => setNotesText(event.target.value)}
          />
        </label>

        <label className="space-y-2 md:col-span-2">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Change reason</span>
          <textarea
            className="min-h-24 w-full rounded-[1rem] border border-black/8 bg-white px-4 py-3 text-sm leading-6 text-ink outline-none placeholder:text-slate/40"
            placeholder="Why is this policy changing? This reason is stored in the policy history."
            value={reason}
            onChange={(event) => setReason(event.target.value)}
          />
        </label>

        <div className="flex items-center justify-between gap-3 md:col-span-2">
          <div className="text-sm text-slate/68">{error ?? "Policy defaults feed the governed runtime when request-specific policy is absent."}</div>
          <button
            type="submit"
            disabled={saving}
            className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-cloud transition hover:bg-slate disabled:cursor-not-allowed disabled:opacity-60"
          >
            {saving ? "Saving..." : "Save policy profile"}
          </button>
        </div>
      </form>

      <div className="rounded-[1.3rem] border border-black/6 bg-white/90 p-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Policy feedback loop</p>
            <p className="mt-2 text-sm leading-6 text-slate/76">
              Review execution results, HITL decisions, and failures. Update policy only with explicit human judgment and a recorded reason.
            </p>
          </div>
          <StatusPill label={`${history.length} versions`} tone="neutral" />
        </div>

        <div className="mt-4 grid gap-3">
          {history.map((version) => (
            <div key={version.version_id} className="rounded-[1.1rem] border border-black/6 bg-cloud/70 px-4 py-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm font-semibold text-ink">{version.changed_by}</p>
                <p className="text-xs text-slate/58">{version.changed_at}</p>
              </div>
              <p className="mt-2 text-sm leading-6 text-slate/78">{version.reason}</p>
              <p className="mt-2 text-xs text-slate/55">
                Previous state: {version.previous_state ? "recorded" : "none"} · New state captured for future governed requests.
              </p>
            </div>
          ))}
          {history.length === 0 ? (
            <p className="rounded-[1.1rem] border border-dashed border-black/8 px-4 py-4 text-sm leading-6 text-slate/68">
              No policy history yet. The first manual change will create the initial feedback-loop record.
            </p>
          ) : null}
        </div>
      </div>
    </div>
  );
}
