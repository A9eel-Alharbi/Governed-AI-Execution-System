"use client";

import { useState, useTransition } from "react";

import { createProject } from "../lib/platform-api";
import { useAuth } from "./auth-provider";

export function ProjectCreateForm() {
  const [name, setName] = useState("");
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [repositoryRoot, setRepositoryRoot] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const { token } = useAuth();

  function submit() {
    startTransition(async () => {
      try {
        const project = await createProject({
          name,
          repository_url: repositoryUrl,
          repository_root: repositoryRoot || undefined,
          token,
        });
        setMessage(`Created project ${project.name}. Refresh or open its detail page to continue.`);
        setName("");
        setRepositoryUrl("");
        setRepositoryRoot("");
      } catch {
        setMessage("Project creation failed. Check the platform API and try again.");
      }
    });
  }

  return (
    <div className="rounded-[1.4rem] border border-black/6 bg-cloud/85 p-4">
      <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Create project</p>
      <div className="space-y-3">
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Gym Revenue SaaS"
          className="w-full rounded-2xl border border-slate/12 bg-white px-4 py-3 text-sm outline-none focus:border-moss/40"
        />
        <input
          value={repositoryUrl}
          onChange={(event) => setRepositoryUrl(event.target.value)}
          placeholder="https://github.com/acme/gym-saas"
          className="w-full rounded-2xl border border-slate/12 bg-white px-4 py-3 text-sm outline-none focus:border-moss/40"
        />
        <input
          value={repositoryRoot}
          onChange={(event) => setRepositoryRoot(event.target.value)}
          placeholder="Optional local repository root"
          className="w-full rounded-2xl border border-slate/12 bg-white px-4 py-3 text-sm outline-none focus:border-moss/40"
        />
      </div>
      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={submit}
          disabled={isPending || !name || !repositoryUrl}
          className="rounded-full bg-ink px-4 py-2 text-sm font-semibold text-cloud disabled:opacity-50"
        >
          {isPending ? "Creating..." : "Create project"}
        </button>
        {message ? <p className="text-sm text-slate/72">{message}</p> : null}
      </div>
    </div>
  );
}
