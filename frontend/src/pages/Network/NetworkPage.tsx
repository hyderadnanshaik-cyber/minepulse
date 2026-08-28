import React from 'react';
import { Radio, Server, Activity, Wifi, RefreshCw } from 'lucide-react';

export const NetworkPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="p-3.5 bg-blue-50 text-blue-600 rounded-xl">
            <Radio className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">LoRa Mesh Topology & Telemetry Fleet</h1>
            <p className="text-xs text-slate-500 mt-0.5">IN865 (865.2 MHz) Multi-Hop Underground Ad-Hoc Sensor Network</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Active Nodes</span>
          <span className="text-2xl font-black text-slate-900 mt-1 block">20 Stations</span>
          <span className="text-xs text-emerald-600 font-bold">100% Mesh Health</span>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Gateway Bridge</span>
          <span className="text-2xl font-black text-slate-900 mt-1 block">MINEGATE-01</span>
          <span className="text-xs text-slate-500">Raspberry Pi Zero 2 W</span>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Packet Delivery</span>
          <span className="text-2xl font-black text-slate-900 mt-1 block">99.8%</span>
          <span className="text-xs text-emerald-600 font-bold">Zero Data Loss Protocol</span>
        </div>
      </div>
    </div>
  );
};

export default NetworkPage;
