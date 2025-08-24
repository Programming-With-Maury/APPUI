import type { UINode } from "./types";

export type MessageFromServer = UINode;

export type MessageToServer = {
  event: string;
  nodeId: string;
  value?: any;
};

export function connectWebSocket(onTree: (tree: UINode) => void): WebSocket {
  const origin = window.location.origin; // http(s)://host[:port]
  // Forward the current path (without leading slash) to seed server-side route
  const currentPath = window.location.pathname.replace(/^\//, "");
  const query = currentPath ? `?path=${encodeURIComponent(currentPath)}` : "";
  const wsUrl = origin.replace(/^http/, "ws") + "/ws" + query;
  const ws = new WebSocket(wsUrl);
  ws.onmessage = (ev) => {
    try {
      const parsed = JSON.parse(ev.data) as MessageFromServer;
      onTree(parsed);
    } catch {}
  };
  // Keep server in sync on back/forward navigation
  window.addEventListener("popstate", () => {
    const path = window.location.pathname.replace(/^\//, "");
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ event: "navigate", nodeId: "__route__", value: path }));
    }
  });
  return ws;
}

export function sendEvent(
  ws: WebSocket,
  nodeId: string,
  event: string,
  value?: any
) {
  const payload: MessageToServer = { event, nodeId, value };
  ws.readyState === WebSocket.OPEN && ws.send(JSON.stringify(payload));
}


