import Link from "next/link";

import type { ProjectSummary } from "../lib/sample-data";
import { StatusPill } from "./status-pill";

function toneForProject(status: ProjectSummary["status"]) {
  if (status === "active") return "success" as const;
  if (status === "connected") return "neutral" as const;
  if (status === "blocked") return "danger" as const;
  return "neutral" as const;
}

export function ProjectLinkCard({ project, description }: { project: ProjectSummary; description: string }) {
  return (
    <Link href={`/projects/${project.slug}`} className="block rounded-[1.4rem] border border-black/6 bg-cloud/85 px-4 py-4 transition hover:border-moss/30 hover:bg-white">
      <div className="mb-2 flex items-center justify-between gap-3">
        <div>
          <p className="font-semibold text-ink">{project.name}</p>
          <p className="text-sm text-slate/70">{project.repository_url}</p>
        </div>
        <StatusPill label={project.status} tone={toneForProject(project.status)} />
      </div>
      <p className="text-sm leading-6 text-slate/78">{description}</p>
    </Link>
  );
}
