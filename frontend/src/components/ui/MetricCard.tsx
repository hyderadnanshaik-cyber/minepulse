import React, { ReactNode } from "react";
interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  trend?: { value: string; isPositive?: boolean; label?: string };
  className?: string;
  statusColor?: "blue" | "green" | "amber" | "red" | "gray";
}
export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  className = "",
  statusColor = "blue",
}) => {
  const borderColors = {
    blue: "border-l-blue-600",
    green: "border-l-emerald-600",
    amber: "border-l-amber-500",
    red: "border-l-red-600",
    gray: "border-l-slate-400",
  };
  return (
    <div
      className={`bg-white rounded-xl p-5 border border-slate-200 border-l-4 ${borderColors[statusColor]} shadow-card hover:shadow-card-hover transition-all duration-200 ${className}`}
    >
      {" "}
      <div className="flex items-center justify-between">
        {" "}
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 ">
          {title}
        </span>{" "}
        {icon && (
          <div className="p-2 bg-slate-50 rounded-lg text-slate-600 ">
            {icon}
          </div>
        )}{" "}
      </div>{" "}
      <div className="mt-3 flex items-baseline gap-2">
        {" "}
        <span className="text-2xl font-bold tracking-tight text-slate-900 ">
          {value}
        </span>{" "}
        {subtitle && (
          <span className="text-xs text-slate-500 font-medium">{subtitle}</span>
        )}{" "}
      </div>{" "}
      {trend && (
        <div className="mt-2.5 flex items-center text-xs font-medium">
          {" "}
          <span
            className={trend.isPositive ? "text-emerald-600" : "text-rose-600"}
          >
            {" "}
            {trend.value}{" "}
          </span>{" "}
          {trend.label && (
            <span className="ml-1 text-slate-500 ">{trend.label}</span>
          )}{" "}
        </div>
      )}{" "}
    </div>
  );
};
