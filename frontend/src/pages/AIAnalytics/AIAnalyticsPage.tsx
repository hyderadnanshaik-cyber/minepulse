import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Brain,
  RefreshCw,
  Cpu,
  Activity,
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
  Zap,
  BarChart3,
  TrendingUp,
  Loader2,
} from 'lucide-react';
import { apiClient } from '../../services/api/apiClient';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  AreaChart,
  Area,
} from 'recharts';

const RISK_COLOR = (level: string) => {
  if (level === 'CRITICAL') return 'text-red-600';
  if (level === 'HIGH') return 'text-orange-500';
  if (level === 'WATCH') return 'text-amber-500';
  return 'text-emerald-600';
};

const RISK_BG = (level: string) => {
  if (level === 'CRITICAL') return 'bg-red-100 text-red-700 border-red-200';
  if (level === 'HIGH') return 'bg-orange-100 text-orange-700 border-orange-200';
  if (level === 'WATCH') return 'bg-amber-100 text-amber-700 border-amber-200';
  return 'bg-emerald-100 text-emerald-700 border-emerald-200';
};

export const AIAnalyticsPage: React.FC = () => {
  const { t } = useTranslation();
  const [predictions, setPredictions] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAI = async () => {
    setLoading(true);
    try {
      const [predRes, alertRes] = await Promise.all([
        apiClient.get('/ai/predictions?limit=30'),
        apiClient.get('/alerts?limit=10'),
      ]);
      const preds = Array.isArray(predRes.data) ? predRes.data : (predRes.data?.predictions ?? []);
      const alts = Array.isArray(alertRes.data) ? alertRes.data : (alertRes.data?.alerts ?? []);
      setPredictions(preds);
      setAlerts(alts);
    } catch {
      // Best-effort
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAI();
    const iv = setInterval(fetchAI, 15000);
    return () => clearInterval(iv);
  }, []);

  // Build chart data from predictions
  const chartData = predictions.slice(0, 20).map((p: any, i: number) => ({
    name: p.node_id || ('P' + (i + 1)),
    anomaly: Number(p.anomaly_score ?? 0).toFixed(3),
    risk: Number(p.risk_score ?? 0).toFixed(1),
    label: p.risk_level || 'NORMAL',
  })).reverse();

  const criticalCount = predictions.filter((p) => p.risk_level === 'CRITICAL').length;
  const highCount = predictions.filter((p) => p.risk_level === 'HIGH').length;
  const normalCount = predictions.filter((p) => p.risk_level === 'NORMAL' || !p.risk_level).length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="p-3.5 bg-purple-50 text-purple-600 rounded-xl">
            <Brain className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">{t('ai.title')}</h1>
            <p className="text-xs text-slate-500 mt-0.5">IsolationForest Anomaly Detector + DGMS Geotechnical Strata Risk Engine</p>
          </div>
        </div>
        <button
          onClick={fetchAI}
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl transition flex items-center gap-2"
        >
          <RefreshCw className={loading ? 'h-3.5 w-3.5 animate-spin' : 'h-3.5 w-3.5'} />
          {t('common.refresh')}
        </button>
      </div>

      {/* Model Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold text-slate-400 uppercase flex items-center gap-1.5"><Cpu className="h-3 w-3" /> ML Engine</span>
          <span className="text-base font-black text-slate-900 mt-1 block">IsolationForest v1.0</span>
          <span className="text-xs text-emerald-600 font-bold">Trained on Geotechnical Baselines</span>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold text-slate-400 uppercase flex items-center gap-1.5"><Zap className="h-3 w-3" /> Inference</span>
          <span className="text-base font-black text-slate-900 mt-1 block font-mono">1.2 ms</span>
          <span className="text-xs text-slate-500">Real-Time Continuous</span>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold text-slate-400 uppercase flex items-center gap-1.5"><BarChart3 className="h-3 w-3" /> Total Predictions</span>
          <span className="text-base font-black text-purple-600 mt-1 block font-mono">{loading ? '...' : predictions.length}</span>
          <span className="text-xs text-slate-500">Last 30 analysed</span>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold text-slate-400 uppercase flex items-center gap-1.5"><ShieldAlert className="h-3 w-3" /> DGMS Rules</span>
          <span className="text-base font-black text-purple-600 mt-1 block">Active</span>
          <span className="text-xs text-slate-500">Rate-of-Deformation Triggers</span>
        </div>
      </div>

      {/* Risk Distribution */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-red-50 border border-red-200 rounded-2xl p-5 flex items-center gap-4">
          <div className="p-3 bg-red-100 text-red-600 rounded-xl"><AlertTriangle className="h-6 w-6" /></div>
          <div>
            <span className="text-[10px] font-extrabold uppercase text-red-500 block">Critical Risk Nodes</span>
            <span className="text-3xl font-black text-red-600">{loading ? '—' : criticalCount}</span>
          </div>
        </div>
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 flex items-center gap-4">
          <div className="p-3 bg-amber-100 text-amber-600 rounded-xl"><TrendingUp className="h-6 w-6" /></div>
          <div>
            <span className="text-[10px] font-extrabold uppercase text-amber-500 block">Elevated Risk Nodes</span>
            <span className="text-3xl font-black text-amber-600">{loading ? '—' : highCount}</span>
          </div>
        </div>
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 flex items-center gap-4">
          <div className="p-3 bg-emerald-100 text-emerald-600 rounded-xl"><CheckCircle2 className="h-6 w-6" /></div>
          <div>
            <span className="text-[10px] font-extrabold uppercase text-emerald-500 block">Normal / Safe Nodes</span>
            <span className="text-3xl font-black text-emerald-600">{loading ? '—' : normalCount}</span>
          </div>
        </div>
      </div>

      {/* Anomaly Score Chart */}
      {chartData.length > 0 && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card space-y-3">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Activity className="h-4 w-4 text-purple-600" />
            Anomaly Score Timeline — Last 20 Inferences
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="anomalyGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" tick={{ fontSize: 9 }} />
              <YAxis domain={[0, 1]} tick={{ fontSize: 9 }} />
              <Tooltip
                contentStyle={{ fontSize: '11px', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                formatter={(v: any) => [Number(v).toFixed(3), 'Anomaly Score']}
              />
              <ReferenceLine y={0.65} stroke="#f59e0b" strokeDasharray="4 2" label={{ value: 'WATCH', position: 'insideRight', fontSize: 9, fill: '#f59e0b' }} />
              <ReferenceLine y={0.85} stroke="#ef4444" strokeDasharray="4 2" label={{ value: 'CRITICAL', position: 'insideRight', fontSize: 9, fill: '#ef4444' }} />
              <Area type="monotone" dataKey="anomaly" stroke="#7c3aed" strokeWidth={2} fill="url(#anomalyGrad)" dot={{ r: 2, fill: '#7c3aed' }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Predictions Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-card overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Brain className="h-4 w-4 text-purple-600" />
            Recent AI Inference Results
          </h3>
          <span className="text-xs text-slate-400 font-mono">{predictions.length} records</span>
        </div>
        {loading ? (
          <div className="p-10 text-center">
            <Loader2 className="h-7 w-7 animate-spin text-purple-600 mx-auto mb-2" />
            <p className="text-xs text-slate-400">Running inference pipeline...</p>
          </div>
        ) : predictions.length === 0 ? (
          <div className="p-10 text-center">
            <Brain className="h-10 w-10 text-slate-200 mx-auto mb-2" />
            <p className="text-xs text-slate-500 font-medium">No AI predictions yet.</p>
            <p className="text-[11px] text-slate-400 mt-1">Predictions are generated automatically when telemetry arrives from sensor nodes.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  <th className="px-5 py-3 text-left font-bold text-slate-500 uppercase tracking-wide">Node</th>
                  <th className="px-5 py-3 text-left font-bold text-slate-500 uppercase tracking-wide">Anomaly Score</th>
                  <th className="px-5 py-3 text-left font-bold text-slate-500 uppercase tracking-wide">Risk Score</th>
                  <th className="px-5 py-3 text-left font-bold text-slate-500 uppercase tracking-wide">Risk Level</th>
                  <th className="px-5 py-3 text-left font-bold text-slate-500 uppercase tracking-wide">Confidence</th>
                  <th className="px-5 py-3 text-left font-bold text-slate-500 uppercase tracking-wide">Model</th>
                  <th className="px-5 py-3 text-left font-bold text-slate-500 uppercase tracking-wide">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {predictions.map((p: any, i: number) => (
                  <tr key={i} className="hover:bg-slate-50/50 transition">
                    <td className="px-5 py-3 font-mono font-bold text-slate-900">{p.node_id || p.node_id_fk || '—'}</td>
                    <td className="px-5 py-3 font-mono text-purple-700 font-bold">{Number(p.anomaly_score ?? 0).toFixed(4)}</td>
                    <td className="px-5 py-3 font-mono text-slate-800">{Number(p.risk_score ?? 0).toFixed(1)}</td>
                    <td className="px-5 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold border ${RISK_BG(p.risk_level || 'NORMAL')}`}>
                        {p.risk_level || 'NORMAL'}
                      </span>
                    </td>
                    <td className="px-5 py-3 font-mono text-slate-600">
                      {p.confidence ? (Number(p.confidence) * 100).toFixed(1) + '%' : '—'}
                    </td>
                    <td className="px-5 py-3 text-slate-500">{p.model_version || 'IsolationForest v1.0'}</td>
                    <td className="px-5 py-3 text-slate-400 font-mono">{p.created_at || p.timestamp || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recent Alerts from AI */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-card overflow-hidden">
          <div className="p-5 border-b border-slate-100">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-red-500" />
              AI-Generated Safety Alerts (Latest 10)
            </h3>
          </div>
          <div className="divide-y divide-slate-50">
            {alerts.map((a: any) => (
              <div key={a.id} className="px-5 py-3.5 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold border ${RISK_BG(a.severity || 'NORMAL')}`}>
                    {a.severity}
                  </span>
                  <span className="font-mono text-xs font-bold text-slate-800">{a.node_code || a.node_id}</span>
                  <span className="text-xs text-slate-600 truncate max-w-xs">{a.title}</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono whitespace-nowrap">{a.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAnalyticsPage;
