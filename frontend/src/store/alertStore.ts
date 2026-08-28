import { create } from "zustand";
import { Alert } from "../types";
interface AlertState {
  alerts: Alert[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
  setAlerts: (alerts: Alert[]) => void;
  addAlert: (alert: Alert) => void;
  acknowledgeAlert: (id: number, acknowledgedBy: string) => void;
  resolveAlert: (id: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}
export const useAlertStore = create<AlertState>((set) => ({
  alerts: [],
  unreadCount: 0,
  loading: false,
  error: null,
  setAlerts: (alerts) =>
    set({
      alerts,
      unreadCount: alerts.filter(
        (a) => a.status === "ACTIVE" || a.status === "DETECTED",
      ).length,
    }),
  addAlert: (alert) =>
    set((state) => {
      const exists = state.alerts.some((a) => a.id === alert.id);
      const newAlerts = exists
        ? state.alerts.map((a) => (a.id === alert.id ? alert : a))
        : [alert, ...state.alerts];
      return {
        alerts: newAlerts,
        unreadCount: newAlerts.filter(
          (a) => a.status === "ACTIVE" || a.status === "DETECTED",
        ).length,
      };
    }),
  acknowledgeAlert: (id, acknowledgedBy) =>
    set((state) => {
      const newAlerts = state.alerts.map((a) =>
        a.id === id
          ? {
              ...a,
              status: "ACKNOWLEDGED" as const,
              acknowledged_at: new Date().toISOString(),
              acknowledged_by: acknowledgedBy,
            }
          : a,
      );
      return {
        alerts: newAlerts,
        unreadCount: newAlerts.filter(
          (a) => a.status === "ACTIVE" || a.status === "DETECTED",
        ).length,
      };
    }),
  resolveAlert: (id) =>
    set((state) => {
      const newAlerts = state.alerts.map((a) =>
        a.id === id
          ? {
              ...a,
              status: "RESOLVED" as const,
              resolved_at: new Date().toISOString(),
            }
          : a,
      );
      return {
        alerts: newAlerts,
        unreadCount: newAlerts.filter(
          (a) => a.status === "ACTIVE" || a.status === "DETECTED",
        ).length,
      };
    }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
