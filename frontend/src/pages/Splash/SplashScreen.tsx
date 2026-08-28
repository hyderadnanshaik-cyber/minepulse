import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Activity, Radio } from 'lucide-react';
import { LanguageSelector } from '../../components/ui/LanguageSelector';

export const SplashScreen: React.FC = () => {
  const navigate = useNavigate();
  const [statusMessage, setStatusMessage] = useState('Initializing telemetry subsystem...');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const start = Date.now();
    const duration = 1200;
    const interval = setInterval(() => {
      const elapsed = Date.now() - start;
      const pct = Math.min(100, Math.floor((elapsed / duration) * 100));
      setProgress(pct);
      if (pct > 30 && pct < 70) {
        setStatusMessage('Establishing LoRa RF & Gateway protocols...');
      } else if (pct >= 70 && pct < 95) {
        setStatusMessage('Checking MINEGATE & Cloud sync status...');
      } else if (pct >= 95) {
        setStatusMessage('System Ready. Redirecting...');
      }
      if (elapsed >= duration + 200) {
        clearInterval(interval);
        navigate('/overview');
      }
    }, 40);
    return () => clearInterval(interval);
  }, [navigate]);

  return (
    <div className="fixed inset-0 bg-white flex flex-col items-center justify-between p-8 select-none z-50">
      <div className="w-full flex justify-between items-center text-xs font-semibold text-slate-400 tracking-wider">
        <span>SIH 2026 • SIH26025</span>
        <LanguageSelector variant="segmented" />
      </div>

      <div className="flex flex-col items-center max-w-md w-full text-center">
        <div className="relative mb-6">
          <div className="h-20 w-20 rounded-2xl bg-blue-700 text-white flex items-center justify-center shadow-xl shadow-blue-500/20">
            <Shield className="h-10 w-10 text-white" />
          </div>
        </div>

        <h1 className="text-4xl font-black tracking-tight text-slate-900">
          MINEGUARD
        </h1>
        <h2 className="text-sm font-extrabold tracking-widest text-blue-600 uppercase mt-1">
          SIH 2026 • RED HACK
        </h2>

        <div className="w-full mt-10">
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden border border-slate-200">
            <div
              className="bg-blue-600 h-full rounded-full transition-all duration-75 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="mt-3 flex justify-between items-center text-xs">
            <span className="text-slate-500 font-medium">{statusMessage}</span>
            <span className="font-bold text-blue-700 font-mono">{progress}%</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 w-full max-w-sm text-center border-t border-slate-100 pt-4 text-slate-400">
        <div className="flex flex-col items-center gap-1">
          <Radio className="h-4 w-4 text-blue-500" />
          <span className="text-[10px] font-semibold uppercase">Sensor Network</span>
        </div>
        <div className="flex flex-col items-center gap-1">
          <Activity className="h-4 w-4 text-emerald-500" />
          <span className="text-[10px] font-semibold uppercase">Live Safety</span>
        </div>
        <div className="flex flex-col items-center gap-1">
          <Shield className="h-4 w-4 text-purple-500" />
          <span className="text-[10px] font-semibold uppercase">DGMS Ready</span>
        </div>
      </div>
    </div>
  );
};

export default SplashScreen;
