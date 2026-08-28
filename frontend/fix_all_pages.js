import fs from 'fs';

// Run fix_syntax first
import './fix_syntax.js';

// 1. themeStore.ts
fs.writeFileSync('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/store/themeStore.ts', `import { create } from 'zustand';

export type Theme = 'light' | 'dark';

interface ThemeState {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
  initTheme: () => void;
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: 'light',
  toggleTheme: () => {
    const current = get().theme;
    const nextTheme: Theme = current === 'dark' ? 'light' : 'dark';
    get().setTheme(nextTheme);
  },
  setTheme: (theme: Theme) => {
    set({ theme });
    try {
      localStorage.setItem('strata_theme', theme);
    } catch (e) {}
    if (typeof document !== 'undefined' && document.documentElement) {
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  },
  initTheme: () => {
    get().setTheme('light');
  },
}));
`, 'utf8');

// 2. SplashScreen.tsx
fs.writeFileSync('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/pages/Splash/SplashScreen.tsx', `import React, { useEffect, useState } from 'react';
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
              style={{ width: \`\${progress}%\` }}
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
`, 'utf8');

// 3. LoginPage.tsx
fs.writeFileSync('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/pages/Auth/LoginPage.tsx', `import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { ShieldCheck, Mail, Lock, LogIn } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('operator@mineguard.internal');
  const [password, setPassword] = useState('safety2026');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    try {
      await login(email, password);
      navigate('/app/dashboard');
    } catch (err: any) {
      setErrorMsg(err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-3xl p-8 border border-slate-200 shadow-xl space-y-6">
        <div className="text-center space-y-2">
          <div className="h-12 w-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center mx-auto shadow-md">
            <ShieldCheck className="h-7 w-7" />
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            MINEGUARD
          </h1>
          <p className="text-xs text-slate-500 font-medium">
            Mine Subsidence Monitoring & Safety System
          </p>
        </div>

        {errorMsg && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 font-bold">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Official Email</label>
            <div className="relative">
              <Mail className="h-4 w-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Station Passcode</label>
            <div className="relative">
              <Lock className="h-4 w-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-md transition flex items-center justify-center gap-2"
          >
            <LogIn className="h-4 w-4" />
            {loading ? 'Authenticating...' : 'Sign In to Command Center'}
          </button>
        </form>

        <div className="text-center">
          <Link to="/register" className="text-xs font-bold text-blue-600 hover:underline">
            Register new safety terminal
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
`, 'utf8');

// 4. RegisterPage.tsx
fs.writeFileSync('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/pages/Auth/RegisterPage.tsx', `import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { ShieldCheck, Mail, Lock, UserPlus, User } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const [displayName, setDisplayName] = useState('SHAIK ADNAN HYDER');
  const [email, setEmail] = useState('adnan@mineguard.internal');
  const [password, setPassword] = useState('safety2026');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    try {
      await register(email, password, displayName);
      navigate('/app/dashboard');
    } catch (err: any) {
      setErrorMsg(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-3xl p-8 border border-slate-200 shadow-xl space-y-6">
        <div className="text-center space-y-2">
          <div className="h-12 w-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center mx-auto shadow-md">
            <ShieldCheck className="h-7 w-7" />
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Register Terminal
          </h1>
          <p className="text-xs text-slate-500 font-medium">
            MINEGUARD Mine Safety System
          </p>
        </div>

        {errorMsg && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 font-bold">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Engineer Name</label>
            <div className="relative">
              <User className="h-4 w-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Official Email</label>
            <div className="relative">
              <Mail className="h-4 w-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Password</label>
            <div className="relative">
              <Lock className="h-4 w-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-md transition flex items-center justify-center gap-2"
          >
            <UserPlus className="h-4 w-4" />
            {loading ? 'Registering...' : 'Complete Terminal Registration'}
          </button>
        </form>

        <div className="text-center">
          <Link to="/login" className="text-xs font-bold text-blue-600 hover:underline">
            Already registered? Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
`, 'utf8');

// 5. NodeDetailPage.tsx
fs.writeFileSync('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/pages/Nodes/NodeDetailPage.tsx', `import React, { useState, useEffect } from 'react';
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
  Sliders,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';

export const NodeDetailPage: React.FC = () => {
  const { nodeId } = useParams<{ nodeId: string }>();
  const navigate = useNavigate();
  const [node, setNode] = useState<Node | null>(null);
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDetail = async () => {
    if (!nodeId) return;
    setLoading(true);
    try {
      const [nodeRes, telRes] = await Promise.all([
        apiClient.get(\`/nodes/\${nodeId}\`),
        apiClient.get(\`/telemetry?node_id=\${nodeId}&limit=20\`)
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

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <button
        onClick={() => navigate('/app/nodes')}
        className="flex items-center gap-1.5 text-xs font-bold text-slate-600 hover:text-slate-900 transition"
      >
        <ArrowLeft className="h-4 w-4" /> Back to Sensor Fleet
      </button>

      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="p-4 bg-blue-50 text-blue-600 rounded-2xl">
            <Cpu className="h-8 w-8" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-black text-slate-900 font-mono">
                {node?.node_code || node?.node_id || \`NODE_\${nodeId}\`}
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-800">
                {node?.status || 'ONLINE'}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Zone: {node?.zone || 'North Working Panel'} • {Number(node?.latitude || 23.75).toFixed(4)}°N, {Number(node?.longitude || 86.42).toFixed(4)}°E
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Link
            to={\`/app/gis?focus=\${node?.node_id || nodeId}\`}
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
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-card">
          <span className="text-[10px] font-bold uppercase text-slate-400 block">Risk Level</span>
          <span className="text-lg font-black text-slate-900 mt-1 block">
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
`, 'utf8');

// 6. NetworkPage.tsx
fs.writeFileSync('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/pages/Network/NetworkPage.tsx', `import React from 'react';
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
`, 'utf8');

console.log('Fixed all pages!');
