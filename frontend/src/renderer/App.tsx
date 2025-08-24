import React from "react";
import type { UINode } from "./types";
import { connectWebSocket, sendEvent } from "./ws";

function Text({ node }: { node: UINode }) {
  return <span>{node.props.text}</span>;
}

function Button({ node, ws }: { node: UINode; ws: WebSocket }) {
  const clickEnabled = node.props?.events?.click;
  return (
    <button
      onClick={() => clickEnabled && sendEvent(ws, node.id, "click")}
      style={{ padding: "6px 10px", fontSize: 14 }}
    >
      {node.props.label}
    </button>
  );
}

function InputText({ node, ws }: { node: UINode; ws: WebSocket }) {
  const changeEnabled = node.props?.events?.change;
  return (
    <input
      value={node.props.value ?? ""}
      placeholder={node.props.placeholder ?? ""}
      onChange={(e) => changeEnabled && sendEvent(ws, node.id, "change", e.target.value)}
      style={{ padding: 6, fontSize: 14 }}
    />
  );
}

function NumberInput({ node, ws }: { node: UINode; ws: WebSocket }) {
  const changeEnabled = node.props?.events?.change;
  return (
    <input
      type="number"
      value={node.props.value ?? 0}
      step={node.props.step ?? 1}
      onChange={(e) =>
        changeEnabled && sendEvent(ws, node.id, "change", parseFloat(e.target.value))
      }
      style={{ padding: 6, fontSize: 14, width: 120 }}
    />
  );
}

function VStack({ node, ws }: { node: UINode; ws: WebSocket }) {
  const gap = node.props.gap ?? 8;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap }}>
      {node.children.map((c) => (
        <Node key={c.id} node={c} ws={ws} />
      ))}
    </div>
  );
}

function HStack({ node, ws }: { node: UINode; ws: WebSocket }) {
  const gap = node.props.gap ?? 8;
  const alignItems = node.props.align ?? "center";
  const justifyContent = node.props.justify ?? "start";
  return (
    <div style={{ display: "flex", flexDirection: "row", gap, alignItems, justifyContent }}>
      {node.children.map((c) => (
        <Node key={c.id} node={c} ws={ws} />
      ))}
    </div>
  );
}

function Node({ node, ws }: { node: UINode; ws: WebSocket }) {
  switch (node.type) {
    case "Text":
      return <Text node={node} />;
    case "Button":
      return <Button node={node} ws={ws} />;
    case "InputText":
      return <InputText node={node} ws={ws} />;
    case "NumberInput":
      return <NumberInput node={node} ws={ws} />;
    case "VStack":
      return <VStack node={node} ws={ws} />;
    case "HStack":
      return <HStack node={node} ws={ws} />;
    default:
      return <div>Unknown: {node.type}</div>;
  }
}

export function App() {
  const [tree, setTree] = React.useState<UINode | null>(null);
  const wsRef = React.useRef<WebSocket | null>(null);

  React.useEffect(() => {
    const ws = connectWebSocket((t) => setTree(t));
    wsRef.current = ws;
    return () => ws.close();
  }, []);

  if (!tree) return <div style={{ padding: 16 }}>Connecting...</div>;
  return (
    <div style={{ padding: 16 }}>
      <Node node={tree} ws={wsRef.current!} />
    </div>
  );
}


