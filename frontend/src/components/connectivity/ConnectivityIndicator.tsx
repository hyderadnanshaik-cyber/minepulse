import React from 'react';
import { useConnectivity } from '../../hooks/useConnectivity';
import { Wifi, Radio, Server, Cloud } from 'lucide-react';

export const ConnectivityIndicator: React.FC = () => {
  const { status, isOnline } = useConnectivity();

  const renderStatusItem = (name: string, isOk: boolean, icon: React.ReactNode) => (
    <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-white border border-slate-200 text-xs">
      {icon}
      <span className="font-medium text-slate-700">{name}:</span>
      <span className={`h-2 w-2 rounded-full ${isOk ? 'bg-emerald-500' : 'bg-rose-500'}`} />
      <span className={`text-[11px] font-semibold ${isOk ? 'text-emerald-700' : 'text-rose-700'}`}>
        {isOk ? 'ONLINE' : 'OFFLINE'}
      </span>
    </div>
  );

  return (
    <div className="flex items-center gap-2">
      <div className="hidden sm:flex items-center gap-2">
        {renderStatusItem('LoRa Field', status.mesh_status === 'ONLINE', <Radio className="h-3.5 w-3.5 text-blue-600" />)}
        {renderStatusItem('MINEGATE', status.gateway_status === 'ONLINE', <Server className="h-3.5 w-3.5 text-indigo-600" />)}
        {renderStatusItem('Internet', isOnline, <Wifi className="h-3.5 w-3.5 text-slate-600" />)}
        {renderStatusItem('Cloud Sync', status.cloud_status === 'ONLINE', <Cloud className="h-3.5 w-3.5 text-sky-600" />)}
      </div>
    </div>
  );
};

export default ConnectivityIndicator;
