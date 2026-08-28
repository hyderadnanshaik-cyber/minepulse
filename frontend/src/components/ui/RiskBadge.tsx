import React from "react";
import { RiskLevel } from "../../types";
interface RiskBadgeProps {
  level: RiskLevel;
  size?: "sm" | "md" | "lg";
}
export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, size = "md" }) => {
  const colorMap: Record<
    RiskLevel,
    { bg: string; text: string; border: string }
  > = {
    NORMAL: {
      bg: "bg-emerald-50",
      text: "text-emerald-700",
      border: "border-emerald-200",
    },
    WATCH: {
      bg: "bg-blue-50",
      text: "text-blue-700",
      border: "border-blue-200",
    },
    WARNING: {
      bg: "bg-amber-50",
      text: "text-amber-700",
      border: "border-amber-200",
    },
    HIGH: {
      bg: "bg-orange-50",
      text: "text-orange-700",
      border: "border-orange-200",
    },
    CRITICAL: {
      bg: "bg-red-50",
      text: "text-red-700",
      border: "border-red-200",
    },
  };
  const style = colorMap[level] || colorMap.NORMAL;
  const sizeClasses = {
    sm: "text-xs px-2 py-0.5 font-medium",
    md: "text-xs px-2.5 py-1 font-semibold tracking-wide",
    lg: "text-sm px-3.5 py-1.5 font-bold tracking-wider",
  };
  return (
    <span
      className={`inline-flex items-center justify-center rounded-md border ${style.bg} ${style.text} ${style.border} ${sizeClasses[size]} uppercase`}
    >
      {" "}
      {level}{" "}
    </span>
  );
};
