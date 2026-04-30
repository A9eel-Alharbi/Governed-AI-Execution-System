import Link from "next/link";

const capabilityRows = [
  {
    label: "Interpretation control",
    detail: "Requests are restored, normalized, classified, policy-checked, and forced into clarify, refuse, dispatch, or escalate.",
  },
  {
    label: "Governed execution",
    detail: "Approved work moves through constraints, work packages, session loaders, approvals, validation, and change control.",
  },
  {
    label: "Human approval",
    detail: "Dispatchable work pauses in a HITL gate before execution. A person approves, rejects, or escalates it.",
  },
  {
    label: "Dry-run discipline",
    detail: "Dry-run executes the full logic path without side effects. Write actions are explicit and skipped by contract.",
  },
  {
    label: "Failure clarity",
    detail: "Execution failures are recorded with traces, partial artifacts, and a resubmit path instead of silent retries.",
  },
  {
    label: "Policy feedback",
    detail: "Humans revise policy through versioned history with author, reason, timestamp, and previous/new state tracking.",
  },
];

const flow = [
  "User creates a project and connects a repo.",
  "Project policy, approvals, threat model, and governed artifact paths are stored.",
  "A request enters the control layer and gets classified.",
  "Dispatchable requests stop at the HITL gate.",
  "Approved requests execute through AOS/CDD with dry-run or live mode.",
  "Runs, failures, and policy decisions feed the audit and feedback loop.",
];

const useCases = [
  "AI coding agents that should not act on ambiguous or unsafe requests.",
  "Internal engineering portals where requests become governed repo work.",
  "Security-sensitive delivery flows that need approvals before execution.",
  "Multi-project platforms that want a repo-backed source of truth with a clean UI surface.",
];

export default function HomePage() {
  return (
    <main className="min-h-screen px-4 py-4 md:px-6">
      <div className="mx-auto max-w-[1500px] space-y-4">
        <section className="rounded-[2rem] border border-black/8 bg-white/76 px-6 py-6 shadow-[0_25px_70px_rgba(15,29,38,0.08)] backdrop-blur md:px-8 md:py-8">
          <div className="flex flex-col gap-10 xl:flex-row xl:items-start xl:justify-between">
            <div className="max-w-4xl">
              <p className="mb-3 text-xs font-semibold uppercase tracking-[0.24em] text-ember">AOS/CDD Platform</p>
              <h1 className="font-display text-5xl leading-[0.95] text-ink md:text-7xl">
                Governed AI software delivery
                <span className="block text-moss">from request to repo</span>
              </h1>
              <p className="mt-6 max-w-3xl text-lg leading-8 text-slate/80 md:text-xl">
                A hosted control room for turning raw requests into bounded, auditable software work. The platform
                sits in front of an executor, enforces approvals and policy, and routes work into repo-backed AOS/CDD
                workflows instead of letting an LLM improvise end to end.
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                <Link
                  href="/workspace"
                  className="rounded-full bg-ink px-6 py-3 text-sm font-semibold text-cloud transition hover:bg-slate"
                >
                  Open workspace
                </Link>
                <a
                  href="#how-it-works"
                  className="rounded-full border border-slate/12 bg-white px-6 py-3 text-sm font-semibold text-slate transition hover:border-moss/30 hover:text-moss"
                >
                  See how it works
                </a>
              </div>

              <div className="mt-10 grid gap-4 md:grid-cols-3">
                <div className="rounded-[1.5rem] border border-black/6 bg-parchment px-4 py-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Control outcome</p>
                  <p className="mt-2 text-2xl font-semibold text-ink">Clarify · Refuse · Dispatch · Escalate</p>
                </div>
                <div className="rounded-[1.5rem] border border-black/6 bg-cloud/80 px-4 py-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate/55">Execution posture</p>
                  <p className="mt-2 text-2xl font-semibold text-ink">HITL, dry-run, policy, rollback visibility</p>
                </div>
                <div className="rounded-[1.5rem] border border-black/6 bg-blush px-4 py-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ember">Source of truth</p>
                  <p className="mt-2 text-2xl font-semibold text-ink">Repo artifacts stay governed</p>
                </div>
              </div>
            </div>

            <div className="w-full max-w-[420px] rounded-[1.9rem] border border-black/8 bg-ink p-5 text-cloud shadow-[0_30px_80px_rgba(15,29,38,0.24)]">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sage/75">System stack</p>
              <div className="mt-4 space-y-3">
                {[
                  "Website UI",
                  "Platform API",
                  "Interpretation / control layer",
                  "AOS/CDD governed execution",
                  "Executor / model layer",
                  "Persistence and ops layer",
                ].map((layer, index) => (
                  <div key={layer} className="rounded-[1.2rem] border border-white/8 bg-white/6 px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.18em] text-sage/70">Layer {index + 1}</p>
                    <p className="mt-1 text-base font-semibold">{layer}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
          <div className="rounded-[2rem] border border-black/8 bg-white/76 p-6 shadow-[0_24px_70px_rgba(15,29,38,0.08)] backdrop-blur">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-ember">How it works</p>
            <h2 className="mt-3 font-display text-4xl leading-tight text-ink">The model is the bounded executor, not the controller</h2>
            <div className="mt-6 space-y-4">
              {flow.map((step, index) => (
                <div key={step} className="grid gap-3 md:grid-cols-[72px_minmax(0,1fr)]">
                  <div className="rounded-full border border-moss/15 bg-moss px-3 py-2 text-center text-sm font-semibold text-cloud">
                    {String(index + 1).padStart(2, "0")}
                  </div>
                  <div className="rounded-[1.4rem] border border-black/6 bg-cloud/80 px-4 py-4 text-sm leading-7 text-slate/78">
                    {step}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[2rem] border border-black/8 bg-white/76 p-6 shadow-[0_24px_70px_rgba(15,29,38,0.08)] backdrop-blur">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-ember">Core capabilities</p>
            <div className="mt-4 divide-y divide-black/6">
              {capabilityRows.map((row) => (
                <div key={row.label} className="grid gap-3 py-4 md:grid-cols-[220px_minmax(0,1fr)]">
                  <p className="text-sm font-semibold text-ink">{row.label}</p>
                  <p className="text-sm leading-7 text-slate/78">{row.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-[2rem] border border-black/8 bg-ink p-6 text-cloud shadow-[0_30px_80px_rgba(15,29,38,0.22)]">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sage/75">What the UI shows</p>
            <h2 className="mt-3 font-display text-4xl leading-tight">A control room, not a chat wrapper</h2>
            <div className="mt-6 grid gap-3">
              {[
                "Projects and repo connections",
                "Policy profiles and version history",
                "Approvals in force",
                "Governed request queue",
                "Run history and failure traces",
                "Threat model and vault-health posture",
              ].map((item) => (
                <div key={item} className="rounded-[1.3rem] border border-white/8 bg-white/6 px-4 py-4 text-sm leading-6 text-cloud/84">
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[2rem] border border-black/8 bg-white/76 p-6 shadow-[0_24px_70px_rgba(15,29,38,0.08)] backdrop-blur">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-ember">Use cases</p>
            <h2 className="mt-3 font-display text-4xl leading-tight text-ink">Where this actually helps</h2>
            <div className="mt-6 grid gap-3 md:grid-cols-2">
              {useCases.map((item) => (
                <div key={item} className="rounded-[1.4rem] border border-black/6 bg-parchment px-4 py-4 text-sm leading-7 text-slate/78">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="rounded-[2rem] border border-black/8 bg-white/76 px-6 py-6 shadow-[0_24px_70px_rgba(15,29,38,0.08)] backdrop-blur md:px-8">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-3xl">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-ember">Product idea</p>
              <h2 className="mt-3 font-display text-4xl leading-tight text-ink">Human judgment stays on the control surface</h2>
              <p className="mt-4 text-base leading-8 text-slate/78">
                The platform provides structure, traces, approvals, policy history, and governed execution paths. It
                does not invent approval decisions, mutate policy autonomously, or silently write to a repo during a dry-run.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link
                href="/workspace"
                className="rounded-full bg-moss px-6 py-3 text-sm font-semibold text-cloud transition hover:bg-[#284d43]"
              >
                Enter workspace
              </Link>
              <a
                href="https://github.com/A9eel-Alharbi/AOS-CDD"
                className="rounded-full border border-slate/12 bg-white px-6 py-3 text-sm font-semibold text-slate transition hover:border-ember/30 hover:text-ember"
              >
                View repo
              </a>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
