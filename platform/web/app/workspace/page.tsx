import { WorkspaceClient } from "../../components/workspace-client";
import { sampleDashboardSummary, sampleGovernedRequests, sampleProjects, sampleRunResponse, sampleRuns } from "../../lib/sample-data";

export default function WorkspacePage() {
  return (
    <WorkspaceClient
      initialProjects={sampleProjects}
      initialRunResponse={sampleRunResponse}
      initialRuns={sampleRuns}
      initialSummary={sampleDashboardSummary}
      initialRequests={sampleGovernedRequests}
    />
  );
}
