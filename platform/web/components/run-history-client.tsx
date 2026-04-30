"use client";

import { useEffect, useState } from "react";

import { getRuns } from "../lib/platform-api";
import type { RunSummary } from "../lib/sample-data";
import { useAuth } from "./auth-provider";
import { RunHistoryCard } from "./run-history-card";

export function RunHistoryClient({
  projectId,
  initialRuns,
}: {
  projectId?: string;
  initialRuns: RunSummary[];
}) {
  const [runs, setRuns] = useState<RunSummary[]>(initialRuns);
  const { token } = useAuth();

  useEffect(() => {
    void getRuns({ token, project_id: projectId }).then(setRuns);
  }, [token, projectId]);

  if (runs.length === 0) {
    return <p className="text-sm text-slate/72">No governed runs have been recorded yet.</p>;
  }

  return (
    <div className="space-y-3">
      {runs.map((run) => (
        <RunHistoryCard key={run.run_id} run={run} />
      ))}
    </div>
  );
}
