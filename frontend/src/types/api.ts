export interface StatsResponse {
  active_workers: number;
  total_identities: number;
  success_rate: number;
  proxy_latency_ms: number | null;
  tasks_pending: number;
  tasks_running: number;
}

export interface WorkerStatus {
  id: string;
  name?: string;
  type: "physical" | "lxc";
  status: "idle" | "busy" | "error" | "warming_up";
  load: number;
  ip?: string;
  last_seen: string | null;
}

export interface DispatchRequest {
  task_type: string;
  target_url: string;
  volume: number;
}

export interface DispatchResponse {
  task_id: number;
  celery_task_id: string;
  status: string;
}

export interface ProxyHealth {
  id: number;
  name: string;
  provider: string | null;
  latency_ms: number | null;
  status: string;
  last_rotated_at: string | null;
}

export interface TaskResponse {
  id: number;
  type: string;
  target_url: string;
  status: "PENDING" | "QUEUED" | "RUNNING" | "SUCCESS" | "FAILED";
  config: Record<string, unknown> | null;
  error_message: string | null;
  identity_username?: string | null;
  duration_seconds?: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface IdentityResponse {
  id: number;
  username: string;
  platform: string;
  status: "active" | "suspended" | "warming_up" | "cooldown";
  trust_score: number;
  user_agent: string | null;
  has_profile: boolean;
  last_used_at: string | null;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}
