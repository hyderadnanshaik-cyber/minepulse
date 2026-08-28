import { useSystemStore } from "../store/systemStore";
import { useNodeStore } from "../store/nodeStore";
import { useAlertStore } from "../store/alertStore";
export function useSystemStatus() {
  const { status, gateway, lastChecked } = useSystemStore();
  const { nodes } = useNodeStore();
  const { alerts } = useAlertStore();
  const totalNodes = nodes.length;
  const onlineNodes = nodes.filter((n) => n.status === "ONLINE").length;
  const degradedNodes = nodes.filter((n) => n.status === "DEGRADED").length;
  const offlineNodes = nodes.filter((n) => n.status === "OFFLINE").length;
  const activeAlerts = alerts.filter((a) => a.status === "ACTIVE");
  const criticalAlerts = activeAlerts.filter((a) => a.severity === "CRITICAL");
  const highAlerts = activeAlerts.filter((a) => a.severity === "HIGH");
  const warningAlerts = activeAlerts.filter((a) => a.severity === "WARNING");
  const watchAlerts = activeAlerts.filter((a) => a.severity === "WATCH");
  let overallRisk: "NORMAL" | "WATCH" | "WARNING" | "HIGH" | "CRITICAL" =
    "NORMAL";
  if (criticalAlerts.length > 0) overallRisk = "CRITICAL";
  else if (highAlerts.length > 0) overallRisk = "HIGH";
  else if (warningAlerts.length > 0) overallRisk = "WARNING";
  else if (watchAlerts.length > 0) overallRisk = "WATCH";
  return {
    status,
    gateway,
    lastChecked,
    totalNodes,
    onlineNodes,
    degradedNodes,
    offlineNodes,
    activeAlertsCount: activeAlerts.length,
    criticalCount: criticalAlerts.length,
    highCount: highAlerts.length,
    warningCount: warningAlerts.length,
    watchCount: watchAlerts.length,
    overallRisk,
  };
}
