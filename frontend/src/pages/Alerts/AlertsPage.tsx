import React, { useState, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import {
  Bell,
  AlertTriangle,
  AlertOctagon,
  CheckCircle2,
  RefreshCw,
  Search,
  ChevronRight,
  Clock,
  Loader2,
} from 'lucide-react';
import { apiClient } from '../../services/api/apiClient';
import { Alert } from '../../types';

export const AlertsPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState<'ALL' | 'CRITICAL' | 'WARNING' | 'RESOLVED'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [actionLoading, setActionLoading] = useState<Record<number, string>>({});
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const showToast = (msg: string, type: 'success' | 'error' = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchAlerts = async () => {
    try {
      const res = await apiClient.get('/alerts?limit=100');
      const data = Array.isArray(res.data) ? res.data : (res.data?.alerts ?? []);
      setAlerts(data);
    } catch (err) {
      console.error('Error fetching alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleAcknowledge = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    setActionLoading((prev) => ({ ...prev, [id]: 'ack' }));
    // Optimistic update
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: 'ACKNOWLEDGED' as any } : a))
    );
    try {
      await apiClient.post('/alerts/' + id + '/acknowledge', {
        notes: 'Acknowledged from Safety Dashboard',
      });
      showToast('Alert acknowledged successfully');
      await fetchAlerts();
    } catch (err: any) {
      // Revert optimistic update
      setAlerts((prev) =>
        prev.map((a) => (a.id === id ? { ...a, status: 'DETECTED' as any } : a))
      );
      showToast('Failed to acknowledge: ' + (err?.response?.data?.detail || err.message), 'error');
    } finally {
      setActionLoading((prev) => {
        const next = { ...prev };
        delete next[id];
        return next;
      });
    }
  };

  const handleResolve = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    setActionLoading((prev) => ({ ...prev, [id]: 'resolve' }));
    // Optimistic update
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: 'RESOLVED' as any } : a))
    );
    try {
      await apiClient.post('/alerts/' + id + '/resolve', {
        notes: 'Resolved from Safety Dashboard after site inspection',
      });
      showToast('Alert resolved and closed');
      await fetchAlerts();
    } catch (err: any) {
      setAlerts((prev) =>
        prev.map((a) => (a.id === id ? { ...a, status: 'ACTIVE' as any } : a))
      );
      showToast('Failed to resolve: ' + (err?.response?.data?.detail || err.message), 'error');
    } finally {
      setActionLoading((prev) => {
        const next = { ...prev };
        delete next[id];
        return next;
      });
    }
  };

  const counts = useMemo(() => {
    const total = alerts.length;
    const critical = alerts.filter((a) => a.severity === 'CRITICAL' && a.status !== 'RESOLVED').length;
    const warning = alerts.filter((a) => (a.severity === 'WARNING' || a.severity === 'HIGH') && a.status !== 'RESOLVED').length;
    const resolved = alerts.filter((a) => a.status === 'RESOLVED').length;
    return { total, critical, warning, resolved };
  }, [alerts]);

  const filteredAlerts = useMemo(() => {
    return alerts.filter((a) => {
      if (filterSeverity === 'CRITICAL' && (a.severity !== 'CRITICAL' || a.status === 'RESOLVED')) return false;
      if (filterSeverity === 'WARNING' && (a.severity === 'CRITICAL' || a.status === 'RESOLVED')) return false;
      if (filterSeverity === 'RESOLVED' && a.status !== 'RESOLVED') return false;

      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesNode = String(a.node_code || a.node_id || '').toLowerCase().includes(q);
        const matchesMsg = (a.message || '').toLowerCase().includes(q);
        const matchesTitle = (a.title || '').toLowerCase().includes(q);
        return matchesNode || matchesMsg || matchesTitle;
      }
      return true;
    });
  }, [alerts, filterSeverity, searchQuery]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Toast Notification */}
      {toast && (
        <div
          className={`fixed top-6 right-6 z-[100] px-5 py-3 rounded-2xl shadow-2xl text-xs font-bold flex items-center gap-2.5 animate-in slide-in-from-top-4 transition ${
            toast.type === 'success'
              ? 'bg-emerald-600 text-white'
              : 'bg-red-600 text-white'
          }`}
        >
          {toast.type === 'success' ? (
            <CheckCircle2 className="h-4 w-4" />
          ) : (
            <AlertTriangle className="h-4 w-4" />
          )}
          {toast.msg}
        </div>
      )}

      {/* Header */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="p-3.5 bg-red-50 text-red-600 rounded-xl">
            <Bell className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">{t('alerts.title')}</h1>
            <p className="text-xs text-slate-500 mt-0.5">Real-time geotechnical risk incidents and statutory DGMS alert log</p>
          </div>
        </div>
        <button
          onClick={fetchAlerts}
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl transition flex items-center gap-2 self-start sm:self-auto"
        >
          <RefreshCw className={loading ? 'h-3.5 w-3.5 animate-spin' : 'h-3.5 w-3.5'} />
          {t('common.refresh')}
        </button>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <button
          onClick={() => setFilterSeverity('ALL')}
          className={filterSeverity === 'ALL' ? 'p-4 rounded-2xl border text-left transition bg-blue-50 border-blue-300 shadow-sm' : 'p-4 rounded-2xl border text-left transition bg-white border-slate-200 shadow-card hover:bg-slate-50'}
        >
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400 block">Total Logged</span>
          <span className="text-2xl font-black text-slate-900 mt-1 block">{counts.total}</span>
        </button>

        <button
          onClick={() => setFilterSeverity('CRITICAL')}
          className={filterSeverity === 'CRITICAL' ? 'p-4 rounded-2xl border text-left transition bg-red-50 border-red-300 shadow-sm' : 'p-4 rounded-2xl border text-left transition bg-white border-slate-200 shadow-card hover:bg-slate-50'}
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-red-500 block">Active Critical</span>
            {counts.critical > 0 && <span className="h-2 w-2 rounded-full bg-red-500 animate-ping" />}
          </div>
          <span className="text-2xl font-black text-red-600 mt-1 block">{counts.critical}</span>
        </button>

        <button
          onClick={() => setFilterSeverity('WARNING')}
          className={filterSeverity === 'WARNING' ? 'p-4 rounded-2xl border text-left transition bg-amber-50 border-amber-300 shadow-sm' : 'p-4 rounded-2xl border text-left transition bg-white border-slate-200 shadow-card hover:bg-slate-50'}
        >
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-amber-500 block">Active Warning</span>
          <span className="text-2xl font-black text-amber-600 mt-1 block">{counts.warning}</span>
        </button>

        <button
          onClick={() => setFilterSeverity('RESOLVED')}
          className={filterSeverity === 'RESOLVED' ? 'p-4 rounded-2xl border text-left transition bg-emerald-50 border-emerald-300 shadow-sm' : 'p-4 rounded-2xl border text-left transition bg-white border-slate-200 shadow-card hover:bg-slate-50'}
        >
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-emerald-500 block">Resolved</span>
          <span className="text-2xl font-black text-emerald-600 mt-1 block">{counts.resolved}</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-card flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Node ID, title, or message..."
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="flex items-center gap-1.5 w-full sm:w-auto">
          {(['ALL', 'CRITICAL', 'WARNING', 'RESOLVED'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilterSeverity(tab)}
              className={
                filterSeverity === tab
                  ? 'px-3 py-1.5 rounded-lg text-xs font-bold transition flex-1 sm:flex-none bg-slate-900 text-white'
                  : 'px-3 py-1.5 rounded-lg text-xs font-bold transition flex-1 sm:flex-none bg-slate-100 text-slate-600 hover:bg-slate-200'
              }
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {loading && alerts.length === 0 ? (
          <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-3" />
            <p className="text-xs text-slate-500 font-medium">Loading safety alerts...</p>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="bg-white rounded-2xl p-12 border border-slate-200 shadow-card text-center">
            <CheckCircle2 className="h-12 w-12 text-emerald-500 mx-auto mb-3" />
            <h3 className="text-base font-bold text-slate-800">{t('safety.safeStatus')}</h3>
            <p className="text-xs text-slate-500 mt-1">No alerts matching the selected filter criteria.</p>
          </div>
        ) : (
          filteredAlerts.map((a) => {
            const isCritical = a.severity === 'CRITICAL' && a.status !== 'RESOLVED';
            const isResolved = a.status === 'RESOLVED';
            const isAcknowledged = a.status === 'ACKNOWLEDGED';
            const actionKey = actionLoading[a.id];

            return (
              <div
                key={a.id}
                onClick={() => navigate('/app/alerts/' + a.id)}
                className={
                  isCritical
                    ? 'bg-white rounded-2xl p-5 border shadow-card hover:shadow-md transition cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 border-red-200 bg-red-50/30'
                    : isResolved
                    ? 'bg-white rounded-2xl p-5 border shadow-card hover:shadow-md transition cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 border-slate-200 opacity-80'
                    : isAcknowledged
                    ? 'bg-white rounded-2xl p-5 border shadow-card hover:shadow-md transition cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 border-blue-200 bg-blue-50/20'
                    : 'bg-white rounded-2xl p-5 border shadow-card hover:shadow-md transition cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 border-amber-200 bg-amber-50/30'
                }
              >
                <div className="flex items-start gap-3.5">
                  <div
                    className={
                      isCritical
                        ? 'p-2.5 rounded-xl mt-0.5 shrink-0 bg-red-100 text-red-700'
                        : isResolved
                        ? 'p-2.5 rounded-xl mt-0.5 shrink-0 bg-emerald-100 text-emerald-700'
                        : isAcknowledged
                        ? 'p-2.5 rounded-xl mt-0.5 shrink-0 bg-blue-100 text-blue-700'
                        : 'p-2.5 rounded-xl mt-0.5 shrink-0 bg-amber-100 text-amber-800'
                    }
                  >
                    {a.severity === 'CRITICAL' && !isResolved ? (
                      <AlertOctagon className="h-5 w-5" />
                    ) : isResolved ? (
                      <CheckCircle2 className="h-5 w-5" />
                    ) : (
                      <AlertTriangle className="h-5 w-5" />
                    )}
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        className={
                          isCritical
                            ? 'px-2.5 py-0.5 text-[10px] font-extrabold rounded-full bg-red-600 text-white'
                            : isResolved
                            ? 'px-2.5 py-0.5 text-[10px] font-extrabold rounded-full bg-emerald-600 text-white'
                            : isAcknowledged
                            ? 'px-2.5 py-0.5 text-[10px] font-extrabold rounded-full bg-blue-600 text-white'
                            : 'px-2.5 py-0.5 text-[10px] font-extrabold rounded-full bg-amber-500 text-white'
                        }
                      >
                        {isResolved ? 'RESOLVED' : isAcknowledged ? 'ACKNOWLEDGED' : a.severity}
                      </span>
                      <span className="font-mono text-xs font-bold text-slate-900">
                        {a.node_code || ('NODE_' + a.node_id)}
                      </span>
                      <span className="text-[11px] text-slate-400 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {a.detected_at || a.triggered_at}
                      </span>
                      {a.risk_score !== undefined && (
                        <span className="text-[11px] font-mono font-bold text-slate-500">
                          Risk: {Number(a.risk_score).toFixed(1)}
                        </span>
                      )}
                    </div>

                    <h4 className="font-bold text-slate-900 text-sm">
                      {a.title || t('safety.groundMovement')}
                    </h4>
                    <p className="text-xs text-slate-600 leading-relaxed max-w-2xl">
                      {a.message}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end md:self-center shrink-0">
                  {/* DETECTED or ACTIVE → show Acknowledge + Resolve */}
                  {(a.status === 'ACTIVE' || a.status === 'DETECTED') && (
                    <>
                      <button
                        onClick={(e) => handleAcknowledge(e, a.id)}
                        disabled={!!actionKey}
                        className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition flex items-center gap-1 disabled:opacity-50"
                      >
                        {actionKey === 'ack' ? (
                          <Loader2 className="h-3 w-3 animate-spin" />
                        ) : null}
                        {t('alerts.acknowledge')}
                      </button>
                      <button
                        onClick={(e) => handleResolve(e, a.id)}
                        disabled={!!actionKey}
                        className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg transition flex items-center gap-1 disabled:opacity-50"
                      >
                        {actionKey === 'resolve' ? (
                          <Loader2 className="h-3 w-3 animate-spin" />
                        ) : null}
                        {t('alerts.resolve')}
                      </button>
                    </>
                  )}

                  {/* ACKNOWLEDGED → only show Resolve */}
                  {a.status === 'ACKNOWLEDGED' && (
                    <button
                      onClick={(e) => handleResolve(e, a.id)}
                      disabled={!!actionKey}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg transition flex items-center gap-1 disabled:opacity-50"
                    >
                      {actionKey === 'resolve' ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : null}
                      {t('alerts.resolve')}
                    </button>
                  )}

                  {/* RESOLVED → show badge */}
                  {a.status === 'RESOLVED' && (
                    <span className="px-3 py-1 bg-emerald-50 text-emerald-700 text-xs font-bold rounded-lg border border-emerald-200">
                      {t('common.resolved')}
                    </span>
                  )}

                  <ChevronRight className="h-4 w-4 text-slate-400" />
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default AlertsPage;
