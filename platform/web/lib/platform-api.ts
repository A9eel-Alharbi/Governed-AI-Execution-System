import {
  sampleProjects,
  samplePolicyProfiles,
  samplePolicyProfileVersions,
  sampleApprovals,
  sampleAuthConfig,
  sampleDashboardSummary,
  sampleGovernedRequests,
  sampleRunDetails,
  sampleRunResponse,
  sampleRuns,
  sampleSession,
  type ApprovalSummary,
  type AuthSession,
  type AuthConfig,
  type DashboardSummary,
  type GovernedRequestSummary,
  type ProjectSummary,
  type PolicyProfile,
  type PolicyProfileVersion,
  type RunDetail,
  type RunResponse,
  type RunSummary,
  type UserSummary,
} from "./sample-data";

const apiBase = process.env.NEXT_PUBLIC_PLATFORM_API_URL ?? "http://127.0.0.1:8100";

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`platform_api_error:${response.status}`);
  }
  return (await response.json()) as T;
}

function authHeaders(token?: string | null): HeadersInit {
  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}

export async function getProjects(token?: string | null): Promise<ProjectSummary[]> {
  try {
    const response = await fetch(`${apiBase}/projects`, {
      cache: "no-store",
      headers: authHeaders(token),
    });
    return await parseJson<ProjectSummary[]>(response);
  } catch {
    return sampleProjects;
  }
}

export async function getDashboardSummary(token?: string | null): Promise<DashboardSummary> {
  try {
    const response = await fetch(`${apiBase}/dashboard/summary`, {
      cache: "no-store",
      headers: authHeaders(token),
    });
    return await parseJson<DashboardSummary>(response);
  } catch {
    return sampleDashboardSummary;
  }
}

export async function getProjectBySlug(slug: string, token?: string | null): Promise<ProjectSummary | null> {
  try {
    const response = await fetch(`${apiBase}/projects/slug/${slug}`, {
      cache: "no-store",
      headers: authHeaders(token),
    });
    return await parseJson<ProjectSummary>(response);
  } catch {
    return sampleProjects.find((project) => project.slug === slug) ?? null;
  }
}

export async function createProject(input: {
  name: string;
  repository_url: string;
  default_branch?: string;
  repository_root?: string;
  token?: string | null;
}): Promise<ProjectSummary> {
  const response = await fetch(`${apiBase}/projects`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(input.token),
    },
    body: JSON.stringify(input),
  });
  return parseJson<ProjectSummary>(response);
}

export async function updateProjectConnection(input: {
  project_id: string;
  repository_url: string;
  default_branch?: string;
  repository_root?: string;
  session_loader?: string;
  policy_artifact?: string;
  threat_model_document?: string;
  status?: ProjectSummary["status"];
  token?: string | null;
}): Promise<ProjectSummary> {
  const response = await fetch(`${apiBase}/projects/${input.project_id}/connection`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(input.token),
    },
    body: JSON.stringify({
      repository_url: input.repository_url,
      default_branch: input.default_branch ?? "main",
      repository_root: input.repository_root ?? null,
      session_loader: input.session_loader ?? null,
      policy_artifact: input.policy_artifact ?? null,
      threat_model_document: input.threat_model_document ?? null,
      status: input.status ?? "connected",
    }),
  });
  return parseJson<ProjectSummary>(response);
}

export async function demoLogin(email: string): Promise<AuthSession> {
  try {
    const response = await fetch(`${apiBase}/auth/demo-login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });
    return await parseJson<AuthSession>(response);
  } catch {
    return sampleSession;
  }
}

export async function getAuthConfig(): Promise<AuthConfig> {
  try {
    const response = await fetch(`${apiBase}/auth/config`, {
      cache: "no-store",
    });
    return await parseJson<AuthConfig>(response);
  } catch {
    return sampleAuthConfig;
  }
}

export async function getCurrentUser(token?: string | null): Promise<UserSummary | null> {
  if (!token) {
    return null;
  }
  try {
    const response = await fetch(`${apiBase}/auth/me`, {
      cache: "no-store",
      headers: authHeaders(token),
    });
    return await parseJson<UserSummary>(response);
  } catch {
    return sampleSession.user;
  }
}

export async function interpretProjectRequest(input: {
  project_id: string;
  text: string;
  execute?: boolean;
  persist?: boolean;
  context?: Record<string, unknown>;
  token?: string | null;
}): Promise<RunResponse> {
  try {
    const response = await fetch(`${apiBase}/${input.execute ? "runs/execute" : "runs/interpret"}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(input.token),
      },
      body: JSON.stringify({
        project_id: input.project_id,
        text: input.text,
        execute: Boolean(input.execute),
        persist: Boolean(input.persist),
        context: input.context ?? {},
      }),
    });
    return await parseJson<RunResponse>(response);
  } catch {
    return {
      ...sampleRunResponse,
      project: sampleProjects.find((project) => project.project_id === input.project_id) ?? sampleRunResponse.project,
      decision: {
        ...sampleRunResponse.decision,
        raw_input: input.text,
        restored_input: input.text,
        normalized_input: input.text,
      },
    };
  }
}

export async function submitGovernedRequest(input: {
  project_id: string;
  text: string;
  execute?: boolean;
  persist?: boolean;
  dry_run?: boolean;
  context?: Record<string, unknown>;
  token?: string | null;
}): Promise<GovernedRequestSummary> {
  try {
    const response = await fetch(`${apiBase}/requests/submit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(input.token),
      },
      body: JSON.stringify({
        project_id: input.project_id,
        text: input.text,
        execute: Boolean(input.execute),
        persist: Boolean(input.persist),
        dry_run: Boolean(input.dry_run),
        context: input.context ?? {},
      }),
    });
    return await parseJson<GovernedRequestSummary>(response);
  } catch {
    return {
      ...sampleGovernedRequests[0],
      project_id: input.project_id,
      request_text: input.text,
      dry_run: Boolean(input.dry_run),
    };
  }
}

export async function getGovernedRequests(input: {
  token?: string | null;
  project_id?: string;
}): Promise<GovernedRequestSummary[]> {
  try {
    const params = new URLSearchParams();
    if (input.project_id) {
      params.set("project_id", input.project_id);
    }
    const response = await fetch(`${apiBase}/requests${params.toString() ? `?${params.toString()}` : ""}`, {
      cache: "no-store",
      headers: authHeaders(input.token),
    });
    return await parseJson<GovernedRequestSummary[]>(response);
  } catch {
    return input.project_id ? sampleGovernedRequests.filter((request) => request.project_id === input.project_id) : sampleGovernedRequests;
  }
}

export async function actOnGovernedRequest(input: {
  request_id: string;
  action: "approve" | "reject" | "escalate";
  reason?: string;
  token?: string | null;
}): Promise<GovernedRequestSummary> {
  const response = await fetch(`${apiBase}/requests/${input.request_id}/${input.action}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(input.token),
    },
    body: JSON.stringify({
      reason: input.reason ?? "",
    }),
  });
  return parseJson<GovernedRequestSummary>(response);
}

export async function resubmitGovernedRequest(input: {
  request_id: string;
  token?: string | null;
}): Promise<GovernedRequestSummary> {
  const response = await fetch(`${apiBase}/requests/${input.request_id}/resubmit`, {
    method: "POST",
    headers: {
      ...authHeaders(input.token),
    },
  });
  return parseJson<GovernedRequestSummary>(response);
}

export async function getRuns(input: {
  token?: string | null;
  project_id?: string;
}): Promise<RunSummary[]> {
  try {
    const params = new URLSearchParams();
    if (input.project_id) {
      params.set("project_id", input.project_id);
    }
    const response = await fetch(`${apiBase}/runs${params.toString() ? `?${params.toString()}` : ""}`, {
      cache: "no-store",
      headers: authHeaders(input.token),
    });
    return await parseJson<RunSummary[]>(response);
  } catch {
    return input.project_id ? sampleRuns.filter((run) => run.project_id === input.project_id) : sampleRuns;
  }
}

export async function getRunDetail(runId: string, token?: string | null): Promise<RunDetail | null> {
  try {
    const response = await fetch(`${apiBase}/runs/${runId}`, {
      cache: "no-store",
      headers: authHeaders(token),
    });
    return await parseJson<RunDetail>(response);
  } catch {
    return sampleRunDetails[runId] ?? null;
  }
}

export async function getApprovals(input: {
  token?: string | null;
  project_id?: string;
}): Promise<ApprovalSummary[]> {
  try {
    const params = new URLSearchParams();
    if (input.project_id) {
      params.set("project_id", input.project_id);
    }
    const response = await fetch(`${apiBase}/approvals${params.toString() ? `?${params.toString()}` : ""}`, {
      cache: "no-store",
      headers: authHeaders(input.token),
    });
    return await parseJson<ApprovalSummary[]>(response);
  } catch {
    return input.project_id ? sampleApprovals.filter((approval) => approval.project_id === input.project_id) : sampleApprovals;
  }
}

export async function createApproval(input: {
  project_id: string;
  title: string;
  target_class: ApprovalSummary["target_class"];
  environment: ApprovalSummary["environment"];
  case_ids: string[];
  notes: string[];
  token?: string | null;
}): Promise<ApprovalSummary> {
  const response = await fetch(`${apiBase}/approvals`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(input.token),
    },
    body: JSON.stringify({
      project_id: input.project_id,
      title: input.title,
      target_class: input.target_class,
      environment: input.environment,
      case_ids: input.case_ids,
      notes: input.notes,
    }),
  });
  return parseJson<ApprovalSummary>(response);
}

export async function updateApproval(input: {
  approval_id: string;
  status: ApprovalSummary["status"];
  approved_by: string[];
  notes: string[];
  token?: string | null;
}): Promise<ApprovalSummary> {
  const response = await fetch(`${apiBase}/approvals/${input.approval_id}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(input.token),
    },
    body: JSON.stringify({
      status: input.status,
      approved_by: input.approved_by,
      notes: input.notes,
    }),
  });
  return parseJson<ApprovalSummary>(response);
}

export async function getPolicyProfile(projectId: string, token?: string | null): Promise<PolicyProfile | null> {
  try {
    const response = await fetch(`${apiBase}/projects/${projectId}/policy-profile`, {
      cache: "no-store",
      headers: authHeaders(token),
    });
    return await parseJson<PolicyProfile>(response);
  } catch {
    return samplePolicyProfiles[projectId] ?? null;
  }
}

export async function updatePolicyProfile(input: {
  project_id: string;
  token?: string | null;
  environment: PolicyProfile["environment"];
  approval_state: PolicyProfile["approval_state"];
  target_class: PolicyProfile["target_class"];
  destructive_action: boolean;
  path_privilege?: string | null;
  human_review_required: boolean;
  notes: string[];
  reason: string;
}): Promise<PolicyProfile> {
  const response = await fetch(`${apiBase}/projects/${input.project_id}/policy-profile`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(input.token),
    },
    body: JSON.stringify({
      environment: input.environment,
      approval_state: input.approval_state,
      target_class: input.target_class,
      destructive_action: input.destructive_action,
      path_privilege: input.path_privilege ?? null,
      human_review_required: input.human_review_required,
      notes: input.notes,
      reason: input.reason,
    }),
  });
  return parseJson<PolicyProfile>(response);
}

export async function getPolicyProfileHistory(projectId: string, token?: string | null): Promise<PolicyProfileVersion[]> {
  try {
    const response = await fetch(`${apiBase}/projects/${projectId}/policy-history`, {
      cache: "no-store",
      headers: authHeaders(token),
    });
    return await parseJson<PolicyProfileVersion[]>(response);
  } catch {
    return samplePolicyProfileVersions[projectId] ?? [];
  }
}
