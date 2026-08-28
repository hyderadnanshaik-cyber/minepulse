import { create } from "zustand";
import { Node, SensorReading, Panel } from "../types";
interface NodeState {
  nodes: Node[];
  panels: Panel[];
  latestReadings: Record<number, SensorReading>;
  selectedNodeId: number | null;
  loading: boolean;
  error: string | null;
  setNodes: (nodes: Node[]) => void;
  setPanels: (panels: Panel[]) => void;
  updateNode: (id: number, patch: Partial<Node>) => void;
  updateReading: (reading: SensorReading) => void;
  setSelectedNodeId: (id: number | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}
export const useNodeStore = create<NodeState>((set) => ({
  nodes: [],
  panels: [],
  latestReadings: {},
  selectedNodeId: null,
  loading: false,
  error: null,
  setNodes: (nodes) => set({ nodes }),
  setPanels: (panels) => set({ panels }),
  updateNode: (id, patch) =>
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === id ? { ...node, ...patch } : node,
      ),
    })),
  updateReading: (reading) =>
    set((state) => ({
      latestReadings: { ...state.latestReadings, [reading.node_id]: reading },
    })),
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
