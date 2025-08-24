import type { UINode } from "./types";

export type MessageFromServer = UINode;

export type MessageToServer = {
  event: string;
  nodeId: string;
  value?: any;
};

export function connectWebSocket(onTree: (tree: UINode) => void): WebSocket {
  const origin = window.location.origin; // http(s)://host[:port]
  const wsUrl = origin.replace(/^http/, "ws") + "/ws";
  const ws = new WebSocket(wsUrl);
  ws.onmessage = (ev) => {
    try {
      const parsed = JSON.parse(ev.data) as MessageFromServer;
      onTree(parsed);
    } catch {}
  };
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


