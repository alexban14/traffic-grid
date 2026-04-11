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
  type: "physical" | "lxc";
  status: "idle" | "busy" | "error" | "warming_up";
  load: number;
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
