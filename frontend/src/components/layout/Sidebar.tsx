import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Activity,
  MapPin,
  Cpu,
  Bell,
  Brain,
  Server,
  FileText,
  Settings,
  X,
  ShieldCheck,
  Mail,
} from "lucide-react";
import { useAlertStore } from "../../store/alertStore";
interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}
export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { unreadCount } = useAlertStore();
  const navItems = [
    {
      label: "Overview / Dashboard",
      to: "/app/dashboard",
      icon: LayoutDashboard,
    },
    { label: "Live Telemetry", to: "/app/telemetry", icon: Activity },
    { label: "GIS / Mine Location", to: "/app/gis", icon: MapPin },
    { label: "Alerts", to: "/app/alerts", icon: Bell, badge: unreadCount },
    { label: "Notifications", to: "/app/notifications", icon: Mail },
    { label: "Hardware / Nodes", to: "/app/nodes", icon: Cpu },
    { label: "AI Risk Analytics", to: "/app/ai", icon: Brain },
    { label: "Edge Gateway", to: "/app/gateway", icon: Server },
    { label: "Reports / Audit Logs", to: "/app/reports", icon: FileText },
    { label: "Settings / Profile", to: "/app/settings", icon: Settings },
  ];
  return (
    <>
      {" "}
      {/* Mobile Backdrop */}{" "}
      {isOpen && (
        <div
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-40 lg:hidden"
          onClick={onClose}
        />
      )}{" "}
      {/* Sidebar aside */}{" "}
      <aside
        className={`fixed top-0 bottom-0 left-0 rtl:left-auto rtl:right-0 z-50 w-64 bg-white border-r rtl:border-r-0 rtl:border-l border-slate-200 flex flex-col transition-transform duration-200 ease-in-out lg:translate-x-0 ${isOpen ? "translate-x-0" : "max-lg:-translate-x-full rtl:max-lg:translate-x-full"}`}
      >
        {" "}
        {/* Sidebar Header */}{" "}
        <div className="h-20 px-6 border-b border-slate-100 flex items-center justify-between">
          {" "}
          <div className="flex items-center gap-3">
            {" "}
            <div className="h-10 w-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-black shadow-sm shrink-0">
              {" "}
              <ShieldCheck className="h-6 w-6 text-white" />{" "}
            </div>{" "}
            <div>
              {" "}
              <div className="font-black text-base text-slate-900 tracking-tight leading-tight">
                {" "}
                MINEGUARD{" "}
              </div>{" "}
              <div className="text-[10px] font-bold text-blue-600 tracking-wide uppercase">
                {" "}
                SIH 2026 • RED HACK{" "}
              </div>{" "}
            </div>{" "}
          </div>{" "}
          <button
            onClick={onClose}
            className="lg:hidden p-1.5 text-slate-500 hover:text-slate-800 rounded-md"
          >
            {" "}
            <X className="h-5 w-5" />{" "}
          </button>{" "}
        </div>{" "}
        {/* Navigation list */}{" "}
        <nav className="flex-1 px-4 py-5 space-y-1.5 overflow-y-auto">
          {" "}
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => {
                  if (window.innerWidth < 1024) onClose();
                }}
                className={({ isActive }) =>
                  `flex items-center justify-between px-4 py-3 rounded-xl text-xs font-bold transition-all ${isActive ? "bg-slate-900 text-white shadow-sm" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"}`
                }
              >
                {" "}
                <div className="flex items-center gap-3">
                  {" "}
                  <Icon className="h-4 w-4 shrink-0" />{" "}
                  <span>{item.label}</span>{" "}
                </div>{" "}
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="px-2 py-0.5 text-[10px] font-extrabold rounded-full bg-red-600 text-white">
                    {" "}
                    {item.badge}{" "}
                  </span>
                )}{" "}
              </NavLink>
            );
          })}{" "}
        </nav>{" "}
        {/* Fleet Gateway Status Card */}{" "}
        <div className="p-4 border-t border-slate-100 bg-slate-50/60">
          {" "}
          <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-2xs flex items-center justify-between">
            {" "}
            <div className="overflow-hidden">
              {" "}
              <div className="text-[11px] font-bold text-slate-900 truncate">
                {" "}
                IN865 LoRa Mesh{" "}
              </div>{" "}
              <div className="text-[10px] text-slate-500 font-semibold truncate">
                {" "}
                Offline Gateway Connected{" "}
              </div>{" "}
            </div>{" "}
            <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0 ml-2" />{" "}
          </div>{" "}
        </div>{" "}
      </aside>{" "}
    </>
  );
};
export default Sidebar;
