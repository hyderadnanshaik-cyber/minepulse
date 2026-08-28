import React, { useEffect, useState } from 'react';
import { ShieldAlert, Wifi, WifiOff, Mail, Smartphone, Server, Database, CheckCircle2, Clock, XCircle, RefreshCw, RefreshCcw } from 'lucide-react';
import { apiClient } from '../../services/api/apiClient';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';

export const NotificationsPage: React.FC = () => {
  const [connectivity, setConnectivity] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [testStatus, setTestStatus] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [connRes, histRes] = await Promise.all([
        apiClient.get('/notifications/connectivity'),
        apiClient.get('/notifications/history')
      ]);
      setConnectivity(connRes.data);
      setHistory(histRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTestAlert = async () => {
    setTestStatus("Dispatching test alert...");
    try {
      const res = await apiClient.post('/notifications/test', {
        name: "Test User",
        message: "This is a manual test alert to verify the offline-first queue mechanism.",
        severity: "CRITICAL"
      });
      setTestStatus(`Test result: ${res.data.message}`);
      fetchData();
    } catch (e) {
      setTestStatus("Failed to run test.");
    }
  };

  const processQueue = async () => {
    try {
      await apiClient.post('/notifications/process-queue');
      setTimeout(fetchData, 2000);
    } catch (e) {}
  };

  if (loading && !connectivity) {
    return <LoadingSpinner size="lg" label="Loading connectivity status..." />;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-red-600" />
            Alert Notification System
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage connectivity, delivery queues, and alert escalation history.
          </p>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={fetchData}
            className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-200 flex items-center gap-2"
          >
            <RefreshCcw className="w-4 h-4" /> Refresh
          </button>
          <button 
            onClick={handleTestAlert}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            Run Test Alert
          </button>
        </div>
      </div>

      {testStatus && (
        <div className="bg-blue-50 border border-blue-200 text-blue-800 p-4 rounded-xl text-sm font-medium">
          {testStatus}
        </div>
      )}

      {/* Connectivity Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatusCard 
          icon={connectivity?.internet_online ? <Wifi className="text-green-500" /> : <WifiOff className="text-red-500" />}
          title="Internet Connection"
          status={connectivity?.internet_online ? "ONLINE" : "OFFLINE"}
          online={connectivity?.internet_online}
        />
        <StatusCard 
          icon={<Smartphone className={connectivity?.cellular_available ? "text-green-500" : "text-red-500"} />}
          title="Cellular Network"
          status={connectivity?.cellular_available ? "AVAILABLE" : "UNAVAILABLE"}
          online={connectivity?.cellular_available}
        />
        <StatusCard 
          icon={<Server className={connectivity?.gateway_online ? "text-green-500" : "text-red-500"} />}
          title="Gateway Health"
          status={connectivity?.gateway_online ? "ONLINE" : "OFFLINE"}
          online={connectivity?.gateway_online}
        />
        <StatusCard 
          icon={<Mail className={connectivity?.email_reachable ? "text-green-500" : "text-red-500"} />}
          title="EmailJS Service"
          status={connectivity?.email_reachable ? "REACHABLE" : "UNREACHABLE"}
          online={connectivity?.email_reachable}
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <h2 className="font-bold text-slate-800">Notification History & Queue</h2>
          <button 
            onClick={processQueue}
            className="text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            <RefreshCw className="w-4 h-4" /> Force Queue Process
          </button>
        </div>
        <div className="divide-y divide-slate-200 max-h-[600px] overflow-y-auto">
          {history.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-sm">No notification history found.</div>
          ) : (
            history.map((item, i) => (
              <div key={i} className="p-4 hover:bg-slate-50 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${item.type === 'EMAIL' ? 'bg-purple-100 text-purple-700' : 'bg-orange-100 text-orange-700'}`}>
                      {item.type}
                    </span>
                    <span className="text-sm font-semibold text-slate-700">{item.recipient}</span>
                  </div>
                  <div className="text-xs text-slate-500 mt-1 line-clamp-1">{item.subject}</div>
                  <div className="text-[10px] text-slate-400 mt-1">Alert ID: {item.alert_id || 'TEST'} • Last attempt: {new Date(item.last_attempt || item.created_at).toLocaleString()}</div>
                </div>
                <div className="text-right">
                  <StatusBadge status={item.status} />
                  <div className="text-[10px] text-slate-400 mt-1">Retries: {item.retry_count}</div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

const StatusCard = ({ icon, title, status, online }: { icon: any, title: string, status: string, online: boolean }) => (
  <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 flex items-center gap-4">
    <div className={`p-3 rounded-lg ${online ? 'bg-green-50' : 'bg-red-50'}`}>
      {icon}
    </div>
    <div>
      <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">{title}</p>
      <p className={`font-bold ${online ? 'text-green-700' : 'text-red-700'}`}>{status}</p>
    </div>
  </div>
);

const StatusBadge = ({ status }: { status: string }) => {
  if (status === 'SENT' || status === 'DELIVERED') {
    return <span className="inline-flex items-center gap-1 text-xs font-semibold text-green-700 bg-green-50 px-2 py-1 rounded"><CheckCircle2 className="w-3 h-3"/> {status}</span>;
  }
  if (status.includes('WAITING') || status === 'QUEUED' || status === 'PENDING') {
    return <span className="inline-flex items-center gap-1 text-xs font-semibold text-amber-700 bg-amber-50 px-2 py-1 rounded"><Clock className="w-3 h-3"/> {status}</span>;
  }
  return <span className="inline-flex items-center gap-1 text-xs font-semibold text-red-700 bg-red-50 px-2 py-1 rounded"><XCircle className="w-3 h-3"/> {status}</span>;
};
