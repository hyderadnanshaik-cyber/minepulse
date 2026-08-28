interface QueuedItem {
  id: string;
  url: string;
  method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  body: unknown;
  timestamp: number;
}
const STORAGE_KEY = "redhack_offline_queue";
export class OfflineQueue {
  private static getQueue(): QueuedItem[] {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }
  private static setQueue(queue: QueuedItem[]): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(queue));
    } catch (e) {
      console.error("Failed to save offline queue", e);
    }
  }
  public static enqueue(
    url: string,
    method: QueuedItem["method"],
    body: unknown,
  ): void {
    const queue = this.getQueue();
    const item: QueuedItem = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      url,
      method,
      body,
      timestamp: Date.now(),
    };
    queue.push(item);
    this.setQueue(queue);
  }
  public static getPendingCount(): number {
    return this.getQueue().length;
  }
  public static clearQueue(): void {
    localStorage.removeItem(STORAGE_KEY);
  }
  public static getPendingItems(): QueuedItem[] {
    return this.getQueue();
  }
}
