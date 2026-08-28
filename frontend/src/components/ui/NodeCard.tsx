import React from "react";
import { Node, SensorReading } from "../../types";
import { StatusBadge } from "./StatusBadge";
import { Battery, Wifi, Activity, ChevronRight } from "lucide-react";
import { Link } from "react-router-dom";
interface NodeCardProps {
  node: Node;
  latestReading?: SensorReading;
  onLocate?: (id: number) => void;
}
export const NodeCard: React.FC<NodeCardProps> = ({
  node,
  latestReading,
  onLocate,
}) => {
  const getBatteryColor = (level: number) => {
    if (level > 60) return "text-emerald-600";
    if (level > 20) return "text-amber-500";
    return "text-rose-600 animate-pulse";
  };
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-card hover:shadow-card-hover transition-all flex flex-col justify-between">
      {" "}
      <div>
        {" "}
        <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-3">
          {" "}
          <div className="flex items-center gap-2">
            {" "}
            <span className="h-2.5 w-2.5 rounded-full bg-blue-600"></span>{" "}
            <h4 className="font-bold text-slate-800 tracking-tight">
              {node.node_code}
            </h4>{" "}
            {node.is_root && (
              <span className="bg-blue-100 text-blue-800 text-[10px] font-bold px-1.5 py-0.5 rounded">
                {" "}
                ROOT{" "}
              </span>
            )}{" "}
          </div>{" "}
          <StatusBadge status={node.status} size="sm" />{" "}
        </div>{" "}
        <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 mb-4">
          {" "}
          <div className="flex items-center gap-1.5 bg-slate-50 p-2 rounded-lg">
            {" "}
            <Battery
              className={`h-4 w-4 ${getBatteryColor(node.battery_level)}`}
            />{" "}
            <span>
              Batt:{" "}
              <strong className="text-slate-800 ">{node.battery_level}%</strong>
            </span>{" "}
          </div>{" "}
          <div className="flex items-center gap-1.5 bg-slate-50 p-2 rounded-lg">
            {" "}
            <Wifi className="h-4 w-4 text-blue-500" />{" "}
            <span>
              RSSI:{" "}
              <strong className="text-slate-800 ">
                {node.signal_strength} dBm
              </strong>
            </span>{" "}
          </div>{" "}
          <div className="flex items-center gap-1.5 bg-slate-50 p-2 rounded-lg">
            {" "}
            <Activity className="h-4 w-4 text-indigo-500" />{" "}
            <span>
              Layer:{" "}
              <strong className="text-slate-800 ">{node.mesh_layer}</strong>
            </span>{" "}
          </div>{" "}
          <div className="flex items-center gap-1.5 bg-slate-50 p-2 rounded-lg">
            {" "}
            <span>
              Depth:{" "}
              <strong className="text-slate-800 ">{node.depth_m}m</strong>
            </span>{" "}
          </div>{" "}
        </div>{" "}
        {latestReading && (
          <div className="bg-slate-50 border border-slate-100 rounded-lg p-2.5 text-xs mb-4">
            {" "}
            <div className="text-[11px] uppercase tracking-wider font-semibold text-slate-400 mb-1">
              {" "}
              Latest Live Reading{" "}
            </div>{" "}
            <div className="flex justify-between items-center text-slate-700 ">
              {" "}
              <span>Displacement:</span>{" "}
              <strong className="text-slate-900 font-mono">
                {(
                  latestReading.displacement_mm ??
                  latestReading.displacement ??
                  0
                ).toFixed(2)}{" "}
                mm
              </strong>{" "}
            </div>{" "}
            <div className="flex justify-between items-center text-slate-700 mt-1">
              {" "}
              <span>Tilt (X / Y):</span>{" "}
              <strong className="text-slate-900 font-mono">
                {(
                  latestReading.tilt_x_deg ??
                  latestReading.tilt_x ??
                  0
                ).toFixed(1)}
                ° /{" "}
                {(
                  latestReading.tilt_y_deg ??
                  latestReading.tilt_y ??
                  0
                ).toFixed(1)}
                °
              </strong>{" "}
            </div>{" "}
          </div>
        )}{" "}
      </div>{" "}
      <div className="flex items-center justify-between pt-3 border-t border-slate-100 mt-2">
        {" "}
        {onLocate && (
          <button
            onClick={() => onLocate(node.id)}
            className="text-xs font-semibold text-blue-700 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-2.5 py-1.5 rounded-md transition"
          >
            {" "}
            Locate Node{" "}
          </button>
        )}{" "}
        <Link
          to={`/app/nodes/${node.id}`}
          className="text-xs font-semibold text-slate-600 hover:text-blue-600 flex items-center ml-auto transition"
        >
          {" "}
          Details <ChevronRight className="h-3.5 w-3.5 ml-0.5" />{" "}
        </Link>{" "}
      </div>{" "}
    </div>
  );
};
