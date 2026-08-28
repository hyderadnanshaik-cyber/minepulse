import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Settings,
  Globe,
  ShieldCheck,
  Check,
  Bell,
  User,
  Phone,
  Mail,
  Lock,
  Save,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Send,
  Volume2,
  Radio,
  Zap,
} from 'lucide-react';
import { apiClient } from '../../services/api/apiClient';
import { SUPPORTED_LANGUAGES, SupportedLanguage, changeLanguage } from '../../i18n';

const OFFICER_KEY = 'mineguard_safety_officer';

interface OfficerProfile {
  name: string;
  email: string;
  phone: string;
  role: string;
  notify_email: boolean;
  notify_sms: boolean;
  alert_timeout_minutes: number;
}

const defaultOfficer: OfficerProfile = {
  name: 'SHAIK ADNAN HYDER',
  email: '',
  phone: '',
  role: 'Mine Safety Officer',
  notify_email: true,
  notify_sms: true,
  alert_timeout_minutes: 5,
};

function loadOfficer(): OfficerProfile {
  try {
    const stored = localStorage.getItem(OFFICER_KEY);
    if (stored) return { ...defaultOfficer, ...JSON.parse(stored) };
  } catch {}
  return defaultOfficer;
}

interface SettingsSectionProps {
  title: string;
  children: React.ReactNode;
}
const SettingsSection: React.FC<SettingsSectionProps> = ({ title, children }) => (
  <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-card">
    <div className="px-5 py-3 bg-slate-50/80 border-b border-slate-100 text-xs font-bold text-slate-700 uppercase tracking-wider">
      {title}
    </div>
    <div className="divide-y divide-slate-100">{children}</div>
  </div>
);

export const SettingsPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const currentLang = (i18n.language as SupportedLanguage) || 'en';
  const [audioSirenEnabled, setAudioSirenEnabled] = useState(true);
  const [officer, setOfficer] = useState<OfficerProfile>(loadOfficer);
  const [saving, setSaving] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [draft, setDraft] = useState<OfficerProfile>(officer);

  const showToast = (msg: string, type: 'success' | 'error' = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3500);
  };

  const handleSaveOfficer = async () => {
    setSaving(true);
    try {
      // Persist to localStorage
      localStorage.setItem(OFFICER_KEY, JSON.stringify(draft));
      setOfficer(draft);

      // Sync to backend
      await apiClient.post('/notifications/officer', {
        name: draft.name,
        email: draft.email,
        phone: draft.phone,
        role: draft.role,
        notify_email: draft.notify_email,
        notify_sms: draft.notify_sms,
        alert_timeout_minutes: draft.alert_timeout_minutes,
      });

      setEditMode(false);
      showToast('Safety Officer profile saved. Notifications configured.');
    } catch (err: any) {
      // Even if backend fails, local save succeeded
      setOfficer(draft);
      setEditMode(false);
      showToast('Profile saved locally. Backend sync pending.');
    } finally {
      setSaving(false);
    }
  };

  const handleTestNotification = async () => {
    if (!officer.email && !officer.phone) {
      showToast('Please save an email or phone number first.', 'error');
      return;
    }
    setTestLoading(true);
    try {
      await apiClient.post('/notifications/test', {
        email: officer.email,
        phone: officer.phone,
        name: officer.name,
      });
      showToast('Test notification sent! Check your email/SMS.');
    } catch (err: any) {
      showToast('Test failed: ' + (err?.response?.data?.detail || 'Backend not configured for SMTP/SMS yet.'), 'error');
    } finally {
      setTestLoading(false);
    }
  };

  return (
    <div className="space-y-5 sm:space-y-6 max-w-4xl mx-auto overflow-x-hidden w-full">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-6 right-6 z-[100] px-5 py-3 rounded-2xl shadow-2xl text-xs font-bold flex items-center gap-2.5 ${toast.type === 'success' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'}`}>
          {toast.type === 'success' ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
          {toast.msg}
        </div>
      )}

      {/* Header */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="p-3.5 bg-blue-50 text-blue-600 rounded-xl">
            <Settings className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">{t('settings.title')}</h1>
            <p className="text-xs text-slate-500 mt-0.5">Control room preferences, alert notifications, and safety officer contact</p>
          </div>
        </div>
      </div>

      {/* ─── SAFETY OFFICER CONTACT CARD ─────────────────────────────────── */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-card overflow-hidden">
        <div className="px-5 py-3 bg-red-50 border-b border-red-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="h-4 w-4 text-red-500" />
            <span className="text-xs font-bold text-red-700 uppercase tracking-wider">
              Emergency Alert Notifications — Safety Officer Contact
            </span>
          </div>
          {!editMode && (
            <button
              onClick={() => { setDraft(officer); setEditMode(true); }}
              className="px-3 py-1 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold rounded-lg transition"
            >
              Edit
            </button>
          )}
        </div>

        <div className="p-5 space-y-5">
          {/* Info banner */}
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-amber-800">How This Works</p>
              <p className="text-[11px] text-amber-700 mt-0.5 leading-relaxed">
                When a CRITICAL alert is generated and goes unacknowledged for <strong>{officer.alert_timeout_minutes} minutes</strong>,
                the system automatically sends an <strong>email</strong> and/or <strong>SMS</strong> to the safety officer below.
                This ensures alerts are never missed even when the app is closed or the officer's phone is on silent.
              </p>
            </div>
          </div>

          {editMode ? (
            /* Edit Form */
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                    <User className="h-3.5 w-3.5 text-slate-400" /> Officer Full Name
                  </label>
                  <input
                    type="text"
                    value={draft.name}
                    onChange={(e) => setDraft({ ...draft, name: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Full name of Safety Officer"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-700">Designation / Role</label>
                  <input
                    type="text"
                    value={draft.role}
                    onChange={(e) => setDraft({ ...draft, role: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g. Mine Manager, Safety Officer"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                    <Mail className="h-3.5 w-3.5 text-slate-400" /> Email Address
                  </label>
                  <input
                    type="email"
                    value={draft.email}
                    onChange={(e) => setDraft({ ...draft, email: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="officer@mineguard.internal"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                    <Phone className="h-3.5 w-3.5 text-slate-400" /> Mobile Number (with country code)
                  </label>
                  <input
                    type="tel"
                    value={draft.phone}
                    onChange={(e) => setDraft({ ...draft, phone: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="+91 9876543210"
                  />
                </div>
              </div>

              {/* Timeout setting */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                  <Bell className="h-3.5 w-3.5 text-slate-400" /> Alert Timeout Before Escalation (minutes)
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min={1}
                    max={30}
                    value={draft.alert_timeout_minutes}
                    onChange={(e) => setDraft({ ...draft, alert_timeout_minutes: Number(e.target.value) })}
                    className="w-48"
                  />
                  <span className="text-sm font-black text-blue-600 font-mono">{draft.alert_timeout_minutes} min</span>
                  <span className="text-xs text-slate-500">after alert → SMS + Email sent</span>
                </div>
              </div>

              {/* Toggle switches */}
              <div className="flex items-center gap-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <div
                    onClick={() => setDraft({ ...draft, notify_email: !draft.notify_email })}
                    className={`h-6 w-11 rounded-full transition-colors relative ${draft.notify_email ? 'bg-blue-600' : 'bg-slate-200'}`}
                  >
                    <span className={`absolute top-1 h-4 w-4 bg-white rounded-full shadow transition-transform ${draft.notify_email ? 'translate-x-6' : 'translate-x-1'}`} />
                  </div>
                  <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                    <Mail className="h-3.5 w-3.5" /> Email Alerts
                  </span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer">
                  <div
                    onClick={() => setDraft({ ...draft, notify_sms: !draft.notify_sms })}
                    className={`h-6 w-11 rounded-full transition-colors relative ${draft.notify_sms ? 'bg-blue-600' : 'bg-slate-200'}`}
                  >
                    <span className={`absolute top-1 h-4 w-4 bg-white rounded-full shadow transition-transform ${draft.notify_sms ? 'translate-x-6' : 'translate-x-1'}`} />
                  </div>
                  <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                    <Phone className="h-3.5 w-3.5" /> SMS Alerts
                  </span>
                </label>
              </div>

              {/* Save / Cancel */}
              <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
                <button
                  onClick={() => setEditMode(false)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveOfficer}
                  disabled={saving}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl flex items-center gap-2 transition"
                >
                  {saving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
                  {saving ? 'Saving...' : 'Save & Activate'}
                </button>
              </div>
            </div>
          ) : (
            /* View Mode */
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                  <span className="text-[10px] font-bold text-slate-400 uppercase flex items-center gap-1"><User className="h-3 w-3" /> Officer Name</span>
                  <span className="text-sm font-black text-slate-900 block">{officer.name || '—'}</span>
                  <span className="text-[11px] text-slate-500">{officer.role}</span>
                </div>

                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                  <span className="text-[10px] font-bold text-slate-400 uppercase flex items-center gap-1"><Bell className="h-3 w-3" /> Escalation Timeout</span>
                  <span className="text-sm font-black text-blue-600 block font-mono">{officer.alert_timeout_minutes} minutes</span>
                  <span className="text-[11px] text-slate-500">After unacknowledged alert</span>
                </div>

                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                  <span className="text-[10px] font-bold text-slate-400 uppercase flex items-center gap-1"><Mail className="h-3 w-3" /> Email</span>
                  <span className={`text-sm font-bold block ${officer.email ? 'text-slate-900' : 'text-slate-400 italic'}`}>
                    {officer.email || 'Not configured — click Edit'}
                  </span>
                  <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full ${officer.notify_email ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>
                    {officer.notify_email ? '✓ ENABLED' : 'DISABLED'}
                  </span>
                </div>

                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                  <span className="text-[10px] font-bold text-slate-400 uppercase flex items-center gap-1"><Phone className="h-3 w-3" /> Mobile SMS</span>
                  <span className={`text-sm font-bold block font-mono ${officer.phone ? 'text-slate-900' : 'text-slate-400 italic'}`}>
                    {officer.phone || 'Not configured — click Edit'}
                  </span>
                  <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full ${officer.notify_sms ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>
                    {officer.notify_sms ? '✓ ENABLED' : 'DISABLED'}
                  </span>
                </div>
              </div>

              {/* Test Notification */}
              <div className="flex items-center gap-3 pt-2 border-t border-slate-100">
                <button
                  onClick={handleTestNotification}
                  disabled={testLoading}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl flex items-center gap-2 transition"
                >
                  {testLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Send className="h-3.5 w-3.5" />}
                  {testLoading ? 'Sending Test...' : 'Send Test Alert Notification'}
                </button>
                <span className="text-[11px] text-slate-400">
                  Sends a test email + SMS to verify delivery works
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ─── USER & SECURITY ─────────────────────────────────────────────── */}
      <SettingsSection title="User & Security">
        <div className="flex items-center justify-between px-5 py-3.5">
          <div className="flex items-center gap-3">
            <User className="h-4 w-4 text-slate-400" />
            <div>
              <p className="text-sm font-medium text-slate-900">Safety Officer</p>
              <p className="text-xs text-slate-400">Primary account holder</p>
            </div>
          </div>
          <span className="text-xs text-slate-500 font-mono">{officer.name}</span>
        </div>
        <div className="flex items-center justify-between px-5 py-3.5">
          <div className="flex items-center gap-3">
            <Lock className="h-4 w-4 text-slate-400" />
            <div>
              <p className="text-sm font-medium text-slate-900">Security Token</p>
              <p className="text-xs text-slate-400">Authentication method</p>
            </div>
          </div>
          <span className="text-xs text-slate-500 font-mono">RSA-2048 / Active</span>
        </div>
      </SettingsSection>

      {/* ─── INTERFACE & LANGUAGE ────────────────────────────────────────── */}
      <SettingsSection title="Interface & Language">
        <div className="px-4 sm:px-5 py-4 space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-800">
            <Globe className="h-4 w-4 text-blue-600 shrink-0" />
            <span className="truncate">Interface Language (भाषा / زبان)</span>
          </div>
          {/* Responsive grid: 1 col on 320px, 3 cols on sm+ */}
          <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 gap-2 pt-1">
            {SUPPORTED_LANGUAGES.map((lang) => {
              const isSelected = currentLang === lang.code;
              return (
                <button
                  key={lang.code}
                  type="button"
                  onClick={() => changeLanguage(lang.code)}
                  className={
                    isSelected
                      ? 'p-3 rounded-xl border text-left transition flex items-center justify-between gap-2 border-blue-600 bg-blue-50'
                      : 'p-3 rounded-xl border text-left transition flex items-center justify-between gap-2 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                  }
                  dir={lang.code === 'ur' ? 'rtl' : 'ltr'}
                >
                  <div className="flex flex-col gap-0.5 min-w-0">
                    <span className="font-bold text-slate-900 text-sm truncate">{lang.nativeName}</span>
                    <span className="text-[10px] text-slate-500">{lang.name}</span>
                  </div>
                  {isSelected && (
                    <div className="h-5 w-5 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0">
                      <Check className="h-3 w-3" />
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </SettingsSection>

      {/* ─── ALERT PREFERENCES ───────────────────────────────────────────── */}
      <SettingsSection title="Alert & Siren Preferences">
        <div className="flex items-center justify-between px-4 sm:px-5 py-3.5 gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <Volume2 className="h-4 w-4 text-slate-400 shrink-0" />
            <div className="min-w-0">
              <p className="text-sm font-medium text-slate-900 truncate">Audible Site Siren</p>
              <p className="text-xs text-slate-400">Activates on CRITICAL alerts via gateway relay</p>
            </div>
          </div>
          <div
            onClick={() => setAudioSirenEnabled(!audioSirenEnabled)}
            className={`h-6 w-11 rounded-full transition-colors relative cursor-pointer shrink-0 ${audioSirenEnabled ? 'bg-blue-600' : 'bg-slate-200'}`}
          >
            <span className={`absolute top-1 h-4 w-4 bg-white rounded-full shadow transition-transform ${audioSirenEnabled ? 'translate-x-6' : 'translate-x-1'}`} />
          </div>
        </div>
        <div className="flex items-center justify-between px-4 sm:px-5 py-3.5 gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <Radio className="h-4 w-4 text-slate-400 shrink-0" />
            <div className="min-w-0">
              <p className="text-sm font-medium text-slate-900 truncate">LoRa Mesh Auto-Reconnect</p>
              <p className="text-xs text-slate-400">Re-establishes mesh routes when node drops</p>
            </div>
          </div>
          <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 shrink-0">Active</span>
        </div>
        <div className="flex items-center justify-between px-4 sm:px-5 py-3.5 gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <Zap className="h-4 w-4 text-slate-400 shrink-0" />
            <div className="min-w-0">
              <p className="text-sm font-medium text-slate-900 truncate">AI Anomaly Detection</p>
              <p className="text-xs text-slate-400">IsolationForest continuous inference</p>
            </div>
          </div>
          <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 shrink-0">Running</span>
        </div>
      </SettingsSection>

      {/* ─── APP INFO ────────────────────────────────────────────────────── */}
      <SettingsSection title="Application Info">
        <div className="flex items-center justify-between px-4 sm:px-5 py-3.5 gap-3">
          <p className="text-sm font-medium text-slate-900 shrink-0">Application Version</p>
          <span className="text-xs text-slate-500 font-mono text-right truncate">MINEGUARD v1.0.0 — SIH 2026</span>
        </div>
        <div className="flex items-center justify-between px-4 sm:px-5 py-3.5 gap-3">
          <p className="text-sm font-medium text-slate-900 shrink-0">Build</p>
          <span className="text-xs text-slate-500 font-mono text-right truncate">RED HACK • React 18 + FastAPI</span>
        </div>
        <div className="flex items-center justify-between px-4 sm:px-5 py-3.5 gap-3">
          <p className="text-sm font-medium text-slate-900 shrink-0">DGMS Compliance</p>
          <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 shrink-0">Circular No. 1/2017</span>
        </div>
      </SettingsSection>
    </div>
  );
};

export default SettingsPage;

