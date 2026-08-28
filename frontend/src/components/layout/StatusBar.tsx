import React from "react";
import { useTranslation } from "react-i18next";
import { useConnectivity } from "../../hooks/useConnectivity";
import { Radio, Server, Globe, CloudUpload } from "lucide-react";
import { ConnectionHealth, SyncStatus } from "../../types";

export const StatusBar: React.FC = () => {
  const { t } = useTranslation();
  const { status } = useConnectivity();

  const getStatusColor = (val: ConnectionHealth | SyncStatus) => {
    switch (val) {
      case "ONLINE":   return { dot: "bg-emerald-500", text: "text-emerald-700", bg: "bg-emerald-50" };
      case "DEGRADED":
      case "SYNCING":  return { dot: "bg-amber-500 animate-pulse", text: "text-amber-700", bg: "bg-amber-50" };
      case "OFFLINE":  return { dot: "bg-red-500", text: "text-red-700", bg: "bg-red-50" };
      default:         return { dot: "bg-slate-400", text: "text-slate-600", bg: "bg-slate-50" };
    }
  };

  const Indicator = ({
    label, shortLabel, val, icon
  }: { label: string; shortLabel: string; val: ConnectionHealth | SyncStatus; icon: React.ReactNode }) => {
    const style = getStatusColor(val);
    const statusText = val === "ONLINE" ? t("common.online") : val === "OFFLINE" ? t("common.offline") : val;
    return (
      <div className={`flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1 rounded border border-slate-200 shadow-xs ${style.bg} shrink-0`}>
        <span className="text-slate-500">{icon}</span>
        <span className="hidden sm:inline text-[11px] font-bold tracking-wider uppercase text-slate-700">{label}:</span>
        <span className="sm:hidden text-[10px] font-bold uppercase text-slate-600">{shortLabel}:</span>
        <span className={`h-2 w-2 rounded-full ${style.dot}`} />
        <span className={`hidden sm:inline text-[11px] font-bold ${style.text}`}>{statusText}</span>
      </div>
    );
  };

  return (
    <header className="bg-white border-b border-slate-200 px-3 sm:px-4 py-1.5 flex items-center justify-between z-30 sticky top-0 shadow-xs overflow-x-hidden">
      <div className="flex items-center gap-1.5 sm:gap-2 min-w-0">
        <Indicator label="Sensor Network" shortLabel="SNSR" val={status.mesh_status}     icon={<Radio className="h-3.5 w-3.5" />} />
        <Indicator label="Edge Gateway"   shortLabel="GW"   val={status.gateway_status}  icon={<Server className="h-3.5 w-3.5" />} />
        <Indicator label="Internet WAN"   shortLabel="WAN"  val={status.internet_status} icon={<Globe className="h-3.5 w-3.5" />} />
        <Indicator label="Cloud Sync"     shortLabel="SYNC" val={status.cloud_status}    icon={<CloudUpload className="h-3.5 w-3.5" />} />
      </div>
      <div className="hidden md:flex items-center gap-2 text-[11px] text-slate-500 shrink-0">
        <span className="font-mono">SIH26025 • Mine Pulse by RED HACK</span>
      </div>
    </header>
  );
};

export default StatusBar;
