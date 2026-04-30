"use client";

import { useState, useTransition } from "react";

import { updateProjectConnection } from "../lib/platform-api";
import type { ProjectSummary } from "../lib/sample-data";
import { useAuth } from "./auth-provider";

export function ProjectConnectionClient({
  project,
  onProjectUpdated,
}: {
  project: ProjectSummary;
  onProjectUpdated: (project: ProjectSummary) => void;
}) {
  const { token } = useAuth();
  const [isPending, startTransition] = useTransition();
  const [message, setMessage] = useState<string | null>(null);
  const [form, setForm] = useState({
    repository_url: project.repository_url,
    default_branch: project.default_branch,
    repository_root: project.repository_root ?? "",
    session_loader: project.session_loader ?? "",
    policy_artifact: project.policy_artifact ?? "",
    threat_model_document: project.threat_model_document ?? "",
    status: project.status,
  });

  function submit() {
    startTransition(async () => {
      try {
        const updated = await updateProjectConnection({
          project_id: project.project_id,
          token,
          repository_url: form.repository_url,
          default_branch: form.default_branch,
          repository_root: form.repository_root || undefined,
          session_loader: form.session_loader || undefined,
          policy_artifact: form.policy_artifact || undefined,
          threat_model_document: form.threat_model_document || undefined,
          status: form.status,
        });
        onProjectUpdated(updated);
        setMessage("Repository connection settings saved.");
      } catch {
        setMessage("Repository connection update failed.");
      }
    });
  }

  return (
    <div className="space-y-3">
      <div className="grid gap-3 md:grid-cols-2">
        <input
          value={form.repository_url}
          onChange={(event) => setForm((current) => ({ ...current, repository_url: event.target.value }))}
          placeholder="Repository URL"
          className="w-full rounded-2xl border border-slate/12 bg-white px-4 py-3 text-sm outline-none focus:border-moss/40"
        />
        <input
          value={form.default_branch}
          onChange={(event) => setForm((current) => ({ ...current, default_branch: event.target.value }))}
          placeholder="main"
          className="w-full rounded-2xl border border-slate/12 bg-white px-4 py-3 text-sm outline-none focus:border-moss/40"
        />
        <input
          value={form.repository_root}
          onChange={(event) => setForm((current) => ({ ...current, repository_root: event.target.value }))}
          placeholder="Local repository root"
          className="w-full rounded-2xl border border-slate/12 bg-white px-4 py-3 text-sm outline-none focus:border-moss/40"
        />
        <select
          value={form.status}
          onChange={(event) =>
            setForm((current) => ({
              ...current,
              status: event.target.value as ProjectSummary["status"],
            }))
          }
          className="w-full rounded-2xl border border-slate/12 bg-white px-4 py-3 text-sm outline-none focus:border-moss/40"
        >
          <option value="draft">draft</option>
          <option value="connected">connected</option>
          <option value="active">active</option>
          <option value="blocked">blocked</option>
        </select>
        <input
          value={form.session_loader}
          onChange={(event) => setForm((current) => ({ ...current, session_loader: event.target.value }))}
          placeholder="examples/.../session-WP-001.yaml"
          className="w-full rounded-2xl border border-slate/12 bg-white px-4 py-3 text-sm outline-none focus:border-moss/40 md:col-span-2"
        />
        <input
          value={form.policy_artifact}
          onChange={(event) => setForm((current) => ({ ...current, policy_artifact: event.target.value }))}
          placeholder="examples/.../ops/policy-profile.yaml"
          className="w-full rounded-2xl border border-slate/12 bg-white px-4 py-3 text-sm outline-none focus:border-moss/40"
        />
        <input
          value={form.threat_model_document}
          onChange={(event) => setForm((current) => ({ ...current, threat_model_document: event.target.value }))}
          placeholder="examples/.../ops/security-threat-model.md"
          className="w-full rounded-2xl border border-slate/12 bg-white px-4 py-3 text-sm outline-none focus:border-moss/40"
        />
      </div>
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-slate/72">
          Connect the repo, point the platform at the session loader, and keep policy/threat-model references aligned with the governed runtime.
        </p>
        <button
          onClick={submit}
          disabled={isPending || !form.repository_url}
          className="rounded-full bg-ink px-4 py-2 text-sm font-semibold text-cloud disabled:opacity-50"
        >
          {isPending ? "Saving..." : "Save connection"}
        </button>
      </div>
      {message ? <p className="text-sm text-slate/72">{message}</p> : null}
    </div>
  );
}
