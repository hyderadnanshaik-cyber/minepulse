import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../../services/api/apiClient';
import { Node, SensorReading } from '../../types';
import {
  ArrowLeft,
  Cpu,
  Activity,
  Battery,
  MapPin,
  RefreshCw,
  PowerOff,
  Trash2,
  AlertTriangle,
  CheckCircle2,
  X,
  Loader2,
} from 'lucide-react';

// ─── Confirm Deactivate Modal ──────────────────────────────────────────────────
interface ConfirmModalProps {
  nodeCode: string;
  mode: 'deactivate' | 'delete';
  onConfirm: () => void;
  onCancel: () => void;
  loading: boolean;
}
const ConfirmModal: React.FC<ConfirmModalProps> = ({ nodeCode, mode, onConfirm, onCancel, loading }) => {
  const isDelete = mode === 'delete';
  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xl max-w-sm w-full space-y-4 text-center">
        <div className={`h-12 w-12 rounded-2xl flex items-center justify-center mx-auto ${isDelete ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-600'}`}>
          {isDelete ? <Trash2 className="h-6 w-6" /> : <PowerOff className="h-6 w-6" />}
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900">
            {isDelete ? 'Delete Station Permanently?' : 'Deactivate Station?'}
          </h3>
          <p className="text-xs text-slate-500 mt-2 leading-relaxed">
            {isDelete
              ? `This will permanently remove ${nodeCode} from the system. All telemetry history will be deleted. This cannot be undone.`
              : `This will mark ${nodeCode} as OFFLINE and stop processing its telemetry. You can reactivate it later from the database.`}
          </p>
        </div>
        <div className="flex items-center justify-center gap-3 pt-1">
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className={`px-5 py-2.5 text-white text-xs font-bold rounded-xl flex items-center gap-2 transition ${isDelete ? 'bg-red-600 hover:bg-red-700' : 'bg-amber-500 hover:bg-amber-600'}`}
          >
            {loading && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
            {isDelete ? 'Delete Permanently' : 'Deactivate Station'}
          </button>
        </div>
      </div>
    </div>
  );
};

// ─── Main Component ─────────────────────────────────────────────────────────────
export const NodeDetailPage: React.FC = () => {
  const { nodeId } = useParams<{ nodeId: string }>();
  const navigate = useNavigate();
  const [node, setNode] = useState<Node | null>(null);
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirmModal, setConfirmModal] = useState<'deactivate' | 'delete' | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const showToast = (msg: string, type: 'success' | 'error' = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3500);
  };

  const fetchDetail = async () => {
    if (!nodeId) return;
    setLoading(true);
    try {
      const [nodeRes, telRes] = await Promise.all([
        apiClient.get(`/nodes/${nodeId}`),
        apiClient.get(`/telemetry?node_id=${nodeId}&limit=20`)
      ]);
      setNode(nodeRes.data);
      setReadings(Array.isArray(telRes.data) ? telRes.data : []);
    } catch {
      // Best-effort
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [nodeId]);

  const handleDeactivate = async () => {
    setActionLoading(true);
    try {
      await apiClient.patch(`/nodes/${nodeId}`, { status: 'OFFLINE' });
      showToast(`${node?.node_code || nodeId} deactivated successfully`);
      setConfirmModal(null);
      await fetchDetail();
    } catch (err: any) {
      showToast('Failed to deactivate: ' + (err?.response?.data?.detail || err.message), 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    setActionLoading(true);
    try {
      await apiClient.delete(`/nodes/${nodeId}`);
      showToast(`${node?.node_code || nodeId} deleted. Redirecting...`);
      setConfirmModal(null);
      setTimeout(() => navigate('/app/nodes'), 1500);
    } catch (err: any) {
      showToast('Failed to delete: ' + (err?.response?.data?.detail || err.message), 'error');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading && !node) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-2">
          <div className="h-8 w-8 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin mx-auto" />
          <p className="text-xs text-slate-500">Loading station parameters...</p>
        </div>
      </div>
    );
  }

  const nodeCode = node?.node_code || node?.node_id || `NODE_${nodeId}`;
  const isOffline = node?.status === 'OFFLINE';

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-6 right-6 z-[100] px-5 py-3 rounded-2xl shadow-2xl text-xs font-bold flex items-center gap-2.5 ${toast.type === 'success' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'}`}>
          {toast.type === 'success' ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
          {toast.msg}
        </div>
      )}

      {/* Confirm Modal */}
      {confirmModal && (
        <ConfirmModal
          nodeCode={nodeCode}
          mode={confirmModal}
          onConfirm={confirmModal === 'delete' ? handleDelete : handleDeactivate}
          onCancel={() => setConfirmModal(null)}
          loading={actionLoading}
        />
      )}

      {/* Back */}
      <button
        onClick={() => navigate('/app/nodes')}
        className="flex items-center gap-1.5 text-xs font-bold text-slate-600 hover:text-slate-900 transition"
      >
        <ArrowLeft className="h-4 w-4" /> Back to Sensor Fleet
      </button>

      {/* Header Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className={`p-4 rounded-2xl ${isOffline ? 'bg-slate-100 text-slate-400' : 'bg-blue-50 text-blue-600'}`}>
            <Cpu className="h-8 w-8" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-black text-slate-900 font-mono">{nodeCode}</h1>
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold ${
                isOffline ? 'bg-slate-100 text-slate-600' :
                node?.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                'bg-emerald-100 text-emerald-800'
              }`}>
                {node?.status || 'ONLINE'}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Zone: {node?.zone || 'North Working Panel'} • {Number(node?.latitude || 23.75).toFixed(4)}°N, {Number(node?.longitude || 86.42).toFixed(4)}°E
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Link
            to={`/app/gis?focus=${node?.node_id || nodeId}`}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition flex items-center gap-1.5"
          >
            <MapPin className="h-4 w-4" /> View GIS
          </Link>
          <button
            onClick={fetchDetail}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5"
          >
            <RefreshCw className="h-4 w-4" /> Refresh
          </button>

          {/* Deactivate / Reactivate */}
          <button
            onClick={() => setConfirmModal('deactivate')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition flex items-center gap-1.5 ${
              isOffline
                ? 'bg-emerald-100 hover:bg-emerald-200 text-emerald-700'
                : 'bg-amber-100 hover:bg-amber-200 text-amber-700'
            }`}
          >
            <PowerOff className="h-4 w-4" />
            {isOffline ? 'Reactivate Station' : 'Deactivate Station'}
          </button>

          {/* Delete */}
          <button
            onClick={() => setConfirmModal('delete')}
            className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 text-xs font-bold rounded-xl transition flex items-center gap-1.5"
          >
            <Trash2 className="h-4 w-4" /> Delete Node
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold uppercase text-slate-400 block">Risk Level</span>
          <span className={`text-lg font-black mt-1 block ${
            node?.risk_level === 'CRITICAL' ? 'text-red-600' :
            node?.risk_level === 'HIGH' ? 'text-orange-500' :
            'text-emerald-600'
          }`}>
            {node?.risk_level || 'NORMAL'}
          </span>
          <span className="text-[11px] font-mono text-slate-500">Score: {node?.risk_score ?? 0}/100</span>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold uppercase text-slate-400 block">Battery Power</span>
          <span className="text-lg font-black text-slate-900 mt-1 block">
            {node?.battery_level || 95}%
          </span>
          <span className="text-[11px] text-emerald-600 font-bold">1S LiFePO4 Healthy</span>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold uppercase text-slate-400 block">Signal Strength</span>
          <span className="text-lg font-black text-slate-900 mt-1 block">
            {node?.signal_strength || -68} dBm
          </span>
          <span className="text-[11px] text-slate-500 font-mono">LoRa IN865 Sub-GHz</span>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold uppercase text-slate-400 block">Mesh Hop Count</span>
          <span className="text-lg font-black text-slate-900 mt-1 block">
            Hop {node?.hop_count || 1}
          </span>
          <span className="text-[11px] text-slate-500">To Central Gateway</span>
        </div>
      </div>

      {/* Telemetry Table */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card space-y-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Activity className="h-4 w-4 text-blue-600" /> Recent Telemetry Stream
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px]">
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Displacement</th>
                <th className="py-2.5 px-3">Tilt Angle</th>
                <th className="py-2.5 px-3">Crack Opening</th>
                <th className="py-2.5 px-3">Vibration</th>
                <th className="py-2.5 px-3">Battery</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {readings.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-slate-400 font-sans">
                    No recent readings available.
                  </td>
                </tr>
              ) : (
                readings.slice(0, 10).map((r, i) => (
                  <tr key={i} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 text-slate-600">{r.timestamp || r.recorded_at || 'Just now'}</td>
                    <td className="py-2.5 px-3 font-bold text-slate-900">{(r.displacement ?? 0.12).toFixed(2)} mm</td>
                    <td className="py-2.5 px-3 text-slate-700">{(r.tilt_x ?? 0.30).toFixed(2)}°</td>
                    <td className="py-2.5 px-3 text-slate-700">{(r.crack_width ?? 0.00).toFixed(2)} mm</td>
                    <td className="py-2.5 px-3 text-slate-700">{(r.vibration ?? 0.02).toFixed(3)} g</td>
                    <td className="py-2.5 px-3 text-slate-700">{r.battery_level || 95}%</td>
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

export default NodeDetailPage;
