type MessageHandler = (data: unknown) => void;
class WebSocketClient {
  private socket: WebSocket | null = null;
  private url: string;
  private reconnectInterval: number = 5000;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private isExplicitlyClosed: boolean = false;
  constructor() {
    // Auto-detect protocol + host so it works on Vercel (wss://) and localhost (ws://)
    const wsBase = import.meta.env.VITE_WS_BASE_URL ||
      `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`;
    this.url = `${wsBase}/ws/live`;
  }
  public connect(): void {
    if (
      this.socket &&
      (this.socket.readyState === WebSocket.OPEN ||
        this.socket.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }
    this.isExplicitlyClosed = false;
    try {
      this.socket = new WebSocket(this.url);
      this.socket.onopen = () => {
        this.emit("connection_change", { status: "CONNECTED" });
      };
      this.socket.onmessage = (event: MessageEvent) => {
        try {
          const parsed = JSON.parse(event.data);
          const type = parsed.type || "message";
          this.emit(type, parsed.payload || parsed);
        } catch {
          this.emit("raw_message", event.data);
        }
      };
      this.socket.onclose = () => {
        this.emit("connection_change", { status: "DISCONNECTED" });
        if (!this.isExplicitlyClosed) {
          this.scheduleReconnect();
        }
      };
      this.socket.onerror = (error) => {
        this.emit("error", error);
      };
    } catch {
      this.scheduleReconnect();
    }
  }
  private scheduleReconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    this.reconnectTimeout = setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
  }
  public subscribe(eventType: string, handler: MessageHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler);
    return () => {
      this.handlers.get(eventType)?.delete(handler);
    };
  }
  private emit(eventType: string, data: unknown): void {
    const callbacks = this.handlers.get(eventType);
    if (callbacks) {
      callbacks.forEach((handler) => handler(data));
    }
  }
  public send(type: string, payload: unknown): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type, payload }));
    }
  }
  public disconnect(): void {
    this.isExplicitlyClosed = true;
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
export const wsClient = new WebSocketClient();
