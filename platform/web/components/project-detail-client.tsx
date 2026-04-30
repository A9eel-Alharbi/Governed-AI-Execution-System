"use client";

import { useEffect, useState } from "react";

import { getApprovals, getGovernedRequests, getPolicyProfile, getProjectBySlug, getRuns } from "../lib/platform-api";
import type { ApprovalSummary, GovernedRequestSummary, PolicyProfile, ProjectSummary, RunResponse, RunSummary } from "../lib/sample-data";
import { ApprovalListClient } from "./approval-list-client";
import { GovernedRequestListClient } from "./governed-request-list-client";
import { useAuth } from "./auth-provider";
import { PolicyProfileClient } from "./policy-profile-client";
import { ProjectConnectionClient } from "./project-connection-client";
import { RequestConsole } from "./request-console";
import { RunHistoryClient } from "./run-history-client";
import { SectionCard } from "./section-card";
import { StatusPill } from "./status-pill";

function vaultTone(status?: string) {
  if (status === "healthy") return "success" as const;
  if (status === "review") return "warning" as const;
  if (status === "degraded") return "danger" as const;
  return "neutral" as const;
}

function workPackageHint(project: ProjectSummary) {
  if (project.session_loader) {
    return `Session loader configured at ${project.session_loader}. This is the current work-package execution entrypoint.`;
  }
  return "No session loader is connected yet, so work-package review and execution remain unbound.";
}

function validationHint(project: ProjectSummary) {
  if (project.repository_root) {
    return "Validation runs are expected to use the governed repo validator from the connected repository root.";
  }
  return "Repository root is not connected yet, so validation review is still incomplete.";
}

function changeControlHint(project: ProjectSummary) {
  if (project.policy_artifact && project.vault_health_status) {
    return "Constraint changes should route through CCR and vault-health review before higher-risk execution.";
  }
  return "Change-control posture is not fully configured yet.";
}

export function ProjectDetailClient({
  slug,
  initialProject,
  initialRunResponse,
  initialRuns,
  initialApprovals,
  initialPolicyProfile,
  initialRequests,
}: {
  slug: string;
  initialProject: ProjectSummary | null;
  initialRunResponse: RunResponse;
  initialRuns: RunSummary[];
  initialApprovals: ApprovalSummary[];
  initialPolicyProfile: PolicyProfile | null;
  initialRequests: GovernedRequestSummary[];
}) {
  const [project, setProject] = useState<ProjectSummary | null>(initialProject);
  const [runs, setRuns] = useState<RunSummary[]>(initialRuns);
  const [approvals, setApprovals] = useState<ApprovalSummary[]>(initialApprovals);
  const [policyProfile, setPolicyProfile] = useState<PolicyProfile | null>(initialPolicyProfile);
  const [requests, setRequests] = useState<GovernedRequestSummary[]>(initialRequests);
  const { token } = useAuth();

  useEffect(() => {
    void getProjectBySlug(slug, token).then(setProject);
  }, [slug, token]);

  useEffect(() => {
    if (!project) {
      return;
    }
    void getRuns({ token, project_id: project.project_id }).then(setRuns);
    void getApprovals({ token, project_id: project.project_id }).then(setApprovals);
    void getPolicyProfile(project.project_id, token).then(setPolicyProfile);
    void getGovernedRequests({ token, project_id: project.project_id }).then(setRequests);
  }, [token, project]);

  if (!project) {
    return (
      <main className="min-h-screen px-4 py-6 md:px-6">
        <div className="mx-auto max-w-6xl rounded-[2rem] border border-black/8 bg-white/72 px-6 py-8 shadow-[0_25px_70px_rgba(15,29,38,0.08)] backdrop-blur">
          <p className="text-lg text-slate/76">Project not found or access denied.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-4 py-6 md:px-6">
      <div className="mx-auto max-w-6xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-[2rem] border border-black/8 bg-white/72 px-6 py-5 shadow-[0_25px_70px_rgba(15,29,38,0.08)] backdrop-blur">
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate/55">Project detail</p>
            <h1 className="font-display text-4xl text-ink">{project.name}</h1>
            <p className="mt-2 text-sm text-slate/72">{project.repository_url}</p>
          </div>
          <div className="flex items-center gap-3">
            <StatusPill label={project.status} tone={vaultTone(project.status)} />
            <a href="/workspace" className="rounded-full border border-slate/12 bg-white px-4 py-2 text-sm font-semibold text-slate">
              Back to workspace
            </a>
          </div>
        </div>

        <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
          <SectionCard eyebrow="Governed request" title="Run a project-specific request">
            <RequestConsole
              project={project}
              initialResponse={{
                ...initialRunResponse,
                project,
              }}
            />
          </SectionCard>

          <SectionCard eyebrow="Governance state" title="Project context">
            <div className="space-y-3">
              <div className="rounded-[1.3rem] border border-black/6 bg-cloud/85 px-4 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Policy artifact</p>
                <p className="mt-2 text-sm leading-6 text-slate/78">{project.policy_artifact ?? "Not set yet"}</p>
              </div>
              <div className="rounded-[1.3rem] border border-black/6 bg-cloud/85 px-4 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Effective policy profile</p>
                <p className="mt-2 text-sm leading-6 text-slate/78">
                  {policyProfile
                    ? `${policyProfile.environment} · ${policyProfile.target_class} · ${policyProfile.approval_state}`
                    : "No platform policy profile saved yet."}
                </p>
              </div>
              <div className="rounded-[1.3rem] border border-black/6 bg-cloud/85 px-4 py-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Vault health</p>
                  <StatusPill label={project.vault_health_status ?? "pending"} tone={vaultTone(project.vault_health_status)} />
                </div>
                <p className="mt-2 text-sm leading-6 text-slate/78">Threat model: {project.threat_model_document ?? "Not set yet"}</p>
              </div>
              <div className="rounded-[1.3rem] border border-black/6 bg-cloud/85 px-4 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Approvals in force</p>
                <p className="mt-2 text-sm leading-6 text-slate/78">
                  {project.approvals_in_force && project.approvals_in_force.length > 0
                    ? project.approvals_in_force.join(", ")
                    : "No active approval artifacts."}
                </p>
              </div>
              <div className="rounded-[1.3rem] border border-black/6 bg-cloud/85 px-4 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Default context</p>
                <pre className="mt-2 overflow-x-auto text-xs leading-6 text-slate/78">
                  {JSON.stringify(project.default_context ?? {}, null, 2)}
                </pre>
              </div>
            </div>
          </SectionCard>
        </div>

        <SectionCard eyebrow="Repo connection" title="Repository and governed artifact mapping">
          <ProjectConnectionClient project={project} onProjectUpdated={setProject} />
        </SectionCard>

        <SectionCard eyebrow="Governed artifacts" title="Work package, validation, and change-control review">
          <div className="grid gap-4 lg:grid-cols-3">
            <div className="rounded-[1.3rem] border border-black/6 bg-cloud/85 px-4 py-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Work package surface</p>
              <p className="mt-2 text-sm leading-6 text-slate/78">{workPackageHint(project)}</p>
            </div>
            <div className="rounded-[1.3rem] border border-black/6 bg-cloud/85 px-4 py-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Validation review</p>
              <p className="mt-2 text-sm leading-6 text-slate/78">{validationHint(project)}</p>
            </div>
            <div className="rounded-[1.3rem] border border-black/6 bg-cloud/85 px-4 py-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Change control</p>
              <p className="mt-2 text-sm leading-6 text-slate/78">{changeControlHint(project)}</p>
            </div>
          </div>
        </SectionCard>

        <SectionCard eyebrow="Run history" title="Project-specific runs">
          <RunHistoryClient projectId={project.project_id} initialRuns={runs} />
        </SectionCard>

        <SectionCard eyebrow="HITL gate" title="Pending and completed governed requests">
          <GovernedRequestListClient projectId={project.project_id} initialRequests={requests} />
        </SectionCard>

        <SectionCard eyebrow="Approval records" title="Approval management">
          <ApprovalListClient projectId={project.project_id} initialApprovals={approvals} />
        </SectionCard>

        <SectionCard eyebrow="Policy profile" title="Execution posture defaults">
          <PolicyProfileClient projectId={project.project_id} initialProfile={policyProfile} />
        </SectionCard>
      </div>
    </main>
  );
}
