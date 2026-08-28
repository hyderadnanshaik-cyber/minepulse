import React, { useState, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, Link } from 'react-router-dom';
import {
  Cpu,
  Plus,
  Search,
  RefreshCw,
  MapPin,
  Activity,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Radio,
  SlidersHorizontal,
  ChevronRight,
  ShieldCheck,
  Zap,
  Clock
} from 'lucide-react';
import { apiClient } from '../../services/api/apiClient';
import { Node } from '../../types';
import { AddNodeModal } from '../../components/nodes/AddNodeModal';
import { EditNodeModal } from '../../components/nodes/EditNodeModal';
import { ArchiveNodeModal } from '../../components/nodes/ArchiveNodeModal';

export const NodesPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [nodes, setNodes] = useState<Node[]>([]);
  const [summary, setSummary] = useState({
    total_nodes: 0,
    online: 0,
    warning: 0,
    critical: 0,
    offline: 0
  });

  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'ONLINE' | 'WARNING' | 'CRITICAL' | 'OFFLINE'>('ALL');

  const [isAddOpen, setIsAddOpen] = useState(false);
  const [editNode, setEditNode] = useState<Node | null>(null);
  const [archiveNode, setArchiveNode] = useState<Node | null>(null);

  const fetchNodesAndSummary = async () => {
    setLoading(true);
    try {
      const [nodesRes, sumRes] = await Promise.all([
        apiClient.get('/nodes'),
        apiClient.get('/nodes/summary')
      ]);
      setNodes(nodesRes.data || []);
      setSummary(sumRes.data || { total_nodes: 0, online: 0, warning: 0, critical: 0, offline: 0 });
    } catch {
      // Best-effort
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNodesAndSummary();
    const interval = setInterval(fetchNodesAndSummary, 5000);
    return () => clearInterval(interval);
  }, []);

  const filteredNodes = useMemo(() => {
    return nodes.filter((n) => {
      const matchesSearch =
        (n.node_code || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (n.name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (n.zone || '').toLowerCase().includes(searchQuery.toLowerCase());

      if (statusFilter === 'ALL') return matchesSearch;
      if (statusFilter === 'ONLINE') return matchesSearch && (n.status === 'ONLINE' || n.risk_level === 'NORMAL');
      if (statusFilter === 'WARNING') return matchesSearch && (n.risk_level === 'WATCH' || n.risk_level === 'WARNING' || n.risk_level === 'HIGH');
      if (statusFilter === 'CRITICAL') return matchesSearch && n.risk_level === 'CRITICAL';
      if (statusFilter === 'OFFLINE') return matchesSearch && n.status === 'OFFLINE';
      return matchesSearch;
    });
  }, [nodes, searchQuery, statusFilter]);

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2.5">
            <Cpu className="h-6 w-6 text-blue-600" />
            Sensor Nodes
          </h1>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            Monitor, configure and manage geotechnical monitoring stations.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={fetchNodesAndSummary}
            disabled={loading}
            className="px-3.5 py-2 rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 text-xs font-bold flex items-center gap-1.5 shadow-xs transition"
          >
            <RefreshCw className={loading ? 'h-3.5 w-3.5 animate-spin' : 'h-3.5 w-3.5'} />
            Refresh
          </button>
          <button
            onClick={() => setIsAddOpen(true)}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold flex items-center gap-1.5 shadow-sm transition"
          >
            <Plus className="h-4 w-4" />
            Add Node
          </button>
        </div>
      </div>

      {/* Dynamic Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase">Total Nodes</span>
            <div className="h-7 w-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <Cpu className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900 mt-2 font-mono">{summary.total_nodes}</div>
          <div className="text-[10px] text-slate-400 font-medium mt-0.5">Active Fleet Size</div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase">Online</span>
            <div className="h-7 w-7 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-emerald-600 mt-2 font-mono">{summary.online}</div>
          <div className="text-[10px] text-slate-400 font-medium mt-0.5">Healthy Communication</div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase">Warning</span>
            <div className="h-7 w-7 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <AlertTriangle className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-amber-600 mt-2 font-mono">{summary.warning}</div>
          <div className="text-[10px] text-slate-400 font-medium mt-0.5">Elevated Risk Movement</div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase">Critical</span>
            <div className="h-7 w-7 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
              <Zap className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-rose-600 mt-2 font-mono">{summary.critical}</div>
          <div className="text-[10px] text-slate-400 font-medium mt-0.5">Immediate Danger</div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase">Offline</span>
            <div className="h-7 w-7 rounded-lg bg-slate-100 text-slate-500 flex items-center justify-center">
              <Radio className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-500 mt-2 font-mono">{summary.offline}</div>
          <div className="text-[10px] text-slate-400 font-medium mt-0.5">No Heartbeat</div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-80">
          <Search className="h-4 w-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search stations, zones..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
        </div>

        {/* Status Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto">
          {(['ALL', 'ONLINE', 'WARNING', 'CRITICAL', 'OFFLINE'] as const).map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={
                statusFilter === st
                  ? 'px-3 py-1.5 rounded-lg text-xs font-bold transition bg-slate-900 text-white'
                  : 'px-3 py-1.5 rounded-lg text-xs font-bold transition bg-slate-100 text-slate-600 hover:bg-slate-200'
              }
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Sensor Node Grid Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredNodes.length === 0 ? (
          <div className="col-span-full p-12 bg-white rounded-2xl border border-slate-200 text-center">
            <Cpu className="h-10 w-10 text-slate-300 mx-auto mb-2" />
            <p className="text-xs font-bold text-slate-600">No monitoring stations found.</p>
            <p className="text-[11px] text-slate-400 mt-0.5">Try clearing filters or search query.</p>
          </div>
        ) : (
          filteredNodes.map((node) => {
            const isCrit = node.risk_level === 'CRITICAL';
            const isWarn = node.risk_level === 'HIGH' || node.risk_level === 'WARNING' || node.risk_level === 'WATCH';
            const isOff = node.status === 'OFFLINE';

            return (
              <div
                key={node.id}
                onClick={() => navigate('/app/nodes/' + (node.node_code || node.node_id))}
                className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs hover:shadow-md hover:border-slate-300 transition cursor-pointer flex flex-col justify-between space-y-4"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={
                      isCrit
                        ? 'p-2.5 rounded-xl bg-rose-50 text-rose-600'
                        : isWarn
                        ? 'p-2.5 rounded-xl bg-amber-50 text-amber-600'
                        : isOff
                        ? 'p-2.5 rounded-xl bg-slate-100 text-slate-500'
                        : 'p-2.5 rounded-xl bg-blue-50 text-blue-600'
                    }>
                      <Cpu className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-black text-slate-900 font-mono">
                        {node.name || ('Station ' + (node.node_code || node.node_id))}
                      </h3>
                      <p className="text-[11px] text-slate-500 font-medium">
                        {node.zone || 'North Working Panel'}
                      </p>
                    </div>
                  </div>

                  <span className={
                    isCrit
                      ? 'px-2.5 py-0.5 text-[10px] font-extrabold rounded-full bg-rose-100 text-rose-800'
                      : isWarn
                      ? 'px-2.5 py-0.5 text-[10px] font-extrabold rounded-full bg-amber-100 text-amber-800'
                      : isOff
                      ? 'px-2.5 py-0.5 text-[10px] font-extrabold rounded-full bg-slate-100 text-slate-600'
                      : 'px-2.5 py-0.5 text-[10px] font-extrabold rounded-full bg-emerald-100 text-emerald-800'
                  }>
                    {node.status || 'ONLINE'}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 p-3 rounded-xl bg-slate-50 border border-slate-100 text-center font-mono">
                  <div>
                    <span className="text-[9px] text-slate-400 uppercase font-bold block">Risk</span>
                    <span className="text-xs font-black text-slate-800">{node.risk_level || 'NORMAL'}</span>
                  </div>
                  <div>
                    <span className="text-[9px] text-slate-400 uppercase font-bold block">Battery</span>
                    <span className="text-xs font-black text-slate-800">{node.battery_level || 95}%</span>
                  </div>
                  <div>
                    <span className="text-[9px] text-slate-400 uppercase font-bold block">Hop</span>
                    <span className="text-xs font-black text-slate-800">#{node.hop_count || 1}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1 border-t border-slate-100 text-[11px]">
                  <span className="text-slate-400 flex items-center gap-1 font-mono">
                    <Clock className="h-3 w-3" />
                    {node.last_seen || 'Active'}
                  </span>
                  <span className="text-blue-600 font-bold flex items-center gap-0.5 hover:underline">
                    View Details <ChevronRight className="h-3.5 w-3.5" />
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Add / Edit / Archive Modals */}
      {isAddOpen && (
        <AddNodeModal
          isOpen={isAddOpen}
          onClose={() => setIsAddOpen(false)}
          onSuccess={fetchNodesAndSummary}
        />
      )}
      {editNode && (
        <EditNodeModal
          isOpen={!!editNode}
          node={editNode}
          onClose={() => setEditNode(null)}
          onSuccess={fetchNodesAndSummary}
        />
      )}
      {archiveNode && (
        <ArchiveNodeModal
          isOpen={!!archiveNode}
          node={archiveNode}
          onClose={() => setArchiveNode(null)}
          onSuccess={fetchNodesAndSummary}
        />
      )}
    </div>
  );
};

export default NodesPage;
