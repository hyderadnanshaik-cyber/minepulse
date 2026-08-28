import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../hooks/useAuth';
import { useAlertStore } from '../../store/alertStore';
import { apiClient } from '../../services/api/apiClient';
import { Node } from '../../types';
import { Link } from 'react-router-dom';
import {
  Radio,
  MapPin,
  FileText,
  Activity,
  Cpu,
  CheckCircle2,
  Brain,
  ShieldCheck,
  Server,
  RefreshCw,
  X,
  ChevronRight,
  Wifi,
  Battery,
  AlertOctagon,
  Play,
  Square,
  AlertTriangle,
  Flame,
  ArrowRight,
  Layers
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  CartesianGrid
} from 'recharts';

export const DashboardPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const { alerts } = useAlertStore();

  const [nodes, setNodes] = useState<Node[]>([]);
  const [selectedStation, setSelectedStation] = useState<string>('all');
  const [waveformData, setWaveformData] = useState<{ time: string; value: number; disp: number; tilt: number }[]>([]);
  const [currentMetric, setCurrentMetric] = useState<{ composite: number; disp: number; tilt: number; vib: number }>({
    composite: 0.92,
    disp: 0.12,
    tilt: 0.30,
    vib: 0.04
  });
  const [spatialData, setSpatialData] = useState<any>(null);
  const [simStatus, setSimStatus] = useState<{ running: boolean; scenario: string | null; step: number; total_steps: number }>({
    running: false,
    scenario: null,
    step: 0,
    total_steps: 4
  });
  const [simLoading, setSimLoading] = useState(false);

  const [summary, setSummary] = useState({
    total_nodes: 0,
    online: 0,
    warning: 0,
    critical: 0,
    offline: 0
  });

  const today = new Date().toLocaleDateString(
    i18n.language === 'hi' ? 'hi-IN' : i18n.language === 'ur' ? 'ur-PK' : 'en-US',
    { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  );

  const fetchData = async () => {
    try {
      const [nodesRes, sumRes, telRes, spatialRes, simRes] = await Promise.all([
        apiClient.get('/nodes'),
        apiClient.get('/nodes/summary'),
        apiClient.get('/telemetry?limit=30'),
        apiClient.get('/ai/spatial-analysis').catch(() => ({ data: null })),
        apiClient.get('/simulation/status').catch(() => ({ data: null }))
      ]);

      const fetchedNodes: Node[] = nodesRes.data || [];
      const fetchedSummary = sumRes.data || { total_nodes: 0, online: 0, warning: 0, critical: 0, offline: 0 };
      const fetchedTelemetry: any[] = telRes.data || [];

      setNodes(fetchedNodes);
      setSummary(fetchedSummary);

      if (spatialRes?.data) {
        setSpatialData(spatialRes.data);
      }
      if (simRes?.data) {
        setSimStatus({
          running: simRes.data.running || false,
          scenario: simRes.data.scenario,
          step: simRes.data.step || 0,
          total_steps: simRes.data.total_steps || 4
        });
      }

      if (Array.isArray(fetchedTelemetry) && fetchedTelemetry.length > 0) {
        const filtered = selectedStation === 'all'
          ? fetchedTelemetry
          : fetchedTelemetry.filter((r) => String(r.node_id) === selectedStation || r.node_code === selectedStation);

        const activeList = filtered.length > 0 ? filtered : fetchedTelemetry;
        const latest = activeList[0];
        const disp = Number(latest.displacement ?? latest.displacement_mm ?? 0.12);
        const tilt = Number(latest.tilt ?? latest.tilt_x ?? 0.30);
        const vib = Number(latest.vibration ?? 0.04);
        const composite = Math.sqrt(disp * disp + tilt * tilt) || 0.92;

        setCurrentMetric({
          composite: parseFloat(composite.toFixed(2)),
          disp: parseFloat(disp.toFixed(2)),
          tilt: parseFloat(tilt.toFixed(2)),
          vib: parseFloat(vib.toFixed(2))
        });

        const points = activeList.slice(0, 16).reverse().map((r, idx) => {
          const d = Number(r.displacement ?? r.displacement_mm ?? 0.8 + Math.sin(idx * 0.5) * 0.3);
          const tl = Number(r.tilt ?? r.tilt_x ?? 0.3);
          const tVal = r.timestamp ? new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : `T-${16 - idx}s`;
          return {
            time: tVal,
            value: parseFloat(d.toFixed(2)),
            disp: parseFloat(d.toFixed(2)),
            tilt: parseFloat(tl.toFixed(2))
          };
        });
        setWaveformData(points);
      }
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, [selectedStation]);

  const handleStartSimulation = async (scenario: string) => {
    setSimLoading(true);
    try {
      await apiClient.post('/simulation/start', { scenario, interval_seconds: 3 });
      await fetchData();
    } catch (err) {
      console.error('Failed to start simulation:', err);
    } finally {
      setSimLoading(false);
    }
  };

  const handleStopSimulation = async () => {
    try {
      await apiClient.post('/simulation/stop');
      await fetchData();
    } catch (err) {
      console.error('Failed to stop simulation:', err);
    }
  };

  const isEvacActive = Boolean(spatialData?.evacuation_active);
  const activeImpactZones = spatialData?.active_impact_zones || [];
  const primaryZone = activeImpactZones[0];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* ─── EVACUATION RECOMMENDATION BANNER ────────────────────────────── */}
      {isEvacActive && (
        <div className="p-5 bg-red-600 text-white rounded-3xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4 animate-in slide-in-from-top-4 border-2 border-red-400">
          <div className="flex items-start sm:items-center gap-3.5">
            <div className="p-3 bg-white/20 rounded-2xl animate-pulse shrink-0">
              <AlertOctagon className="h-7 w-7" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[10px] font-extrabold uppercase tracking-widest bg-white text-red-600 px-2.5 py-0.5 rounded-full">
                  MANDATORY DGMS EVACUATION ADVISORY
                </span>
                <span className="text-xs text-white/80 font-mono">
                  Trigger Station: {primaryZone?.node_id || 'NODE_03'}
                </span>
              </div>
              <h2 className="text-base sm:text-lg font-black mt-1">
                Hazardous Subsidence Propagation Detected in Working Panel
              </h2>
              <p className="text-xs text-white/90 mt-0.5 max-w-2xl font-medium">
                {primaryZone?.recommended_action ||
                  'Correlated ground movement detected across adjacent stations. Evacuate all personnel from the predicted impact perimeter immediately.'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 self-end md:self-center shrink-0">
            <Link
              to="/app/gis"
              className="px-4 py-2.5 bg-white text-red-600 hover:bg-slate-100 text-xs font-bold rounded-xl whitespace-nowrap transition shadow-sm flex items-center gap-1.5"
            >
              <MapPin className="h-4 w-4" /> Inspect Impact Zone on GIS
            </Link>
          </div>
        </div>
      )}

      {/* ─── TOP WELCOME & METRICS ────────────────────────────────────────── */}
      <div className="bg-white rounded-3xl p-6 sm:p-7 border border-slate-200 shadow-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200">
              COMMAND & CONTROL
            </span>
            <span className="text-xs text-slate-400 font-medium">• {today}</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 mt-1 tracking-tight">
            Mine Safety Command Center
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Sub-millimeter strata movement, real-time kinematic derivatives, and AI subsidence early warning.
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          <Link
            to="/app/gis"
            className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold rounded-xl transition flex items-center gap-1.5"
          >
            <MapPin className="h-4 w-4 text-emerald-600" />
            <span>GIS Map</span>
          </Link>

          <Link
            to="/app/alerts"
            className="px-4 py-2.5 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 text-xs font-bold rounded-xl transition flex items-center gap-1.5"
          >
            <ShieldCheck className="h-4 w-4 text-red-600" />
            <span>Alerts ({summary.critical + summary.warning})</span>
          </Link>
        </div>
      </div>

      {/* ─── KPI SUMMARY CARDS ────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5 sm:gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Total Fleet</span>
            <Cpu className="h-4 w-4 text-slate-400" />
          </div>
          <span className="text-2xl sm:text-3xl font-black text-slate-900 mt-1 block font-mono">{summary.total_nodes || nodes.length || 20}</span>
          <span className="text-[11px] text-slate-500 font-medium">Active Stations</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-emerald-500">Nominal / Online</span>
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          </div>
          <span className="text-2xl sm:text-3xl font-black text-emerald-600 mt-1 block font-mono">{summary.online}</span>
          <span className="text-[11px] text-emerald-700 font-bold">Stable Geotechnical Baseline</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-amber-500">Watch / Elevated</span>
            <Activity className="h-4 w-4 text-amber-500" />
          </div>
          <span className="text-2xl sm:text-3xl font-black text-amber-600 mt-1 block font-mono">{summary.warning}</span>
          <span className="text-[11px] text-amber-700 font-bold">5–20mm Thresholds</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-red-500">Critical Hazards</span>
            <AlertOctagon className="h-4 w-4 text-red-500" />
          </div>
          <span className="text-2xl sm:text-3xl font-black text-red-600 mt-1 block font-mono">{summary.critical}</span>
          <span className="text-[11px] text-red-600 font-bold">DGMS Alarm Action Active</span>
        </div>
      </div>

      {/* ─── SCENARIO SIMULATION CONTROL PANEL ───────────────────────────── */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-card space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
              <Activity className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                End-to-End Safety Simulation Suite (Database-Driven Ingestion)
              </h3>
              <p className="text-[11px] text-slate-500">
                Injects calibrated underground telemetry through the actual backend ingestion & ML pipeline to demonstrate propagation and alert generation.
              </p>
            </div>
          </div>

          {simStatus.running && (
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-800 border border-amber-200 rounded-lg text-xs font-bold">
                <span className="h-2 w-2 rounded-full bg-amber-500 animate-ping" />
                Step {simStatus.step} of {simStatus.total_steps}
              </span>
              <button
                onClick={handleStopSimulation}
                className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-lg transition flex items-center gap-1"
              >
                <Square className="h-3 w-3" /> Stop
              </button>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <button
            onClick={() => handleStartSimulation('SCENARIO_A_SINGLE_SUBSIDENCE')}
            disabled={simStatus.running || simLoading}
            className="p-4 rounded-2xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50/40 text-left transition flex flex-col justify-between space-y-2 disabled:opacity-50"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-900">Scenario A</span>
              <Play className="h-3.5 w-3.5 text-blue-600" />
            </div>
            <p className="text-[11px] text-slate-500 leading-snug">
              <strong>Progressive Single Sinking:</strong> Station 3 accelerates downward while neighbors remain stable.
            </p>
            <span className="text-[10px] font-bold text-blue-700 uppercase">Single Anomaly →</span>
          </button>

          <button
            onClick={() => handleStartSimulation('SCENARIO_B_CORRELATED_PROPAGATION')}
            disabled={simStatus.running || simLoading}
            className="p-4 rounded-2xl border border-red-200 bg-red-50/30 hover:border-red-400 hover:bg-red-50 text-left transition flex flex-col justify-between space-y-2 disabled:opacity-50"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-red-900">Scenario B (Primary Test)</span>
              <Flame className="h-3.5 w-3.5 text-red-600" />
            </div>
            <p className="text-[11px] text-red-800/80 leading-snug">
              <strong>Multi-Node Propagation:</strong> Station 3 sinks, triggering correlated deterioration at Station 2. Triggers Evacuation.
            </p>
            <span className="text-[10px] font-bold text-red-600 uppercase">Evacuation Propagation →</span>
          </button>

          <button
            onClick={() => handleStartSimulation('SCENARIO_C_LOCALIZED_CRACK')}
            disabled={simStatus.running || simLoading}
            className="p-4 rounded-2xl border border-slate-200 hover:border-amber-400 hover:bg-amber-50/40 text-left transition flex flex-col justify-between space-y-2 disabled:opacity-50"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-900">Scenario C</span>
              <AlertTriangle className="h-3.5 w-3.5 text-amber-600" />
            </div>
            <p className="text-[11px] text-slate-500 leading-snug">
              <strong>Localized Crack:</strong> Station 4 fissure opening with stable tilt and displacement fleet-wide.
            </p>
            <span className="text-[10px] font-bold text-amber-700 uppercase">Crack Detection →</span>
          </button>

          <button
            onClick={() => handleStartSimulation('SCENARIO_D_NORMAL_BASELINE')}
            disabled={simStatus.running || simLoading}
            className="p-4 rounded-2xl border border-slate-200 hover:border-emerald-400 hover:bg-emerald-50/40 text-left transition flex flex-col justify-between space-y-2 disabled:opacity-50"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-900">Scenario D</span>
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
            </div>
            <p className="text-[11px] text-slate-500 leading-snug">
              <strong>Reset to Normal:</strong> All stations stream nominal baseline telemetry (&lt;0.5mm). Clears alarms.
            </p>
            <span className="text-[10px] font-bold text-emerald-700 uppercase">Normal Baseline →</span>
          </button>
        </div>
      </div>

      {/* ─── REAL-TIME WAVEFORM CHART & GATEWAY INFO ──────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-card space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Server className="h-4 w-4 text-blue-600" />
              <span className="text-xs font-bold text-slate-900">Raspberry Pi Edge Gateway</span>
            </div>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
              Online
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Hardware Profile</span>
              <span className="font-bold text-slate-800">Raspberry Pi Gateway</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Radio Mesh Band</span>
              <span className="font-bold text-slate-800">LoRa IN865 Sub-GHz</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Database & PostGIS</span>
              <span className="font-bold text-emerald-700">PostgreSQL (Synced)</span>
            </div>
            <div className="flex justify-between py-1.5">
              <span className="text-slate-500">MQTT Core</span>
              <span className="font-bold text-emerald-700">Mosquitto Connected</span>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[11px] text-slate-400 font-mono">Heartbeat: 30s</span>
            <Link to="/app/gateway" className="text-xs font-bold text-blue-600 hover:underline">
              Gateway Diagnostics →
            </Link>
          </div>
        </div>

        <div className="lg:col-span-2 bg-white rounded-3xl p-6 border border-slate-200 shadow-card space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3 flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-blue-600" />
              <span className="text-xs font-bold text-slate-900">Live Kinematic Strata Displacement Waveform</span>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={selectedStation}
                onChange={(e) => setSelectedStation(e.target.value)}
                className="px-2.5 py-1 bg-slate-50 border border-slate-200 rounded-lg text-xs font-mono text-slate-700 focus:outline-none"
              >
                <option value="all">All Fleet Combined</option>
                {nodes.slice(0, 10).map((n) => (
                  <option key={n.id} value={n.node_code || n.node_id}>
                    {n.node_code || n.node_id}
                  </option>
                ))}
              </select>
              <span className="text-xs font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-100">
                {currentMetric.disp} mm
              </span>
            </div>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={waveformData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={10} />
                <YAxis stroke="#94a3b8" fontSize={10} domain={[0, 35]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '0.75rem',
                    fontSize: '11px',
                    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
                  }}
                />
                <ReferenceLine y={5.0} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Watch (5mm)', fill: '#f59e0b', fontSize: 10 }} />
                <ReferenceLine y={25.0} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'DGMS Critical (25mm)', fill: '#ef4444', fontSize: 10 }} />
                <Area type="monotone" dataKey="value" stroke="#2563eb" fill="#3b82f6" fillOpacity={0.15} strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
