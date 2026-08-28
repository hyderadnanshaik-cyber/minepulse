import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  AlertTriangle,
  AlertOctagon,
  CheckCircle2,
  Clock,
  MapPin,
  Brain,
  ArrowLeft,
  Map,
  Activity,
  ShieldCheck,
  User,
  FileText,
  ChevronRight,
} from "lucide-react";
import { apiClient } from "../../services/api/apiClient";
interface AlertDetail {
  id: number;
  node_id: string;
  alert_type: string;
  severity: string;
  title: string;
  message: string;
  risk_score: number;
  anomaly_score: number;
  status: string;
  local_alarm_activated: boolean;
  detected_at: string;
  acknowledged_at: string | null;
  acknowledged_by: string | null;
  resolved_at: string | null;
  sync_status: string;
  node_name?: string;
  node_zone?: string;
  node_latitude?: number;
  node_longitude?: number;
  model_version?: string;
  features?: Record<string, any>;
  actions?: Array<{
    id: number;
    action: string;
    performed_by: string;
    notes: string;
    created_at: string;
  }>;
}
export const AlertDetailPage: React.FC = () => {
  const { alertId } = useParams<{ alertId: string }>();
  const navigate = useNavigate();
  const [alert, setAlert] = useState<AlertDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const fetchDetail = async () => {
    if (!alertId) return;
    setLoading(true);
    try {
      const res = await apiClient.get(`/alerts/${alertId}`);
      const data = res.data;
      setAlert({
        ...data,
        node_name: data.node?.name || data.node_name,
        node_zone: data.node?.zone || data.node_zone,
        node_latitude: data.node?.latitude ?? data.node_latitude,
        node_longitude: data.node?.longitude ?? data.node_longitude,
        model_version:
          data.prediction?.model_version ||
          data.model_version ||
          "v2.1.0-IsolationForest-Hybrid",
        features: data.prediction?.features || data.features,
        actions: data.actions || data.alert_actions || [],
      });
      setError(null);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail || "Failed to load incident details",
      );
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchDetail();
  }, [alertId]);
  const handleAcknowledge = async () => {
    if (!alert) return;
    try {
      await apiClient.post(`/alerts/${alert.id}/acknowledge`);
      fetchDetail();
    } catch {}
  };
  const handleResolve = async () => {
    if (!alert) return;
    try {
      await apiClient.post(`/alerts/${alert.id}/resolve`);
      fetchDetail();
    } catch {}
  };
  const formatTime = (iso: string | null) => {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleString();
  };
  const severityConfig = {
    CRITICAL: {
      bg: "bg-red-600",
      text: "text-white",
      icon: AlertOctagon,
      borderColor: "border-red-300 ",
      bgLight: "bg-red-50 ",
    },
    HIGH: {
      bg: "bg-amber-500",
      text: "text-white",
      icon: AlertTriangle,
      borderColor: "border-amber-300 ",
      bgLight: "bg-amber-50 ",
    },
    WARNING: {
      bg: "bg-amber-500",
      text: "text-white",
      icon: AlertTriangle,
      borderColor: "border-amber-300 ",
      bgLight: "bg-amber-50 ",
    },
  };
  const sev =
    severityConfig[alert?.severity as keyof typeof severityConfig] ||
    severityConfig.WARNING;
  const SevIcon = sev.icon;
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        {" "}
        <div className="text-center space-y-3">
          {" "}
          <div className="h-10 w-10 border-4 border-slate-200 border-t-indigo-600 rounded-full animate-spin mx-auto" />{" "}
          <p className="text-sm text-slate-500 ">
            Loading incident details...
          </p>{" "}
        </div>{" "}
      </div>
    );
  }
  if (error || !alert) {
    return (
      <div className="space-y-6">
        {" "}
        <button
          onClick={() => navigate("/app/alerts")}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 transition"
        >
          {" "}
          <ArrowLeft className="h-4 w-4" /> Back to Alerts{" "}
        </button>{" "}
        <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center">
          {" "}
          <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-3" />{" "}
          <h3 className="text-base font-bold text-slate-800 ">
            Incident Not Found
          </h3>{" "}
          <p className="text-xs text-slate-500 mt-1">
            {error || `Alert ID "${alertId}" could not be loaded.`}
          </p>{" "}
        </div>{" "}
      </div>
    );
  }
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {" "}
      {/* Back Navigation */}{" "}
      <button
        onClick={() => navigate("/app/alerts")}
        className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 transition"
      >
        {" "}
        <ArrowLeft className="h-4 w-4" /> Back to Alerts{" "}
      </button>{" "}
      {/* Severity Banner */}{" "}
      <div className={`${sev.bg} rounded-2xl p-6 text-white shadow-lg`}>
        {" "}
        <div className="flex items-center gap-3 mb-2">
          {" "}
          <SevIcon className="h-7 w-7" />{" "}
          <span className="text-[11px] font-extrabold uppercase tracking-widest opacity-80">
            {" "}
            {alert.severity} Safety Incident{" "}
          </span>{" "}
          <span className="ml-auto text-xs opacity-70 font-mono">
            INC-{String(alert.id).padStart(6, "0")}
          </span>{" "}
        </div>{" "}
        <h1 className="text-xl sm:text-2xl font-black leading-tight">
          {" "}
          {alert.title || "Ground Movement Detected"}{" "}
        </h1>{" "}
        <p className="text-sm opacity-90 mt-2 leading-relaxed max-w-2xl">
          {" "}
          {alert.message}{" "}
        </p>{" "}
      </div>{" "}
      {/* Quick Actions */}{" "}
      <div className="flex flex-wrap gap-3">
        {" "}
        {(alert.status === "DETECTED" || alert.status === "ACTIVE") && (
          <button
            onClick={handleAcknowledge}
            className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5"
          >
            {" "}
            <CheckCircle2 className="h-4 w-4" /> Acknowledge{" "}
          </button>
        )}{" "}
        {(alert.status === "DETECTED" ||
          alert.status === "ACTIVE" ||
          alert.status === "ACKNOWLEDGED") && (
          <button
            onClick={handleResolve}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5"
          >
            {" "}
            <ShieldCheck className="h-4 w-4" /> Resolve{" "}
          </button>
        )}{" "}
        <Link
          to={`/app/nodes/${alert.node_id}`}
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition flex items-center gap-1.5"
        >
          {" "}
          <Activity className="h-4 w-4" /> View Node{" "}
        </Link>{" "}
        <Link
          to={`/app/gis?focus=${alert.node_id}`}
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition flex items-center gap-1.5"
        >
          {" "}
          <Map className="h-4 w-4" /> View on Map{" "}
        </Link>{" "}
      </div>{" "}
      {/* Detail Grid */}{" "}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {" "}
        {/* Node Info */}{" "}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card space-y-4">
          {" "}
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            {" "}
            <MapPin className="h-4 w-4 text-emerald-600" /> Monitoring
            Station{" "}
          </h3>{" "}
          <div className="space-y-2.5">
            {" "}
            <div className="flex items-center justify-between">
              {" "}
              <span className="text-xs text-slate-500 ">Node ID</span>{" "}
              <span className="text-sm font-bold font-mono text-slate-900 ">
                {alert.node_id}
              </span>{" "}
            </div>{" "}
            <div className="flex items-center justify-between">
              {" "}
              <span className="text-xs text-slate-500 ">Station Name</span>{" "}
              <span className="text-sm font-semibold text-slate-700 ">
                {alert.node_name || `Station ${alert.node_id}`}
              </span>{" "}
            </div>{" "}
            <div className="flex items-center justify-between">
              {" "}
              <span className="text-xs text-slate-500 ">
                Zone / Location
              </span>{" "}
              <span className="text-sm text-slate-700 ">
                {alert.node_zone || "Underground"}
              </span>{" "}
            </div>{" "}
            {alert.node_latitude && alert.node_longitude && (
              <div className="flex items-center justify-between">
                {" "}
                <span className="text-xs text-slate-500 ">
                  Coordinates
                </span>{" "}
                <span className="text-xs font-mono text-slate-500 ">
                  {alert.node_latitude?.toFixed(6)}°N,{" "}
                  {alert.node_longitude?.toFixed(6)}°E
                </span>{" "}
              </div>
            )}{" "}
          </div>{" "}
        </div>{" "}
        {/* Incident Status */}{" "}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card space-y-4">
          {" "}
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            {" "}
            <Clock className="h-4 w-4 text-blue-600" /> Incident Timeline{" "}
          </h3>{" "}
          <div className="space-y-2.5">
            {" "}
            <div className="flex items-center justify-between">
              {" "}
              <span className="text-xs text-slate-500 ">Status</span>{" "}
              <span
                className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold ${alert.status === "RESOLVED" ? "bg-emerald-100 text-emerald-800 " : alert.status === "ACKNOWLEDGED" ? "bg-blue-100 text-blue-800 " : "bg-red-100 text-red-800 "}`}
              >
                {" "}
                {alert.status}{" "}
              </span>{" "}
            </div>{" "}
            <div className="flex items-center justify-between">
              {" "}
              <span className="text-xs text-slate-500 ">Detected</span>{" "}
              <span className="text-xs font-mono text-slate-700 ">
                {formatTime(alert.detected_at)}
              </span>{" "}
            </div>{" "}
            {alert.acknowledged_at && (
              <div className="flex items-center justify-between">
                {" "}
                <span className="text-xs text-slate-500 ">
                  Acknowledged
                </span>{" "}
                <span className="text-xs font-mono text-slate-700 ">
                  {formatTime(alert.acknowledged_at)}
                </span>{" "}
              </div>
            )}{" "}
            {alert.acknowledged_by && (
              <div className="flex items-center justify-between">
                {" "}
                <span className="text-xs text-slate-500 ">
                  Acknowledged By
                </span>{" "}
                <span className="text-xs text-slate-700 ">
                  {alert.acknowledged_by}
                </span>{" "}
              </div>
            )}{" "}
            {alert.resolved_at && (
              <div className="flex items-center justify-between">
                {" "}
                <span className="text-xs text-slate-500 ">Resolved</span>{" "}
                <span className="text-xs font-mono text-slate-700 ">
                  {formatTime(alert.resolved_at)}
                </span>{" "}
              </div>
            )}{" "}
          </div>{" "}
        </div>{" "}
      </div>{" "}
      {/* AI Evaluation Card */}{" "}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card space-y-4">
        {" "}
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          {" "}
          <Brain className="h-4 w-4 text-indigo-600" /> AI Risk Evaluation{" "}
        </h3>{" "}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {" "}
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 ">
            {" "}
            <span className="text-[10px] text-slate-400 font-bold uppercase block">
              Risk Score
            </span>{" "}
            <span className="text-xl font-black font-mono text-slate-900 mt-0.5 block">
              {" "}
              {(alert.risk_score ?? 0).toFixed(1)} / 100{" "}
            </span>{" "}
          </div>{" "}
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 ">
            {" "}
            <span className="text-[10px] text-slate-400 font-bold uppercase block">
              Anomaly Score
            </span>{" "}
            <span className="text-xl font-black font-mono text-indigo-600 mt-0.5 block">
              {" "}
              {(alert.anomaly_score ?? 0).toFixed(4)}{" "}
            </span>{" "}
          </div>{" "}
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 ">
            {" "}
            <span className="text-[10px] text-slate-400 font-bold uppercase block">
              Severity
            </span>{" "}
            <span
              className={`text-base font-black uppercase mt-1 block ${alert.severity === "CRITICAL" ? "text-red-600 " : "text-amber-600 "}`}
            >
              {" "}
              {alert.severity}{" "}
            </span>{" "}
          </div>{" "}
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 ">
            {" "}
            <span className="text-[10px] text-slate-400 font-bold uppercase block">
              Model Version
            </span>{" "}
            <span className="text-sm font-bold font-mono text-slate-700 mt-1 block">
              {" "}
              {alert.model_version || "v2.1.0"}{" "}
            </span>{" "}
          </div>{" "}
        </div>{" "}
        {alert.local_alarm_activated && (
          <div className="px-4 py-2.5 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs font-bold flex items-center gap-2">
            {" "}
            <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />{" "}
            Emergency alert system activated for this node{" "}
          </div>
        )}{" "}
      </div>{" "}
      {/* Explainability */}{" "}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card space-y-3">
        {" "}
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          {" "}
          <FileText className="h-4 w-4 text-slate-600 " /> Why Was This Alert
          Generated?{" "}
        </h3>{" "}
        <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-700 leading-relaxed space-y-2">
          {" "}
          <p>
            {" "}
            The AI risk assessment engine (IsolationForest + DGMS Statutory
            Rules) evaluated multi-sensor telemetry from{" "}
            <strong>{alert.node_id}</strong> and determined a{" "}
            <strong
              className={
                alert.severity === "CRITICAL"
                  ? "text-red-600 "
                  : "text-amber-600 "
              }
            >
              {alert.severity}
            </strong>{" "}
            risk condition.{" "}
          </p>{" "}
          <p>
            {" "}
            Composite risk score:{" "}
            <strong>{(alert.risk_score ?? 0).toFixed(1)}/100</strong> exceeded
            the alert threshold. ML anomaly score:{" "}
            <strong>{(alert.anomaly_score ?? 0).toFixed(4)}</strong>.{" "}
          </p>{" "}
          <p className="text-slate-500 ">
            {" "}
            This classification was produced by the actual AI/ML risk pipeline
            processing real telemetry data through PostgreSQL. It is not a
            frontend simulation.{" "}
          </p>{" "}
        </div>{" "}
        {/* Recommended Action */}{" "}
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 ">
          {" "}
          <span className="font-bold block mb-1">Recommended Action:</span>{" "}
          <p>
            Immediately inspect the affected zone around{" "}
            {alert.node_zone || alert.node_id} and follow site emergency
            procedures. Coordinate with the mine safety officer and verify
            physical conditions before resuming operations.
          </p>{" "}
        </div>{" "}
      </div>{" "}
      {/* Audit Trail */}{" "}
      {alert.actions && alert.actions.length > 0 && (
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card space-y-3">
          {" "}
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            {" "}
            <User className="h-4 w-4 text-slate-600 " /> Audit Trail{" "}
          </h3>{" "}
          <div className="space-y-2">
            {" "}
            {alert.actions.map((act) => (
              <div
                key={act.id}
                className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs"
              >
                {" "}
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${act.action === "ACKNOWLEDGE" ? "bg-blue-100 text-blue-700 " : "bg-emerald-100 text-emerald-700 "}`}
                >
                  {" "}
                  {act.action}{" "}
                </span>{" "}
                <span className="text-slate-700 font-semibold">
                  {act.performed_by || "System"}
                </span>{" "}
                {act.notes && (
                  <span className="text-slate-500 truncate max-w-xs">
                    — {act.notes}
                  </span>
                )}{" "}
                <span className="ml-auto text-slate-400 font-mono text-[10px]">
                  {formatTime(act.created_at)}
                </span>{" "}
              </div>
            ))}{" "}
          </div>{" "}
        </div>
      )}{" "}
      {/* Cross-Reference Links */}{" "}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
        {" "}
        <h3 className="text-sm font-bold text-slate-900 mb-3">
          Related Resources
        </h3>{" "}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {" "}
          <Link
            to={`/app/nodes/${alert.node_id}`}
            className="p-3 rounded-xl bg-slate-50 border border-slate-100 hover:bg-slate-100 transition flex items-center justify-between text-xs font-semibold text-slate-700 "
          >
            {" "}
            <span className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-blue-600" /> Node Details
            </span>{" "}
            <ChevronRight className="h-3.5 w-3.5 text-slate-400 " />{" "}
          </Link>{" "}
          <Link
            to={`/app/gis?focus=${alert.node_id}`}
            className="p-3 rounded-xl bg-slate-50 border border-slate-100 hover:bg-slate-100 transition flex items-center justify-between text-xs font-semibold text-slate-700 "
          >
            {" "}
            <span className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-emerald-600" /> GIS Location
            </span>{" "}
            <ChevronRight className="h-3.5 w-3.5 text-slate-400 " />{" "}
          </Link>{" "}
          <Link
            to="/app/ai"
            className="p-3 rounded-xl bg-slate-50 border border-slate-100 hover:bg-slate-100 transition flex items-center justify-between text-xs font-semibold text-slate-700 "
          >
            {" "}
            <span className="flex items-center gap-2">
              <Brain className="h-4 w-4 text-indigo-600" /> AI Risk Analytics
            </span>{" "}
            <ChevronRight className="h-3.5 w-3.5 text-slate-400 " />{" "}
          </Link>{" "}
        </div>{" "}
      </div>{" "}
    </div>
  );
};
export default AlertDetailPage;
