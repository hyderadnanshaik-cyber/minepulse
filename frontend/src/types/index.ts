export type ConnectionHealth = "ONLINE" | "DEGRADED" | "OFFLINE" | "UNKNOWN";
export type SyncStatus = "ONLINE" | "SYNCING" | "OFFLINE" | "UNKNOWN";
export type RiskLevel = "NORMAL" | "WATCH" | "WARNING" | "HIGH" | "CRITICAL";
export type AlertSeverity = "WATCH" | "WARNING" | "HIGH" | "CRITICAL";
export type AlertStatus = "ACTIVE" | "ACKNOWLEDGED" | "RESOLVED" | "DETECTED";
export type UserRole = "ADMIN" | "ENGINEER" | "OPERATOR" | "VIEWER";

export interface User {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL?: string | null;
  role: UserRole;
}

export interface Panel {
  id: number;
  panel_id: string;
  name?: string;
  description?: string;
  status?: string;
}

export interface Node {
  id: number;
  node_id: string;
  node_code: string;
  device_id?: string;
  name?: string;
  panel_id?: string | number;
  panel_name?: string;
  zone?: string;
  status: ConnectionHealth;
  risk_level?: RiskLevel;
  risk_score?: number;
  battery_level: number;
  battery?: number;
  signal_strength: number;
  rssi?: number;
  snr?: number;
  hop_count?: number;
  parent_node_id?: string | number | null;
  mesh_route?: string[];
  last_seen?: string;
  installed_at?: string;
  latitude: number;
  longitude: number;
  hardware_spec?: string;
  buzzer_active?: boolean;
  led_active?: boolean;
  is_root?: boolean;
  mesh_layer?: number;
  depth_m?: number;
}

export interface SensorReading {
  id?: number;
  node_id: string | number;
  node_code?: string;
  timestamp?: string;
  recorded_at?: string;
  tilt?: number;
  tilt_x?: number;
  tilt_x_deg?: number;
  tilt_y?: number;
  tilt_y_deg?: number;
  vibration?: number;
  accel_x?: number;
  accel_y?: number;
  accel_z?: number;
  gyro_x?: number;
  gyro_y?: number;
  gyro_z?: number;
  mag_x?: number;
  mag_y?: number;
  mag_z?: number;
  temperature?: number;
  humidity?: number;
  pressure?: number;
  displacement?: number;
  displacement_mm?: number;
  displacement_rate?: number;
  displacement_baseline?: number;
  crack_detected?: boolean;
  crack_status?: boolean;
  crack_width?: number;
  battery?: number;
  battery_level?: number;
  rssi?: number;
  signal_strength?: number;
  snr?: number;
  hop_count?: number;
  parent_node_id?: string | null;
  mesh_route?: string[];
}

export interface Alert {
  id: number;
  node_id: string | number;
  node_code?: string;
  alert_type: string;
  severity: AlertSeverity;
  status: AlertStatus;
  title?: string;
  message: string;
  risk_score?: number;
  anomaly_score?: number;
  local_alarm_activated?: boolean;
  detected_at?: string;
  triggered_at?: string;
  acknowledged_at?: string | null;
  resolved_at?: string | null;
  acknowledged_by?: string | null;
  sync_status?: string;
}

export interface MeshConnection {
  id?: number;
  from_node_id?: string | number;
  to_node_id?: string | number;
  node_id?: string;
  neighbor_node_id?: string;
  rssi?: number;
  signal_strength?: number;
  hop_count?: number;
  layer?: number;
  packet_loss_pct?: number;
  is_active?: boolean;
  last_seen?: string;
}

export interface GatewayStatus {
  id?: number;
  name?: string;
  device_id?: string;
  ip_address?: string;
  status: ConnectionHealth;
  cpu_usage?: number;
  ram_usage?: number;
  temperature?: number;
  storage_used?: number;
  mqtt_status?: string;
  mesh_status?: string;
  db_status?: string;
  internet_connected?: boolean;
  cloud_sync_status?: SyncStatus;
  alarm_active?: boolean;
  last_seen?: string;
  updated_at?: string;
}

export interface SystemStatus {
  mesh_status: ConnectionHealth;
  gateway_status: ConnectionHealth;
  internet_status: ConnectionHealth;
  cloud_status: SyncStatus;
  db_status: ConnectionHealth;
}

