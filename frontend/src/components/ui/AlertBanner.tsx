import React from "react";
import { Alert } from "../../types";
import {
  AlertTriangle,
  AlertCircle,
  Info,
  ShieldAlert,
  CheckCircle,
} from "lucide-react";
interface AlertBannerProps {
  alert: Alert;
  onAcknowledge?: (id: number) => void;
  onResolve?: (id: number) => void;
}
export const AlertBanner: React.FC<AlertBannerProps> = ({
  alert,
  onAcknowledge,
  onResolve,
}) => {
  const getIcon = () => {
    switch (alert.severity) {
      case "CRITICAL":
        return <ShieldAlert className="h-5 w-5 text-red-600 animate-pulse" />;
      case "HIGH":
        return <AlertTriangle className="h-5 w-5 text-orange-600" />;
      case "WARNING":
        return <AlertCircle className="h-5 w-5 text-amber-600" />;
      case "WATCH":
        return <Info className="h-5 w-5 text-blue-600" />;
      default:
        return <Info className="h-5 w-5 text-slate-600 " />;
    }
  };
  const getBg = () => {
    switch (alert.severity) {
      case "CRITICAL":
        return "bg-red-50 border-red-200 text-red-900";
      case "HIGH":
        return "bg-orange-50 border-orange-200 text-orange-900";
      case "WARNING":
        return "bg-amber-50 border-amber-200 text-amber-900";
      case "WATCH":
        return "bg-blue-50 border-blue-200 text-blue-900";
      default:
        return "bg-slate-50 border-slate-200 text-slate-900 ";
    }
  };
  return (
    <div
      className={`p-4 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-3 ${getBg()}`}
    >
      {" "}
      <div className="flex items-start gap-3">
        {" "}
        <div className="mt-0.5">{getIcon()}</div>{" "}
        <div>
          {" "}
          <div className="flex items-center gap-2">
            {" "}
            <span className="font-bold text-sm tracking-wide">
              [{alert.severity}] {alert.alert_type}
            </span>{" "}
            <span className="text-xs opacity-75 font-mono">
              Node #{alert.node_id}
            </span>{" "}
          </div>{" "}
          <p className="text-sm mt-0.5">{alert.message}</p>{" "}
          <span className="text-[11px] opacity-60 mt-1 block">
            {" "}
            Triggered:{" "}
            {alert.triggered_at
              ? new Date(alert.triggered_at).toLocaleString()
              : "N/A"}{" "}
          </span>{" "}
        </div>{" "}
      </div>{" "}
      <div className="flex items-center gap-2 self-end md:self-center">
        {" "}
        {alert.status === "ACTIVE" && onAcknowledge && (
          <button
            onClick={() => onAcknowledge(alert.id)}
            className="px-3 py-1.5 bg-white border border-slate-300 text-slate-800 text-xs font-semibold rounded-lg hover:bg-slate-50 shadow-sm transition"
          >
            {" "}
            Acknowledge{" "}
          </button>
        )}{" "}
        {alert.status !== "RESOLVED" && onResolve && (
          <button
            onClick={() => onResolve(alert.id)}
            className="px-3 py-1.5 bg-emerald-600 text-white text-xs font-semibold rounded-lg hover:bg-emerald-700 shadow-sm transition flex items-center gap-1"
          >
            {" "}
            <CheckCircle className="h-3.5 w-3.5" /> Resolve{" "}
          </button>
        )}{" "}
      </div>{" "}
    </div>
  );
};
