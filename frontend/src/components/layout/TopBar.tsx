import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../hooks/useAuth";
import { useAlertStore } from "../../store/alertStore";
import {
  Bell, LogOut, User as UserIcon, Menu, HelpCircle,
  Sparkles, Activity, Mail, X,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { LanguageSelector } from "../ui/LanguageSelector";

interface TopBarProps {
  onToggleSidebar?: () => void;
  onOpenTour?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({ onToggleSidebar, onOpenTour }) => {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const { unreadCount } = useAlertStore();
  const navigate = useNavigate();
  const [helpOpen, setHelpOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  // Compact initials from display name
  const displayName = user?.displayName || "Safety Officer";
  const initials = displayName
    .split(" ")
    .map((w: string) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <header className="bg-white border-b border-slate-200 px-3 sm:px-5 lg:px-8 py-2.5 flex items-center justify-between gap-2 shadow-xs sticky top-0 z-30 min-w-0">
      {/* Left: Hamburger + Title */}
      <div className="flex items-center gap-2 min-w-0">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 rounded-xl hover:bg-slate-100 text-slate-600 focus:outline-none shrink-0"
          aria-label="Toggle navigation"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div className="min-w-0">
          <h1 className="text-sm sm:text-base font-bold text-slate-900 leading-tight truncate">
            Mine Safety Command Center
          </h1>
        </div>
      </div>

      {/* Right: Actions — collapse on mobile */}
      <div className="flex items-center gap-1.5 sm:gap-2.5 shrink-0">
        {/* Network status — hidden on <md */}
        <div className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 text-[11px] font-semibold border border-emerald-200">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>IN865 Connected</span>
        </div>

        {/* Language Selector — segmented on sm+, icon-only on mobile */}
        <LanguageSelector variant="segmented" className="hidden sm:inline-flex" />
        <LanguageSelector variant="dropdown" className="sm:hidden" />

        {/* Notification Bell */}
        <Link
          to="/app/alerts"
          className="relative p-2 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition"
          title={t("nav.alerts")}
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 right-1.5 h-4 w-4 rounded-full bg-red-600 text-white text-[10px] font-bold flex items-center justify-center animate-pulse">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </Link>

        {/* Help menu — hidden on <sm to save space */}
        <div className="relative hidden sm:block">
          <button
            onClick={() => setHelpOpen(!helpOpen)}
            className="p-2 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition"
            title="Help & Tour"
          >
            <HelpCircle className="h-5 w-5" />
          </button>
          {helpOpen && (
            <div className="absolute right-0 mt-2 w-52 rounded-2xl bg-white border border-slate-200 shadow-xl py-2 z-50 animate-in fade-in-50 zoom-in-95">
              <div className="px-3.5 py-1.5 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">
                Help & Resources
              </div>
              <button
                onClick={() => { setHelpOpen(false); onOpenTour?.(); }}
                className="w-full px-3.5 py-2 text-left text-xs font-bold text-slate-700 hover:bg-blue-50 hover:text-blue-700 flex items-center gap-2.5 transition"
              >
                <Sparkles className="h-4 w-4 text-blue-600" /> Take Product Tour
              </button>
              <button
                onClick={() => { setHelpOpen(false); navigate("/app/settings"); }}
                className="w-full px-3.5 py-2 text-left text-xs font-semibold text-slate-700 hover:bg-slate-50 flex items-center gap-2.5 transition"
              >
                <Activity className="h-4 w-4 text-slate-500" /> System Health & Status
              </button>
              <div className="my-1 border-t border-slate-100" />
              <a
                href="mailto:support@minepulse.internal"
                className="w-full px-3.5 py-2 text-left text-xs font-semibold text-slate-700 hover:bg-slate-50 flex items-center gap-2.5 transition"
              >
                <Mail className="h-4 w-4 text-slate-500" /> Contact Mine Safety Officer
              </a>
            </div>
          )}
        </div>

        {/* User Avatar — initials on mobile, full pill on sm+ */}
        <div className="flex items-center gap-1.5">
          {/* Mobile: compact avatar only */}
          <div className="sm:hidden h-8 w-8 rounded-full bg-slate-800 text-white text-[11px] font-extrabold flex items-center justify-center">
            {initials}
          </div>
          {/* sm+: full name pill */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200 text-slate-800 text-xs font-bold max-w-[160px]">
            <span className="truncate">{displayName}</span>
            <div className="h-5 w-5 rounded-full bg-slate-300 flex items-center justify-center text-slate-700 shrink-0">
              <UserIcon className="h-3.5 w-3.5" />
            </div>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition"
          title="Sign Out"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
};

export default TopBar;
