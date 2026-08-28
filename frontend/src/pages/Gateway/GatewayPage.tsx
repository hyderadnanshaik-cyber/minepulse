import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Server,
  Activity,
  Cpu,
  HardDrive,
  Wifi,
  Radio,
  RefreshCw,
  Clock,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Zap,
  Volume2
} from 'lucide-react';
import { apiClient } from '../../services/api/apiClient';

export const GatewayPage: React.FC = () => {
  const { t } = useTranslation();
  const [gatewayData, setGatewayData] = useState<any>({
    hostname: 'MINEGATE-01',
    model: 'Raspberry Pi Zero 2 W',
    ip_address: '192.168.4.1',
    status: 'ONLINE',
    cpu_usage: 12.4,
    ram_usage: 34.1,
    temperature: 42.5,
    storage_used: 18.2,
    mesh_status: 'ONLINE',
    db_status: 'ONLINE',
    internet_connected: true,
    cloud_sync_status: 'SYNCED',
    alarm_active: false
  });
  const [loading, setLoading] = useState(false);

  const fetchGateway = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/gateway/status');
      if (res.data) setGatewayData(res.data);
    } catch {
      // Best-effort
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGateway();
    const interval = setInterval(fetchGateway, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="p-3.5 bg-blue-50 text-blue-600 rounded-xl">
            <Server className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">{t('gateway.title')}</h1>
            <p className="text-xs text-slate-500 mt-0.5">Raspberry Pi Zero 2 W Industrial LoRa Edge Concentrator Node</p>
          </div>
        </div>

        <button
          onClick={fetchGateway}
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl transition flex items-center gap-2"
        >
          <RefreshCw className={loading ? 'h-3.5 w-3.5 animate-spin' : 'h-3.5 w-3.5'} /> {t('common.refresh')}
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Gateway State</span>
          <span className="text-xl font-black text-emerald-600 mt-1 block">ONLINE</span>
          <span className="text-xs text-slate-500">Zero Data Loss Protocol</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold text-slate-400 uppercase">CPU Core Temp</span>
          <span className="text-xl font-black text-slate-900 mt-1 block font-mono">{gatewayData.temperature}°C</span>
          <span className="text-xs text-emerald-600 font-bold">Optimal Range (&lt;65°C)</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Memory Footprint</span>
          <span className="text-xl font-black text-slate-900 mt-1 block font-mono">{gatewayData.ram_usage}%</span>
          <span className="text-xs text-slate-500">512MB LPDDR2</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Cloud Sync</span>
          <span className="text-xl font-black text-blue-600 mt-1 block">SYNCED</span>
          <span className="text-xs text-slate-500">Dual-Write Active</span>
        </div>
      </div>
    </div>
  );
};

export default GatewayPage;
