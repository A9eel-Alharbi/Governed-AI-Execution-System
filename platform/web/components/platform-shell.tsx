import { RequestConsole } from "./request-console";
import { AuthPanel } from "./auth-panel";
import { GovernedRequestListClient } from "./governed-request-list-client";
import { ProjectCreateForm } from "./project-create-form";
import { ProjectLinkCard } from "./project-link-card";
import { RunHistoryClient } from "./run-history-client";
import { SectionCard } from "./section-card";
import { StatusPill } from "./status-pill";
import type { DashboardSummary, GovernedRequestSummary, ProjectSummary, RunResponse, RunSummary } from "../lib/sample-data";

const navGroups = [
  {
    label: "Workspace",
    items: [
      { name: "Projects", active: true },
      { name: "Requests" },
      { name: "Runs" },
      { name: "Reports" },
    ],
  },
  {
    label: "Governance",
    items: [
      { name: "Policies" },
      { name: "Approvals" },
      { name: "Work Packages" },
      { name: "Change Control" },
    ],
  },
];

const queue = [
  {
    request: "Create a follow-up work package for revenue reporting",
    outcome: "dispatch",
    owner: "A9eel",
  },
  {
    request: "Modify production secrets for billing webhook",
    outcome: "escalate",
    owner: "Security Lead",
  },
  {
    request: "Update vision constraints for memberships",
    outcome: "clarify",
    owner: "Product Owner",
  },
];

const runTimeline = [
  {
    id: "RUN-1042",
    step: "Interpretation completed",
    detail: "Case classified into `implementation.run_wp` with governed dispatch.",
  },
  {
    id: "RUN-1042",
    step: "Policy applied",
    detail: "Repo policy profile and approval overlay resolved to production-safe scope.",
  },
  {
    id: "RUN-1042",
    step: "Execution staged",
    detail: "Session loader, vault health, and work package passed preflight checks.",
  },
];

function describeProject(project: ProjectSummary) {
  if (project.status === "active") {
    return "Governed request flows and runtime paths are available for this repository.";
  }
  if (project.status === "connected") {
    return "Repository is connected. Project definition and first governed work package are the next steps.";
  }
  if (project.status === "blocked") {
    return "Project is blocked pending governance or approval resolution.";
  }
  return "Project is still in draft mode and has not completed its repo-backed setup.";
}

function toneForHealth(status?: string) {
  if (status === "healthy") return "success" as const;
  if (status === "review") return "warning" as const;
  if (status === "degraded") return "danger" as const;
  return "neutral" as const;
}

export function PlatformShell({
  projects,
  initialRunResponse,
  initialRuns,
  summary,
  initialRequests,
}: {
  projects: ProjectSummary[];
  initialRunResponse: RunResponse;
  initialRuns: RunSummary[];
  summary: DashboardSummary;
  initialRequests: GovernedRequestSummary[];
}) {
  const selectedProject = projects[0] ?? initialRunResponse.project;
  const activeOutcome = Object.entries(summary.outcome_counts).sort((left, right) => right[1] - left[1])[0];
  const rightDrawerSections = [
    {
      title: "Policy profile",
      value: selectedProject.policy_artifact ?? "Not configured yet",
      note: "Project-level policy artifact used to seed governed interpretation and execution context.",
    },
    {
      title: "Approvals in force",
      value:
        selectedProject.approvals_in_force && selectedProject.approvals_in_force.length > 0
          ? selectedProject.approvals_in_force.join(", ")
          : "No active approvals",
      note: "Approval artifacts constrain which higher-risk paths can dispatch without escalation.",
    },
    {
      title: "Vault health",
      value: selectedProject.vault_health_status ?? "pending",
      note: selectedProject.threat_model_document
        ? `Threat model tracked at ${selectedProject.threat_model_document}.`
        : "Threat model and vault-health artifact still need to be defined for this project.",
    },
  ];

  return (
    <main className="min-h-screen px-4 py-4 md:px-6">
      <div className="grid min-h-[calc(100vh-2rem)] grid-cols-1 gap-4 xl:grid-cols-[280px_minmax(0,1fr)_340px]">
        <aside className="rounded-[2rem] border border-black/8 bg-ink px-5 py-6 text-cloud shadow-[0_30px_80px_rgba(15,29,38,0.22)]">
          <div className="mb-8">
            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.24em] text-sage/80">AOS/CDD Platform</p>
            <h1 className="font-display text-3xl leading-tight">Governed delivery for request-to-repo work</h1>
          </div>

          <div className="mb-8 rounded-[1.4rem] border border-white/10 bg-white/5 p-4">
            <p className="mb-2 text-xs uppercase tracking-[0.2em] text-sage/70">Current workspace</p>
            <p className="text-lg font-semibold">Agent Control Stack</p>
            <p className="mt-2 text-sm leading-6 text-cloud/68">Website surface for approvals, work packages, runs, and repo-connected execution.</p>
          </div>

          <div className="mb-8">
            <AuthPanel />
          </div>

          <nav className="space-y-6">
            {navGroups.map((group) => (
              <div key={group.label}>
                <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-sage/65">{group.label}</p>
                <div className="space-y-1.5">
                  {group.items.map((item) => (
                    <button
                      key={item.name}
                      className={`flex w-full items-center justify-between rounded-2xl px-4 py-3 text-left text-sm transition ${
                        item.active
                          ? "bg-moss text-cloud shadow-[inset_0_0_0_1px_rgba(255,255,255,0.06)]"
                          : "text-cloud/76 hover:bg-white/6 hover:text-white"
                      }`}
                    >
                      <span>{item.name}</span>
                      {item.active ? <span className="h-2.5 w-2.5 rounded-full bg-amber" /> : null}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </nav>

          <div className="mt-8 rounded-[1.4rem] border border-amber/20 bg-amber/10 p-4 text-sm leading-6 text-cloud/80">
            <p className="mb-2 font-semibold text-parchment">Design direction</p>
            <p>Ink, moss, parchment, and ember reflect control, review, repo history, and operational caution without using generic SaaS purple.</p>
          </div>
        </aside>

        <div className="space-y-4">
          <section className="rounded-[2rem] border border-black/8 bg-white/72 p-6 shadow-[0_25px_70px_rgba(15,29,38,0.08)] backdrop-blur">
            <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-ember">Operating surface</p>
                <h2 className="font-display text-4xl leading-tight text-ink">Supabase-style control room for governed agent execution</h2>
              </div>
              <div className="rounded-full border border-moss/15 bg-moss px-4 py-2 text-sm font-semibold text-cloud">
                Website {"->"} API {"->"} Control {"->"} AOS/CDD {"->"} Executor
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="rounded-[1.6rem] border border-slate/10 bg-parchment p-5">
                <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate/60">Request console</p>
                <RequestConsole project={selectedProject} initialResponse={initialRunResponse} />
              </div>

              <div className="grid gap-4">
                <div className="rounded-[1.6rem] border border-black/8 bg-white p-5">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate/55">Policy-critical paths</p>
                  <p className="text-4xl font-bold text-ink">{summary.policy_critical_paths}</p>
                  <p className="mt-2 text-sm text-slate/72">Approved security, production, and infrastructure scopes currently tracked by the platform.</p>
                </div>
                <div className="rounded-[1.6rem] border border-black/8 bg-white p-5">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate/55">Platform posture</p>
                  <p className="text-lg font-semibold text-ink">
                    {summary.projects_with_repo_connections}/{summary.total_projects} repos connected
                  </p>
                  <p className="mt-2 text-sm text-slate/72">
                    {summary.policy_profiles_configured} policy profiles configured and {summary.approvals_approved}/{summary.approvals_total} approvals currently approved.
                  </p>
                </div>
              </div>
            </div>
          </section>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-[1.6rem] border border-black/8 bg-white p-5">
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate/55">Projects</p>
              <p className="text-4xl font-bold text-ink">{summary.total_projects}</p>
              <p className="mt-2 text-sm text-slate/72">
                {summary.active_projects} active · {summary.connected_projects} connected · {summary.blocked_projects} blocked
              </p>
            </div>
            <div className="rounded-[1.6rem] border border-black/8 bg-white p-5">
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate/55">Runs</p>
              <p className="text-4xl font-bold text-ink">{summary.runs_total}</p>
              <p className="mt-2 text-sm text-slate/72">
                {activeOutcome ? `Most common outcome: ${activeOutcome[0]} (${activeOutcome[1]})` : "No governed runs yet."}
              </p>
            </div>
            <div className="rounded-[1.6rem] border border-black/8 bg-white p-5">
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate/55">Approvals</p>
              <p className="text-4xl font-bold text-ink">{summary.approvals_total}</p>
              <p className="mt-2 text-sm text-slate/72">{summary.approvals_approved} approved for higher-risk execution paths.</p>
            </div>
            <div className="rounded-[1.6rem] border border-black/8 bg-white p-5">
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate/55">Policy profiles</p>
              <p className="text-4xl font-bold text-ink">{summary.policy_profiles_configured}</p>
              <p className="mt-2 text-sm text-slate/72">Projects with a saved execution posture on the platform.</p>
            </div>
          </div>

          <div className="grid gap-4 2xl:grid-cols-[1.05fr_0.95fr]">
            <SectionCard eyebrow="Connected projects" title="Projects under governance">
              <div className="space-y-4">
                <ProjectCreateForm />
                {projects.map((project) => (
                  <ProjectLinkCard key={project.project_id} project={project} description={describeProject(project)} />
                ))}
              </div>
            </SectionCard>

            <SectionCard eyebrow="Run history" title="Recent governed runs" action={<StatusPill label="policy-aware" tone="success" />}>
              <RunHistoryClient initialRuns={initialRuns} />
            </SectionCard>
          </div>

          <SectionCard eyebrow="HITL queue" title="Requests awaiting human judgment">
            <GovernedRequestListClient initialRequests={initialRequests} />
          </SectionCard>

          <SectionCard eyebrow="Execution journal" title="Current governed run" tone="dark">
            <div className="space-y-4">
              {runTimeline.map((entry, index) => (
                <div key={`${entry.id}-${entry.step}`} className="grid gap-3 md:grid-cols-[84px_minmax(0,1fr)]">
                  <div className="relative pl-6 text-sm text-sage/80">
                    <span className="absolute left-0 top-1 h-3 w-3 rounded-full bg-amber" />
                    {index !== runTimeline.length - 1 ? <span className="absolute left-[5px] top-5 h-[calc(100%+8px)] w-px bg-white/14" /> : null}
                    {entry.id}
                  </div>
                  <div className="rounded-[1.4rem] border border-white/8 bg-white/6 px-4 py-4">
                    <p className="font-semibold text-cloud">{entry.step}</p>
                    <p className="mt-2 text-sm leading-6 text-cloud/74">{entry.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>

        <aside className="rounded-[2rem] border border-black/8 bg-white/76 p-5 shadow-[0_24px_70px_rgba(15,29,38,0.08)] backdrop-blur">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate/55">Governance drawer</p>
              <h2 className="font-display text-2xl text-ink">Policy and approval context</h2>
            </div>
            <StatusPill label={selectedProject.vault_health_status ?? "pending"} tone={toneForHealth(selectedProject.vault_health_status)} />
          </div>

          <div className="mb-5 rounded-[1.5rem] border border-black/6 bg-parchment p-4">
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate/58">Selected project</p>
            <p className="font-semibold text-ink">{selectedProject.name}</p>
            <p className="mt-2 text-sm leading-7 text-slate/82">{selectedProject.repository_url}</p>
          </div>

          <div className="space-y-3">
            {rightDrawerSections.map((section) => (
              <div key={section.title} className="rounded-[1.4rem] border border-black/6 bg-cloud/85 px-4 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">{section.title}</p>
                <p className="mt-2 text-lg font-semibold text-ink">{section.value}</p>
                <p className="mt-2 text-sm leading-6 text-slate/72">{section.note}</p>
              </div>
            ))}
          </div>

          <div className="mt-5 rounded-[1.5rem] border border-ember/15 bg-blush p-4">
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-ember">Why this palette</p>
            <p className="text-sm leading-6 text-slate/78">
              Ink and slate communicate control and auditability. Moss signals safe approval paths. Ember and amber
              mark escalation and review without relying on generic neon dashboards.
            </p>
          </div>
        </aside>
      </div>
    </main>
  );
}
