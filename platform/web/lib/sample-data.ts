export type ProjectSummary = {
  project_id: string;
  owner_id?: string | null;
  owner_name?: string | null;
  name: string;
  slug: string;
  repository_url: string;
  default_branch: string;
  status: "draft" | "connected" | "active" | "blocked";
  repository_root?: string | null;
  session_loader?: string | null;
  policy_artifact?: string | null;
  approvals_in_force?: string[];
  vault_health_status?: "healthy" | "review" | "degraded" | "pending";
  threat_model_document?: string | null;
  default_context?: Record<string, unknown>;
  is_processing?: boolean;
  processing_started_at?: string | null;
};

export type DecisionPayload = {
  raw_input: string;
  restored_input: string;
  normalized_input: string;
  outcome: "clarify" | "refuse" | "dispatch" | "escalate";
  rationale: string;
  case_id?: string | null;
  clarification_question?: string | null;
  refusal_reason?: string | null;
  escalation_reason?: string | null;
  dispatch_target?: {
    case_id: string;
    procedure: string;
    target: string;
    human_review_gate?: boolean;
  } | null;
  decision_trace?: Array<{ stage: string; detail: string }>;
};

export type ExecutionPayload = {
  status: string;
  procedure: string;
  target: string;
  details?: Record<string, unknown>;
};

export type RunResponse = {
  project: ProjectSummary;
  context: Record<string, unknown>;
  decision: DecisionPayload;
  execution?: ExecutionPayload | null;
};

export type RunSummary = {
  run_id: string;
  project_id: string;
  owner_id?: string | null;
  text: string;
  outcome: "clarify" | "refuse" | "dispatch" | "escalate";
  case_id?: string | null;
  execution_status?: string | null;
  created_at: string;
  rationale: string;
};

export type RunDetail = {
  run_id: string;
  project_id: string;
  owner_id?: string | null;
  created_at: string;
  request_text: string;
  context: Record<string, unknown>;
  decision: DecisionPayload;
  execution?: ExecutionPayload | null;
};

export type ApprovalSummary = {
  approval_id: string;
  project_id: string;
  owner_id?: string | null;
  title: string;
  status: "draft" | "approved" | "rejected" | "expired";
  target_class: "general" | "security" | "production" | "infrastructure";
  environment: "dev" | "staging" | "prod";
  case_ids: string[];
  approved_by: string[];
  notes: string[];
  updated_at: string;
};

export type PolicyProfile = {
  project_id: string;
  owner_id?: string | null;
  environment: "dev" | "staging" | "prod";
  approval_state: "unapproved" | "approved";
  target_class: "general" | "security" | "production" | "infrastructure";
  destructive_action: boolean;
  path_privilege?: string | null;
  human_review_required: boolean;
  notes: string[];
  updated_at: string;
};

export type PolicyProfileVersion = {
  version_id: string;
  project_id: string;
  owner_id?: string | null;
  previous_state?: Record<string, unknown> | null;
  new_state: Record<string, unknown>;
  changed_by: string;
  changed_at: string;
  reason: string;
};

export type UserSummary = {
  user_id: string;
  email: string;
  name: string;
  role: "owner" | "member" | "admin";
};

export type AuthSession = {
  token: string;
  user: UserSummary;
};

export type AuthConfig = {
  mode: "demo" | "external";
  provider_name: string;
  login_path?: string | null;
};

export type DashboardSummary = {
  total_projects: number;
  active_projects: number;
  connected_projects: number;
  blocked_projects: number;
  projects_with_repo_connections: number;
  policy_profiles_configured: number;
  approvals_total: number;
  approvals_approved: number;
  runs_total: number;
  policy_critical_paths: number;
  outcome_counts: Record<string, number>;
};

export type GovernedRequestSummary = {
  request_id: string;
  project_id: string;
  owner_id?: string | null;
  request_text: string;
  status:
    | "SUBMITTED"
    | "CLASSIFIED"
    | "PENDING_APPROVAL"
    | "APPROVED"
    | "DISPATCHED"
    | "REJECTED"
    | "TERMINATED"
    | "ESCALATED"
    | "PENDING_REVIEW"
    | "EXECUTION_FAILED"
    | "FAILED"
    | "COMPLETED";
  dry_run: boolean;
  risk_level: "low" | "medium" | "high";
  outcome?: "clarify" | "refuse" | "dispatch" | "escalate" | null;
  case_id?: string | null;
  policy_triggers: string[];
  intended_actions: string[];
  approval_reason?: string | null;
  escalation_reason?: string | null;
  rejection_reason?: string | null;
  failure_summary?: string | null;
  failure_detail?: string | null;
  last_successful_step?: string | null;
  partial_artifacts: string[];
  tool_call_log: Array<Record<string, unknown>>;
  request_context: Record<string, unknown>;
  decision_trace: Array<{ stage: string; detail: string }>;
  created_at: string;
  updated_at: string;
  expires_at?: string | null;
};

export const sampleProjects: ProjectSummary[] = [
  {
    project_id: "proj_agent_control_stack",
    owner_id: "user_demo",
    owner_name: "A9eel",
    name: "Agent Control Stack",
    slug: "agent-control-stack",
    repository_url: "https://github.com/A9eel-Alharbi/AOS-CDD.git",
    default_branch: "main",
    status: "active",
    repository_root: "D:/Projects/mygithub/v2/aos-cdd-v2",
    session_loader: "examples/agent-control-stack/sessions/session-WP-001.yaml",
    policy_artifact: "examples/agent-control-stack/ops/policy-profile.yaml",
    approvals_in_force: ["APR-001-security-validation"],
    vault_health_status: "healthy",
    threat_model_document: "examples/agent-control-stack/ops/security-threat-model.md",
    default_context: {
      repository_root: "D:/Projects/mygithub/v2/aos-cdd-v2",
      session_loader: "examples/agent-control-stack/sessions/session-WP-001.yaml",
      policy_artifact: "examples/agent-control-stack/ops/policy-profile.yaml",
    },
    is_processing: false,
    processing_started_at: null,
  },
  {
    project_id: "proj_gym_revenue_saas",
    owner_id: "user_demo",
    owner_name: "A9eel",
    name: "Gym Revenue SaaS",
    slug: "gym-revenue-saas",
    repository_url: "https://github.com/acme/gym-saas",
    default_branch: "main",
    status: "connected",
    repository_root: "D:/Projects/mygithub/v2/aos-cdd-v2",
    approvals_in_force: [],
    vault_health_status: "pending",
    default_context: {
      repository_root: "D:/Projects/mygithub/v2/aos-cdd-v2",
      project_name: "Gym Revenue SaaS",
      project_goal: "Build a governed SaaS API for gym memberships and revenue tracking.",
      v1_scope: "members, plans, payments, monthly revenue summary",
    },
    is_processing: false,
    processing_started_at: null,
  },
];

export const sampleRunResponse: RunResponse = {
  project: sampleProjects[0],
  context: sampleProjects[0].default_context ?? {},
  decision: {
    raw_input: "Run WP-001 now",
    restored_input: "Run WP-001 now",
    normalized_input: "Run WP-001 now",
    outcome: "dispatch",
    rationale: "The request is clear enough to proceed through a registered governed path.",
    case_id: "implementation.run_wp",
    dispatch_target: {
      case_id: "implementation.run_wp",
      procedure: "run_work_package",
      target: "examples/agent-control-stack/sessions/session-WP-001.yaml",
      human_review_gate: false,
    },
    decision_trace: [
      { stage: "restore", detail: "No restoration changes were applied." },
      { stage: "balance", detail: "No balancing changes were applied." },
      { stage: "classify", detail: "Matched case `implementation.run_wp`." },
      { stage: "policy", detail: "Request approved for governed dispatch." },
    ],
  },
  execution: {
    status: "ready",
    procedure: "run_work_package",
    target: "examples/agent-control-stack/sessions/session-WP-001.yaml",
  },
};

export const sampleSession: AuthSession = {
  token: "demo-token",
  user: {
    user_id: "user_demo",
    email: "demo@aos-cdd.local",
    name: "A9eel",
    role: "owner",
  },
};

export const sampleAuthConfig: AuthConfig = {
  mode: "demo",
  provider_name: "Demo Auth",
  login_path: null,
};

export const sampleDashboardSummary: DashboardSummary = {
  total_projects: 2,
  active_projects: 1,
  connected_projects: 1,
  blocked_projects: 0,
  projects_with_repo_connections: 2,
  policy_profiles_configured: 2,
  approvals_total: 1,
  approvals_approved: 1,
  runs_total: 2,
  policy_critical_paths: 1,
  outcome_counts: {
    dispatch: 1,
    clarify: 1,
  },
};

export const sampleRuns: RunSummary[] = [
  {
    run_id: "run_20260429121000_ab12cd34",
    project_id: "proj_agent_control_stack",
    owner_id: "user_demo",
    text: "Run WP-001 now",
    outcome: "dispatch",
    case_id: "implementation.run_wp",
    execution_status: "ready",
    created_at: "2026-04-29T09:10:00+00:00",
    rationale: "The request is clear enough to proceed through a registered governed path.",
  },
  {
    run_id: "run_20260429121500_ef56ab78",
    project_id: "proj_gym_revenue_saas",
    owner_id: "user_demo",
    text: "Update constraints for the vision document",
    outcome: "clarify",
    case_id: "docs.update_constraints",
    execution_status: null,
    created_at: "2026-04-29T09:15:00+00:00",
    rationale: "The request maps to a known case, but required intent is still missing.",
  },
];

export const sampleRunDetails: Record<string, RunDetail> = {
  run_20260429121000_ab12cd34: {
    run_id: "run_20260429121000_ab12cd34",
    project_id: "proj_agent_control_stack",
    owner_id: "user_demo",
    created_at: "2026-04-29T09:10:00+00:00",
    request_text: "Run WP-001 now",
    context: sampleProjects[0].default_context ?? {},
    decision: sampleRunResponse.decision,
    execution: sampleRunResponse.execution,
  },
};

export const sampleApprovals: ApprovalSummary[] = [
  {
    approval_id: "APR-001-security-validation",
    project_id: "proj_agent_control_stack",
    owner_id: "user_demo",
    title: "Production security validation approval",
    status: "approved",
    target_class: "security",
    environment: "prod",
    case_ids: ["ops.run_validation"],
    approved_by: ["security.lead", "platform.lead"],
    notes: ["Allows governed security validation against production-class scope."],
    updated_at: "2026-04-29T09:00:00+00:00",
  },
];

export const samplePolicyProfiles: Record<string, PolicyProfile> = {
  proj_agent_control_stack: {
    project_id: "proj_agent_control_stack",
    owner_id: "user_demo",
    environment: "prod",
    approval_state: "approved",
    target_class: "security",
    destructive_action: false,
    path_privilege: "security-approved",
    human_review_required: true,
    notes: [
      "Governed security validation requires human review before high-risk execution.",
      "Platform mirrors the repo policy profile for request defaults.",
    ],
    updated_at: "2026-04-29T09:00:00+00:00",
  },
  proj_gym_revenue_saas: {
    project_id: "proj_gym_revenue_saas",
    owner_id: "user_demo",
    environment: "dev",
    approval_state: "unapproved",
    target_class: "general",
    destructive_action: false,
    path_privilege: null,
    human_review_required: false,
    notes: ["New project remains in a low-risk draft policy posture until constraints settle."],
    updated_at: "2026-04-29T09:05:00+00:00",
  },
};

export const samplePolicyProfileVersions: Record<string, PolicyProfileVersion[]> = {
  proj_agent_control_stack: [
    {
      version_id: "policy_ver_agent_control_stack_initial",
      project_id: "proj_agent_control_stack",
      owner_id: "user_demo",
      previous_state: null,
      new_state: samplePolicyProfiles.proj_agent_control_stack,
      changed_by: "user_demo",
      changed_at: "2026-04-29T09:00:00+00:00",
      reason: "Initial platform policy mirror created from governed repo policy.",
    },
  ],
  proj_gym_revenue_saas: [
    {
      version_id: "policy_ver_gym_revenue_saas_initial",
      project_id: "proj_gym_revenue_saas",
      owner_id: "user_demo",
      previous_state: null,
      new_state: samplePolicyProfiles.proj_gym_revenue_saas,
      changed_by: "user_demo",
      changed_at: "2026-04-29T09:05:00+00:00",
      reason: "Initial low-risk draft policy created for new project onboarding.",
    },
  ],
};

export const sampleGovernedRequests: GovernedRequestSummary[] = [
  {
    request_id: "req_20260429170000_ab12cd34",
    project_id: "proj_agent_control_stack",
    owner_id: "user_demo",
    request_text: "Run WP-001 now",
    status: "PENDING_APPROVAL",
    dry_run: false,
    risk_level: "high",
    outcome: "dispatch",
    case_id: "implementation.run_wp",
    policy_triggers: ["Request approved for governed dispatch."],
    intended_actions: ["run_work_package: examples/agent-control-stack/sessions/session-WP-001.yaml"],
    partial_artifacts: [],
    tool_call_log: [],
    request_context: sampleProjects[0].default_context ?? {},
    decision_trace: sampleRunResponse.decision.decision_trace ?? [],
    created_at: "2026-04-29T17:00:00+00:00",
    updated_at: "2026-04-29T17:00:00+00:00",
    expires_at: "2026-04-29T21:00:00+00:00",
  },
];
