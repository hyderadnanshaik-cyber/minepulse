import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, MapPin, Bell, Cpu, Settings } from 'lucide-react';
import { useAlertStore } from '../../store/alertStore';

export const BottomNav: React.FC = () => {
  const { alerts } = useAlertStore();
  const unackedCount = alerts.filter(
    (a) => (a.severity === 'CRITICAL' || a.severity === 'HIGH' || a.severity === 'WARNING') && a.status !== 'RESOLVED'
  ).length;

  const navItems = [
    { to: '/app/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="h-5 w-5" /> },
    { to: '/app/gis', label: 'GIS Map', icon: <MapPin className="h-5 w-5" /> },
    {
      to: '/app/alerts',
      label: 'Alerts',
      icon: (
        <div className="relative">
          <Bell className="h-5 w-5" />
          {unackedCount > 0 && (
            <span className="absolute -top-1.5 -right-2 h-4 min-w-[16px] px-1 bg-red-600 text-white text-[9px] font-black rounded-full flex items-center justify-center animate-pulse">
              {unackedCount}
            </span>
          )}
        </div>
      )
    },
    { to: '/app/nodes', label: 'Fleet', icon: <Cpu className="h-5 w-5" /> },
    { to: '/app/settings', label: 'Settings', icon: <Settings className="h-5 w-5" /> }
  ];

  return (
    <nav aria-label="Mobile Navigation" className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-slate-200 px-2 py-1 shadow-lg">
      <div className="flex items-center justify-around">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center py-1.5 px-3 rounded-xl text-[10px] font-bold transition-all ${
                isActive
                  ? 'text-blue-600 font-black'
                  : 'text-slate-500 hover:text-slate-900'
              }`
            }
          >
            {item.icon}
            <span className="mt-0.5">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
};

export default BottomNav;
