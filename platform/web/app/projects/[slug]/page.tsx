import { ProjectDetailClient } from "../../../components/project-detail-client";
import { sampleApprovals, sampleGovernedRequests, samplePolicyProfiles, sampleProjects, sampleRunResponse, sampleRuns } from "../../../lib/sample-data";

export default async function ProjectDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const initialProject = sampleProjects.find((project) => project.slug === slug) ?? null;
  const initialRuns = initialProject ? sampleRuns.filter((run) => run.project_id === initialProject.project_id) : [];
  const initialApprovals = initialProject ? sampleApprovals.filter((approval) => approval.project_id === initialProject.project_id) : [];
  const initialPolicyProfile = initialProject ? samplePolicyProfiles[initialProject.project_id] ?? null : null;
  const initialRequests = initialProject ? sampleGovernedRequests.filter((request) => request.project_id === initialProject.project_id) : [];

  return (
    <ProjectDetailClient
      slug={slug}
      initialProject={initialProject}
      initialRunResponse={sampleRunResponse}
      initialRuns={initialRuns}
      initialApprovals={initialApprovals}
      initialPolicyProfile={initialPolicyProfile}
      initialRequests={initialRequests}
    />
  );
}
