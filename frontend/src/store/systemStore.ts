import { create } from "zustand";
import {
  SystemStatus,
  GatewayStatus,
  ConnectionHealth,
  SyncStatus,
} from "../types";

export interface SystemState {
  status: SystemStatus;
  gateway: GatewayStatus | null;
  lastChecked: string;
  setMeshStatus: (status: ConnectionHealth) => void;
  setGatewayStatus: (status: ConnectionHealth) => void;
  setInternetStatus: (status: "ONLINE" | "OFFLINE" | "UNKNOWN") => void;
  setCloudStatus: (status: SyncStatus) => void;
  setGatewayDetails: (gateway: GatewayStatus | null) => void;
  setStatus: (status: Partial<SystemStatus>) => void;
  updateFullStatus: (status: Partial<SystemStatus>) => void;
}

export const useSystemStore = create<SystemState>((set) => ({
  status: {
    mesh_status: "ONLINE",
    gateway_status: "ONLINE",
    internet_status:
      typeof navigator !== "undefined" && navigator.onLine
        ? "ONLINE"
        : "OFFLINE",
    cloud_status: "ONLINE",
    db_status: "ONLINE",
  },
  gateway: null,
  lastChecked: new Date().toISOString(),
  setMeshStatus: (mesh_status) =>
    set((state) => ({
      status: { ...state.status, mesh_status },
      lastChecked: new Date().toISOString(),
    })),
  setGatewayStatus: (gateway_status) =>
    set((state) => ({
      status: { ...state.status, gateway_status },
      lastChecked: new Date().toISOString(),
    })),
  setInternetStatus: (internet_status) =>
    set((state) => ({
      status: { ...state.status, internet_status },
      lastChecked: new Date().toISOString(),
    })),
  setCloudStatus: (cloud_status) =>
    set((state) => ({
      status: { ...state.status, cloud_status },
      lastChecked: new Date().toISOString(),
    })),
  setGatewayDetails: (gateway) => set({ gateway }),
  setStatus: (partial) =>
    set((state) => ({
      status: { ...state.status, ...partial },
      lastChecked: new Date().toISOString(),
    })),
  updateFullStatus: (partial) =>
    set((state) => ({
      status: { ...state.status, ...partial },
      lastChecked: new Date().toISOString(),
    })),
}));
