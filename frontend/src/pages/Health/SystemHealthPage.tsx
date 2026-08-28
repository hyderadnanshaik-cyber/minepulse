import React from "react";
import { HeartPulse } from "lucide-react";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
export const SystemHealthPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {" "}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card flex items-center justify-between">
        {" "}
        <div className="flex items-center gap-3">
          {" "}
          <div className="p-3 bg-emerald-50 text-emerald-700 rounded-xl">
            {" "}
            <HeartPulse className="h-6 w-6" />{" "}
          </div>{" "}
          <div>
            {" "}
            <h1 className="text-xl font-bold text-slate-900 ">
              System Health & Diagnostics
            </h1>{" "}
            <p className="text-xs text-slate-500 ">
              Service workers, offline queues, battery levels, and telemetry
              heartbeats.
            </p>{" "}
          </div>{" "}
        </div>{" "}
      </div>{" "}
      <div className="bg-white rounded-2xl p-12 border border-slate-200 shadow-card text-center">
        {" "}
        <LoadingSpinner
          size="lg"
          label="System Diagnostics — Loading data..."
        />{" "}
      </div>{" "}
    </div>
  );
};
