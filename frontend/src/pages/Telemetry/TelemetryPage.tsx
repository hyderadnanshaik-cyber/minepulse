import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Activity,
  RefreshCw,
  Search,
  Cpu,
  Compass,
  Zap,
  Clock,
  ChevronRight
} from 'lucide-react';
import { apiClient } from '../../services/api/apiClient';
import { SensorReading, Node } from '../../types';
import { Link } from 'react-router-dom';

export const TelemetryPage: React.FC = () => {
  const { t } = useTranslation();
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [selectedStation, setSelectedStation] = useState<string>('all');
  const [activeMetricTab, setActiveMetricTab] = useState<'ALL' | 'DISPLACEMENT' | 'TILT' | 'VIBRATION' | 'CRACK'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchTelemetry = async () => {
    setLoading(true);
    try {
      const [telRes, nodeRes] = await Promise.all([
        apiClient.get('/telemetry?limit=50'),
        apiClient.get('/nodes')
      ]);
      setReadings(Array.isArray(telRes.data) ? telRes.data : []);
      setNodes(Array.isArray(nodeRes.data) ? nodeRes.data : []);
    } catch {
      // Best-effort
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 4000);
    return () => clearInterval(interval);
  }, []);

  const filteredReadings = readings.filter((r) => {
    const nodeMatch = selectedStation === 'all' || String(r.node_id) === selectedStation || r.node_code === selectedStation;
    const searchMatch = !searchQuery.trim() || String(r.node_code || r.node_id).toLowerCase().includes(searchQuery.toLowerCase());
    return nodeMatch && searchMatch;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="p-3.5 bg-blue-50 text-blue-600 rounded-xl">
            <Activity className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">{t('telemetry.title')}</h1>
            <p className="text-xs text-slate-500 mt-0.5">Real-time geotechnical sensor stream, tilt dynamics, and displacement telemetry</p>
          </div>
        </div>

        <button
          onClick={fetchTelemetry}
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl transition flex items-center gap-2"
        >
          <RefreshCw className={loading ? 'h-3.5 w-3.5 animate-spin' : 'h-3.5 w-3.5'} /> {t('common.refresh')}
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-card flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Station code..."
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <select
            value={selectedStation}
            onChange={(e) => setSelectedStation(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-700 font-bold focus:outline-none"
          >
            <option value="all">All Stations ({nodes.length})</option>
            {nodes.map((n) => (
              <option key={n.id} value={n.node_code || String(n.node_id)}>
                {n.name || ('Station ' + (n.node_code || n.node_id))}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Telemetry Stream Table */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Cpu className="h-4 w-4 text-blue-600" /> Live Ingest Stream
          </h3>
          <span className="text-xs text-slate-400 font-mono">Latest {filteredReadings.length} records</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px]">
                <th className="py-3 px-4">Station</th>
                <th className="py-3 px-4">Recorded At</th>
                <th className="py-3 px-4">Displacement</th>
                <th className="py-3 px-4">Tilt X / Y</th>
                <th className="py-3 px-4">Crack Opening</th>
                <th className="py-3 px-4">Vibration</th>
                <th className="py-3 px-4">Battery</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {filteredReadings.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400 font-sans">
                    No telemetry records available for the selected station.
                  </td>
                </tr>
              ) : (
                filteredReadings.map((r, i) => (
                  <tr key={i} className="hover:bg-slate-50 transition">
                    <td className="py-3 px-4 font-bold text-slate-900">{r.node_code || ('NODE_' + r.node_id)}</td>
                    <td className="py-3 px-4 text-slate-500">{r.timestamp || r.recorded_at || 'Live'}</td>
                    <td className="py-3 px-4 font-bold text-blue-600">{(Number(r.displacement ?? 0.12)).toFixed(2)} mm</td>
                    <td className="py-3 px-4 text-slate-700">{(Number(r.tilt_x ?? 0.30)).toFixed(2)}°</td>
                    <td className="py-3 px-4 text-slate-700">{(Number(r.crack_width ?? 0.0)).toFixed(2)} mm</td>
                    <td className="py-3 px-4 text-slate-700">{(Number(r.vibration ?? 0.02)).toFixed(3)} g</td>
                    <td className="py-3 px-4 text-emerald-600 font-bold">{r.battery_level || 95}%</td>
                    <td className="py-3 px-4 text-right font-sans">
                      <Link
                        to={'/app/nodes/' + (r.node_code || r.node_id)}
                        className="text-xs font-bold text-blue-600 hover:underline inline-flex items-center gap-0.5"
                      >
                        Inspect <ChevronRight className="h-3 w-3" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default TelemetryPage;
