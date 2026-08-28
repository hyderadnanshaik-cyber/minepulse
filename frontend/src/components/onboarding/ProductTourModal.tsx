import React, { useState } from 'react';
import { X, Sparkles, ChevronRight, ChevronLeft, ShieldCheck, Cpu, MapPin, Bell } from 'lucide-react';

interface ProductTourModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const TOUR_STEPS = [
  {
    title: 'Welcome to MINEGUARD',
    desc: 'Real-Time Mine Subsidence & Geotechnical Hazard Early Warning System designed for underground coal and mineral mines.',
    icon: <ShieldCheck className="h-8 w-8 text-blue-600" />,
  },
  {
    title: 'Multi-Sensor Fleet',
    desc: 'Each station integrates 9-Axis IMU tilt, continuous displacement, and mechanical crack opening sensors.',
    icon: <Cpu className="h-8 w-8 text-blue-600" />,
  },
  {
    title: 'PostGIS Spatial Map',
    desc: 'Live interactive underground tunnel mapping with sub-millimeter WGS84 coordinate precision.',
    icon: <MapPin className="h-8 w-8 text-emerald-600" />,
  },
  {
    title: 'DGMS Statutory Alerts',
    desc: 'Instant early warnings and evacuation advisories triggered by rate-of-movement thresholds and AI anomaly detection.',
    icon: <Bell className="h-8 w-8 text-red-600" />,
  },
];

export const ProductTourModal: React.FC<ProductTourModalProps> = ({ isOpen, onClose }) => {
  const [step, setStep] = useState(0);

  if (!isOpen) return null;

  const current = TOUR_STEPS[step];
  const isLast = step === TOUR_STEPS.length - 1;

  const handleFinish = () => {
    localStorage.setItem('strata_tour_completed', 'true');
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-end sm:items-center justify-center p-3 sm:p-4 z-50 animate-in fade-in-50">
      <div className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200 shadow-2xl w-full max-w-[92vw] sm:max-w-md max-h-[90vh] overflow-y-auto space-y-5 sm:space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-blue-600" />
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              System Walkthrough ({step + 1}/{TOUR_STEPS.length})
            </span>
          </div>
          <button onClick={handleFinish} className="p-1 text-slate-400 hover:text-slate-700">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="text-center space-y-3 py-2">
          <div className="p-4 bg-slate-50 rounded-2xl w-fit mx-auto border border-slate-100 shadow-xs">
            {current.icon}
          </div>
          <h3 className="text-lg font-black text-slate-900">{current.title}</h3>
          <p className="text-xs text-slate-600 leading-relaxed max-w-xs mx-auto">
            {current.desc}
          </p>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-slate-100">
          <button
            type="button"
            disabled={step === 0}
            onClick={() => setStep((s) => s - 1)}
            className="px-3 py-2 text-xs font-bold text-slate-500 hover:text-slate-800 disabled:opacity-30 flex items-center gap-1"
          >
            <ChevronLeft className="h-4 w-4" /> Previous
          </button>

          <div className="flex items-center gap-1.5">
            {TOUR_STEPS.map((_, i) => (
              <span
                key={i}
                className={
                  i === step
                    ? 'h-2 w-6 rounded-full bg-blue-600 transition-all'
                    : 'h-2 w-2 rounded-full bg-slate-200'
                }
              />
            ))}
          </div>

          <button
            type="button"
            onClick={isLast ? handleFinish : () => setStep((s) => s + 1)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-md flex items-center gap-1 transition"
          >
            {isLast ? 'Get Started' : 'Next'} <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductTourModal;
