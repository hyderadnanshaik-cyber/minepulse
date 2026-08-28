import React from 'react';
import { AlertOctagon, X, MapPin, CheckCircle2, Building2, AlertTriangle } from 'lucide-react';

interface AffectedInfraItem {
  id?: number;
  name: string;
  asset_type?: string;
  distance_m?: number;
  impact_level?: string;
  criticality?: string;
}

interface SubsidenceAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAcknowledge: () => void;
  onViewGIS: () => void;
  alert?: {
    nodeId?: string;
    panel?: string;
    displacement?: number;
    tilt?: number;
    crackWidth?: number;
    severity?: string;
    message?: string;
    triggeredAt?: string;
    alertId?: number;
    affectedInfrastructure?: AffectedInfraItem[];
  };
}

const getAssetIcon = (assetType?: string) => {
  const map: Record<string, string> = {
    MAIN_ENTRANCE: '🚧',
    TUNNEL: '🕳️',
    SHAFT: '⬇️',
    VENTILATION_SYSTEM: '💨',
    CONTROL_ROOM: '🖥️',
    ELECTRICAL_SUBSTATION: '⚡',
    PUMPING_STATION: '💧',
    STORAGE_AREA: '🏗️',
    CONVEYOR: '🔧',
    EMERGENCY_EXIT: '🚨',
  };
  return map[assetType || ''] || '🏭';
};

export const SubsidenceAlertModal: React.FC<SubsidenceAlertModalProps> = ({
  isOpen,
  onClose,
  onAcknowledge,
  onViewGIS,
  alert,
}) => {
  if (!isOpen || !alert) return null;

  // Extract infrastructure list from explicit prop or parse from alert.message
  let infraList: AffectedInfraItem[] = alert.affectedInfrastructure || [];
  if (infraList.length === 0 && alert.message && alert.message.includes('AT-RISK INFRASTRUCTURE:')) {
    const rawPart = alert.message.split('AT-RISK INFRASTRUCTURE:')[1]?.split('.')[0];
    if (rawPart) {
      infraList = rawPart.split(',').map((itemStr) => {
        const trimmed = itemStr.trim();
        const distMatch = trimmed.match(/\(([\d.]+)m\)/);
        const dist = distMatch ? parseFloat(distMatch[1]) : undefined;
        const name = trimmed.replace(/\([\d.]+m\)/, '').trim();
        return { name, distance_m: dist, impact_level: 'HIGH', criticality: 'CRITICAL' };
      });
    }
  }

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4 z-50 animate-in fade-in-50">
      <div className="bg-white rounded-3xl p-4 sm:p-6 border-2 border-red-500 shadow-2xl w-full max-w-[92vw] sm:max-w-lg max-h-[90vh] overflow-y-auto space-y-4 sm:space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-red-100 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-red-100 text-red-600 rounded-xl animate-pulse">
              <AlertOctagon className="h-6 w-6" />
            </div>
            <div>
              <span className="text-[10px] font-extrabold tracking-wider uppercase text-red-600">
                CRITICAL DGMS STRATA ALARM
              </span>
              <h2 className="text-base font-bold text-slate-900 leading-tight">
                Abnormal Ground Movement Detected
              </h2>
            </div>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-700">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Hazard Message Banner */}
        <div className="bg-red-50 border border-red-200 rounded-2xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs font-mono font-bold text-red-900">
            <span>Station: {alert.nodeId}</span>
            <span>Zone: {alert.panel}</span>
          </div>
          <p className="text-xs text-red-800 leading-relaxed font-medium">
            {alert.message || 'Severe rate-of-displacement threshold exceeded. Evacuation advisory active.'}
          </p>
        </div>

        {/* ⚠️ CRITICAL NEW SECTION: Public & Mine Infrastructure at Risk */}
        {infraList.length > 0 && (
          <div className="bg-amber-50 border-2 border-amber-400 rounded-2xl p-4 space-y-2.5">
            <div className="flex items-center gap-2 text-amber-900">
              <Building2 className="h-5 w-5 text-amber-600 shrink-0" />
              <div>
                <h3 className="text-xs font-extrabold uppercase tracking-wide">
                  Public & Mine Infrastructure at Risk ({infraList.length} Structures)
                </h3>
                <p className="text-[11px] text-amber-700">
                  Predicted ground instability within hazard radius of the following assets:
                </p>
              </div>
            </div>

            <div className="space-y-1.5 pt-1">
              {infraList.map((inf, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between bg-white px-3 py-2 rounded-xl border border-amber-200 shadow-xs gap-2"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-base">{getAssetIcon(inf.asset_type)}</span>
                    <span className="text-xs font-bold text-slate-900 truncate">{inf.name}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    {inf.distance_m != null && (
                      <span className="text-[11px] font-mono font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded-md">
                        {inf.distance_m}m away
                      </span>
                    )}
                    <span className="text-[10px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-red-100 text-red-700 border border-red-200">
                      {inf.impact_level || 'AT RISK'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Kinematic Metrics */}
        <div className="grid grid-cols-3 gap-2.5 text-center font-mono">
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
            <span className="text-[9px] uppercase font-bold text-slate-400 block">Displacement</span>
            <span className="text-sm font-black text-red-600">{(alert.displacement ?? 14.8).toFixed(2)} mm</span>
          </div>
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
            <span className="text-[9px] uppercase font-bold text-slate-400 block">Strata Tilt</span>
            <span className="text-sm font-black text-red-600">{(alert.tilt ?? 3.4).toFixed(2)}°</span>
          </div>
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
            <span className="text-[9px] uppercase font-bold text-slate-400 block">Crack Fissure</span>
            <span className="text-sm font-black text-red-600">{(alert.crackWidth ?? 2.1).toFixed(2)} mm</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-slate-100">
          <button
            type="button"
            onClick={onViewGIS}
            className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold rounded-xl flex items-center gap-1.5 transition"
          >
            <MapPin className="h-4 w-4 text-blue-600" />
            Inspect on GIS Map
          </button>
          <button
            type="button"
            onClick={onAcknowledge}
            className="px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-xl flex items-center gap-1.5 shadow-md transition"
          >
            <CheckCircle2 className="h-4 w-4" />
            Acknowledge Incident
          </button>
        </div>
      </div>
    </div>
  );
};

export default SubsidenceAlertModal;
