import React from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  ShieldAlert,
  Radio,
  Server,
  Activity,
  ChevronRight,
  Cpu,
  Layers,
  ArrowRight,
  Gauge,
  Thermometer,
  BatteryCharging,
  Compass,
  Database,
} from "lucide-react";
import { LanguageSelector } from "../../components/ui/LanguageSelector";
export const OverviewPage: React.FC = () => {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 antialiased font-sans">
      {" "}
      {/* Top Navbar */}{" "}
      <header className="sticky top-0 z-40 bg-white backdrop-blur-md border-b border-slate-200 ">
        {" "}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {" "}
          <div className="flex items-center gap-3">
            {" "}
            <div className="h-9 w-9 rounded-lg bg-blue-700 text-white flex items-center justify-center font-black text-lg shadow-sm">
              {" "}
              MP{" "}
            </div>{" "}
            <div>
              {" "}
              <span className="font-extrabold text-lg text-slate-900 tracking-tight">
                Mine Pulse
              </span>{" "}
              <span className="ml-2 rtl:ml-0 rtl:mr-2 text-xs font-semibold px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full border border-blue-100">
                {" "}
                StrataSafe{" "}
              </span>{" "}
            </div>{" "}
          </div>{" "}
          <div className="flex items-center gap-3">
            {" "}
            {/* Multilingual Selector in Overview Header */}{" "}
            <LanguageSelector
              variant="segmented"
              className="hidden sm:inline-flex"
            />{" "}
            <LanguageSelector variant="dropdown" className="sm:hidden" />{" "}
            <Link
              to="/login"
              className="px-4 py-2 text-sm font-semibold text-slate-700 hover:text-blue-700 transition"
            >
              {" "}
              {t("overview.signIn")}{" "}
            </Link>{" "}
            <Link
              to="/app/dashboard"
              className="px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white text-sm font-bold rounded-lg shadow-sm transition flex items-center gap-1.5"
            >
              {" "}
              {t("overview.launchDashboard")}{" "}
              <ArrowRight className="h-4 w-4 rtl-flip" />{" "}
            </Link>{" "}
          </div>{" "}
        </div>{" "}
      </header>{" "}
      {/* Main Content Sections */}{" "}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
        {" "}
        {/* Section 1: Hero */}{" "}
        <section className="bg-white rounded-3xl p-8 sm:p-12 lg:p-16 border border-slate-200 shadow-sm relative overflow-hidden">
          {" "}
          <div className="max-w-3xl relative z-10">
            {" "}
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 text-xs font-bold rounded-full mb-4 border border-blue-100">
              {" "}
              <span className="h-2 w-2 rounded-full bg-blue-600 animate-pulse" />{" "}
              {t("overview.taglinePill")}{" "}
            </div>{" "}
            <h1 className="text-4xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
              {" "}
              {t("overview.heroTitle")}{" "}
            </h1>{" "}
            <p className="mt-4 text-lg text-slate-600 leading-relaxed font-normal">
              {" "}
              {t("overview.heroDesc")}{" "}
            </p>{" "}
            <div className="mt-8 flex flex-wrap gap-4">
              {" "}
              <Link
                to="/login"
                className="px-6 py-3.5 bg-blue-700 hover:bg-blue-800 text-white font-bold text-sm rounded-xl shadow-md transition flex items-center gap-2"
              >
                {" "}
                {t("overview.accessControl")}{" "}
                <ChevronRight className="h-4 w-4 rtl-flip" />{" "}
              </Link>{" "}
              <a
                href="#architecture"
                className="px-6 py-3.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-sm rounded-xl transition"
              >
                {" "}
                {t("overview.exploreArch")}{" "}
              </a>{" "}
            </div>{" "}
          </div>{" "}
          <div className="hidden lg:block absolute right-10 top-1/2 -translate-y-1/2 opacity-15 pointer-events-none">
            {" "}
            <ShieldAlert className="w-96 h-96 text-blue-900" />{" "}
          </div>{" "}
        </section>{" "}
        {/* Section 2: About the System */}{" "}
        <section className="bg-white rounded-2xl p-8 border border-slate-200 shadow-card">
          {" "}
          <div className="flex items-center gap-3 mb-4">
            {" "}
            <div className="p-2.5 bg-blue-50 text-blue-700 rounded-lg">
              {" "}
              <Activity className="h-6 w-6" />{" "}
            </div>{" "}
            <div>
              {" "}
              <h2 className="text-2xl font-bold text-slate-900 ">
                {t("overview.aboutTitle")}
              </h2>{" "}
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                {t("overview.aboutSub")}
              </p>{" "}
            </div>{" "}
          </div>{" "}
          <p className="text-slate-600 leading-relaxed">
            {" "}
            {t("overview.aboutDesc")}{" "}
          </p>{" "}
        </section>{" "}
        {/* Section 3: Engineering Pillars */}{" "}
        <section className="bg-white rounded-2xl p-8 border border-slate-200 shadow-card">
          {" "}
          <div className="flex items-center gap-3 mb-6">
            {" "}
            <div className="p-2.5 bg-emerald-50 text-emerald-700 rounded-lg">
              {" "}
              <Layers className="h-6 w-6" />{" "}
            </div>{" "}
            <div>
              {" "}
              <h2 className="text-2xl font-bold text-slate-900 ">
                {t("overview.pillarsTitle")}
              </h2>{" "}
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                {t("overview.pillarsSub")}
              </p>{" "}
            </div>{" "}
          </div>{" "}
          <div className="grid sm:grid-cols-3 gap-5">
            {" "}
            <div className="p-5 bg-emerald-50/50 border border-emerald-100 rounded-2xl">
              {" "}
              <h4 className="font-bold text-emerald-900 text-base">
                {t("overview.p1Title")}
              </h4>{" "}
              <p className="text-xs text-emerald-800 mt-2 leading-relaxed">
                {t("overview.p1Desc")}
              </p>{" "}
            </div>{" "}
            <div className="p-5 bg-blue-50/50 border border-blue-100 rounded-2xl">
              {" "}
              <h4 className="font-bold text-blue-900 text-base">
                {t("overview.p2Title")}
              </h4>{" "}
              <p className="text-xs text-blue-800 mt-2 leading-relaxed">
                {t("overview.p2Desc")}
              </p>{" "}
            </div>{" "}
            <div className="p-5 bg-indigo-50/50 border border-indigo-100 rounded-2xl">
              {" "}
              <h4 className="font-bold text-indigo-900 text-base">
                {t("overview.p3Title")}
              </h4>{" "}
              <p className="text-xs text-indigo-800 mt-2 leading-relaxed">
                {t("overview.p3Desc")}
              </p>{" "}
            </div>{" "}
          </div>{" "}
        </section>{" "}
        {/* Section 4: End-to-End Architecture */}{" "}
        <section
          id="architecture"
          className="bg-white rounded-2xl p-8 border border-slate-200 shadow-card"
        >
          {" "}
          <div className="flex items-center gap-3 mb-6">
            {" "}
            <div className="p-2.5 bg-indigo-50 text-indigo-700 rounded-lg">
              {" "}
              <Radio className="h-6 w-6" />{" "}
            </div>{" "}
            <div>
              {" "}
              <h2 className="text-2xl font-bold text-slate-900 ">
                03. End-to-End Field Architecture
              </h2>{" "}
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                LoRa SX1276 IN865 (865.2 MHz) ➔ Raspberry Pi Zero 2 W Gateway ➔
                PostgreSQL 18 PostGIS
              </p>{" "}
            </div>{" "}
          </div>{" "}
          <div className="bg-slate-50 p-6 rounded-xl border border-slate-200 overflow-x-auto">
            {" "}
            <div className="min-w-[700px] flex items-center justify-between gap-4 text-center">
              {" "}
              {/* Layer 1 */}{" "}
              <div className="flex-1 p-4 bg-white rounded-xl border border-blue-200 shadow-xs">
                {" "}
                <Radio className="h-8 w-8 text-blue-600 mx-auto mb-2" />{" "}
                <div className="font-bold text-sm text-slate-800 ">
                  ESP32 Sensor Nodes (×20 Grid)
                </div>{" "}
                <div className="text-[11px] text-slate-500 mt-1">
                  MPU9250 9-Axis + BME280 + Draw-Wire + Crack Gauge + SX1276
                </div>{" "}
              </div>{" "}
              <div className="text-blue-500 font-black text-xl rtl-flip">➔</div>{" "}
              {/* Layer 2 */}{" "}
              <div className="flex-1 p-4 bg-white rounded-xl border border-indigo-200 shadow-xs">
                {" "}
                <Server className="h-8 w-8 text-indigo-600 mx-auto mb-2" />{" "}
                <div className="font-bold text-sm text-slate-800 ">
                  MINEGATE Central Gateway
                </div>{" "}
                <div className="text-[11px] text-slate-500 mt-1">
                  RPi Zero 2 W + IN865 Concentrator + SIM7600E-H 4G + GPIO 18
                  Siren
                </div>{" "}
              </div>{" "}
              <div className="text-indigo-500 font-black text-xl rtl-flip">
                ➔
              </div>{" "}
              {/* Layer 3 */}{" "}
              <div className="flex-1 p-4 bg-white rounded-xl border border-emerald-200 shadow-xs">
                {" "}
                <Database className="h-8 w-8 text-emerald-600 mx-auto mb-2" />{" "}
                <div className="font-bold text-sm text-slate-800 ">
                  PostgreSQL 18 + PostGIS + AI
                </div>{" "}
                <div className="text-[11px] text-slate-500 mt-1">
                  FastAPI Backend, Isolation Forest ML, Offline React PWA
                </div>{" "}
              </div>{" "}
            </div>{" "}
          </div>{" "}
        </section>{" "}
        {/* Section 5: Hardware Overview */}{" "}
        <section className="bg-white rounded-2xl p-8 border border-slate-200 shadow-card">
          {" "}
          <div className="flex items-center gap-3 mb-6">
            {" "}
            <div className="p-2.5 bg-blue-50 text-blue-700 rounded-lg">
              {" "}
              <Cpu className="h-6 w-6" />{" "}
            </div>{" "}
            <div>
              {" "}
              <h2 className="text-2xl font-bold text-slate-900 ">
                {t("overview.hardwareTitle")}
              </h2>{" "}
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                {t("overview.hardwareSub")}
              </p>{" "}
            </div>{" "}
          </div>{" "}
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {" "}
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
              {" "}
              <Compass className="h-5 w-5 text-blue-600 mb-2" />{" "}
              <h4 className="font-bold text-sm text-slate-900 ">
                MPU9250 9-Axis IMU
              </h4>{" "}
              <p className="text-xs text-slate-600 mt-1">
                3-Axis Gyro + 3-Axis Accel + 3-Axis Magnetometer with precision
                tilt fusion.
              </p>{" "}
            </div>{" "}
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
              {" "}
              <Gauge className="h-5 w-5 text-indigo-600 mb-2" />{" "}
              <h4 className="font-bold text-sm text-slate-900 ">
                Draw-Wire & Crack Gauge
              </h4>{" "}
              <p className="text-xs text-slate-600 mt-1">
                Continuous sub-mm displacement transducer and potentiometric
                crack gauge on ADS1115.
              </p>{" "}
            </div>{" "}
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
              {" "}
              <Thermometer className="h-5 w-5 text-emerald-600 mb-2" />{" "}
              <h4 className="font-bold text-sm text-slate-900 ">
                BME280 & DS3231 RTC
              </h4>{" "}
              <p className="text-xs text-slate-600 mt-1">
                Ambient temperature, barometric pressure, humidity, and
                battery-backed hardware timestamping.
              </p>{" "}
            </div>{" "}
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
              {" "}
              <BatteryCharging className="h-5 w-5 text-amber-600 mb-2" />{" "}
              <h4 className="font-bold text-sm text-slate-900 ">
                Solar LiFePO4 Battery
              </h4>{" "}
              <p className="text-xs text-slate-600 mt-1">
                Safe 3.2V LiFePO4 chemistry with solar energy harvesting and
                continuous charging circuit.
              </p>{" "}
            </div>{" "}
          </div>{" "}
        </section>{" "}
      </main>{" "}
      {/* Footer */}{" "}
      <footer className="bg-white border-t border-slate-200 py-8">
        {" "}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 ">
          {" "}
          <div className="flex items-center gap-2">
            {" "}
            <span className="font-bold text-slate-900 ">Mine Pulse</span>{" "}
            <span>•</span> <span>SIH 2026 Problem SIH26025</span> <span>•</span>{" "}
            <span>Team RED HACK</span>{" "}
          </div>{" "}
          <div>
            {" "}
            <span>
              StrataSafe — AI-Powered Mine Safety & Geotechnical Monitoring
              Platform
            </span>{" "}
          </div>{" "}
        </div>{" "}
      </footer>{" "}
    </div>
  );
};
export default OverviewPage;
