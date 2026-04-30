"use client";

import { useEffect, useState } from "react";

import { getDashboardSummary, getGovernedRequests, getProjects, getRuns } from "../lib/platform-api";
import type { DashboardSummary, GovernedRequestSummary, ProjectSummary, RunResponse, RunSummary } from "../lib/sample-data";
import { useAuth } from "./auth-provider";
import { PlatformShell } from "./platform-shell";

export function WorkspaceClient({
  initialProjects,
  initialRunResponse,
  initialRuns,
  initialSummary,
  initialRequests,
}: {
  initialProjects: ProjectSummary[];
  initialRunResponse: RunResponse;
  initialRuns: RunSummary[];
  initialSummary: DashboardSummary;
  initialRequests: GovernedRequestSummary[];
}) {
  const [projects, setProjects] = useState<ProjectSummary[]>(initialProjects);
  const [runs, setRuns] = useState<RunSummary[]>(initialRuns);
  const [summary, setSummary] = useState<DashboardSummary>(initialSummary);
  const [requests, setRequests] = useState<GovernedRequestSummary[]>(initialRequests);
  const { token } = useAuth();

  useEffect(() => {
    void getProjects(token).then(setProjects);
    void getRuns({ token }).then(setRuns);
    void getDashboardSummary(token).then(setSummary);
    void getGovernedRequests({ token }).then(setRequests);
  }, [token]);

  return <PlatformShell projects={projects} initialRunResponse={initialRunResponse} initialRuns={runs} summary={summary} initialRequests={requests} />;
}
