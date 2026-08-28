import React from "react";
import { ConnectionHealth, SyncStatus } from "../../types";
interface StatusBadgeProps {
  status: ConnectionHealth | SyncStatus | "CONNECTED" | "DISCONNECTED";
  size?: "sm" | "md" | "lg";
  showDot?: boolean;
}
export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = "md",
  showDot = true,
}) => {
  let bgClass = "bg-slate-100 text-slate-700 border-slate-200 ";
  let dotClass = "bg-slate-400";
  if (status === "ONLINE" || status === "CONNECTED") {
    bgClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
    dotClass = "bg-emerald-500";
  } else if (status === "DEGRADED" || status === "SYNCING") {
    bgClass = "bg-amber-50 text-amber-700 border-amber-200";
    dotClass = "bg-amber-500 animate-pulse";
  } else if (status === "OFFLINE" || status === "DISCONNECTED") {
    bgClass = "bg-red-50 text-red-700 border-red-200";
    dotClass = "bg-red-500";
  }
  const sizeClasses = {
    sm: "text-xs px-2 py-0.5",
    md: "text-xs px-2.5 py-1 font-medium",
    lg: "text-sm px-3 py-1.5 font-semibold",
  };
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${bgClass} ${sizeClasses[size]}`}
    >
      {" "}
      {showDot && <span className={`h-2 w-2 rounded-full ${dotClass}`} />}{" "}
      {status}{" "}
    </span>
  );
};
