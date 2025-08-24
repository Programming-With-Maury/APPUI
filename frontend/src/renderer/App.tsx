import React from "react";
import type { UINode } from "./types";
import { connectWebSocket, sendEvent } from "./ws";
import { marked } from "marked";
import * as echarts from "echarts";
import { Icon } from "./Icon";

function Text({ node }: { node: UINode }) {
  return <span>{node.props.text}</span>;
}

function Button({ node, ws }: { node: UINode; ws: WebSocket }) {
  const clickEnabled = node.props?.events?.click;
  const variant: string = node.props?.variant ?? "default";
  return (
    <button
      onClick={() => clickEnabled && sendEvent(ws, node.id, "click")}
      className={["btn", variant === "primary" && "btn--primary", variant === "danger" && "btn--danger"].filter(Boolean).join(" ")}
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
      className="input"
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
      className="input"
    />
  );
}

function VStack({ node, ws }: { node: UINode; ws: WebSocket }) {
  const gap = node.props.gap ?? 8;
  return (
    <div className="stack stack--v" style={{ gap }}>
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
    <div className="stack stack--h" style={{ gap, alignItems, justifyContent }}>
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
    case "Header": {
      const L = Math.min(Math.max(node.props.level ?? 2, 1), 6);
      const Tag = (`h${L}` as unknown) as keyof JSX.IntrinsicElements;
      return <Tag>{node.props.text}</Tag>;
    }
    case "Paragraph":
      return <p>{node.props.text}</p>;
    case "Button":
      return <Button node={node} ws={ws} />;
    case "InputText":
      return <InputText node={node} ws={ws} />;
    case "NumberInput":
      return <NumberInput node={node} ws={ws} />;
    case "Slider": {
      const enabled = node.props?.events?.change;
      return (
        <div className="stack stack--h" style={{ gap: 8 }}>
          <input
            type="range"
            min={node.props.min ?? 0}
            max={node.props.max ?? 100}
            step={node.props.step ?? 1}
            value={node.props.value ?? 0}
            onChange={(e) => enabled && sendEvent(ws, node.id, "change", parseFloat(e.target.value))}
          />
          <span>{node.props.value}</span>
        </div>
      );
    }
    case "TextArea": {
      const enabled = node.props?.events?.change;
      return (
        <textarea
          className="input"
          rows={node.props.rows ?? 3}
          placeholder={node.props.placeholder ?? ""}
          value={node.props.value ?? ""}
          onChange={(e) => enabled && sendEvent(ws, node.id, "change", e.target.value)}
        />
      );
    }
    case "Radio": {
      const enabled = node.props?.events?.change;
      const options: string[] = node.props.options ?? [];
      const value: string | undefined = node.props.value;
      return (
        <div className="stack stack--v" style={{ gap: 6 }}>
          {options.map((opt) => (
            <label key={opt} className="checkbox">
              <input
                type="radio"
                name={node.id}
                checked={value === opt}
                onChange={() => enabled && sendEvent(ws, node.id, "change", opt)}
              />
              {opt}
            </label>
          ))}
        </div>
      );
    }
    case "MultiSelect": {
      const enabled = node.props?.events?.change;
      const options: string[] = node.props.options ?? [];
      const values: string[] = node.props.values ?? [];
      return (
        <select
          multiple
          className="select"
          value={values}
          onChange={(e) => {
            const selected = Array.from(e.target.selectedOptions).map((o) => o.value);
            enabled && sendEvent(ws, node.id, "change", selected);
          }}
        >
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      );
    }
    case "DateInput": {
      const enabled = node.props?.events?.change;
      return (
        <input
          type="date"
          className="input"
          value={node.props.value ?? ""}
          onChange={(e) => enabled && sendEvent(ws, node.id, "change", e.target.value)}
        />
      );
    }
    case "TimeInput": {
      const enabled = node.props?.events?.change;
      return (
        <input
          type="time"
          className="input"
          value={node.props.value ?? ""}
          onChange={(e) => enabled && sendEvent(ws, node.id, "change", e.target.value)}
        />
      );
    }
    case "Image":
      return (
        <img src={node.props.src} alt={node.props.alt ?? ""} width={node.props.width} height={node.props.height} style={{ maxWidth: "100%", borderRadius: 8 }} />
      );
    case "Code":
      return (
        <pre style={{ background: "#0b1220", color: "#e5e7eb", padding: 12, borderRadius: 8, overflowX: "auto" }}>
          <code>{node.props.content ?? ""}</code>
        </pre>
      );
    case "Json": {
      const str = JSON.stringify(node.props.data ?? null, null, 2);
      return (
        <pre style={{ background: "#0b1220", color: "#e5e7eb", padding: 12, borderRadius: 8, overflowX: "auto" }}>
          <code>{str}</code>
        </pre>
      );
    }
    case "Progress": {
      const v = Math.max(0, Math.min(100, Number(node.props.value ?? 0)));
      return (
        <div style={{ background: "var(--border)", height: 10, borderRadius: 999 }}>
          <div style={{ width: `${v}%`, height: 10, background: "var(--primary)", borderRadius: 999 }} />
        </div>
      );
    }
    case "Expander": {
      const open: boolean = !!node.props.open;
      const toggleEnabled = node.props?.events?.toggle;
      return (
        <div className="card">
          <button className="btn" onClick={() => toggleEnabled && sendEvent(ws, node.id, "toggle", !open)}>
            {open ? "▾" : "▸"} {node.props.title ?? "Details"}
          </button>
          {open && (
            <div style={{ marginTop: 8 }}>
              {node.children.map((c) => (
                <Node key={c.id} node={c} ws={ws} />
              ))}
            </div>
          )}
        </div>
      );
    }
    case "Modal": {
      const open: boolean = !!node.props.open;
      const closeEnabled = node.props?.events?.close;
      if (!open) return null;
      return (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", padding: 16 }}>
          <div className="card" style={{ maxWidth: 720, width: "100%" }}>
            <div className="stack stack--h" style={{ justifyContent: "space-between", marginBottom: 8 }}>
              <div className="card__title">{node.props.title ?? "Modal"}</div>
              <button className="btn" onClick={() => closeEnabled && sendEvent(ws, node.id, "close")}>Close</button>
            </div>
            {node.children.map((c) => (
              <Node key={c.id} node={c} ws={ws} />
            ))}
          </div>
        </div>
      );
    }
    case "DataEditor": {
      const cols: string[] = node.props.columns ?? [];
      const rows: any[][] = node.props.rows ?? [];
      const cellEnabled = node.props?.events?.cell;
      return (
        <div style={{ overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                {cols.map((c) => (
                  <th key={c}>{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i}>
                  {r.map((cell, j) => (
                    <td key={j}>
                      <input
                        className="input"
                        value={String(cell)}
                        onChange={(e) => cellEnabled && sendEvent(ws, node.id, "cell", { row: i, col: j, value: e.target.value })}
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }
    case "Download": {
      const dataStr = `data:${node.props.mime ?? "text/plain"};charset=utf-8,` + encodeURIComponent(node.props.content ?? "");
      return (
        <a href={dataStr} download={node.props.filename ?? "download.txt"} className="btn">
          {node.props.label ?? "Download"}
        </a>
      );
    }
    case "Alert": {
      const kind = node.props.kind ?? "info";
      const bg = kind === "error" ? "#fee2e2" : kind === "warning" ? "#fef3c7" : "#dbeafe";
      const color = "#111827";
      return <div className="card" style={{ background: bg, color }}>{node.props.message}</div>;
    }
    case "Toast": {
      const kind = node.props.kind ?? "info";
      const bg = kind === "error" ? "#fee2e2" : kind === "warning" ? "#fef3c7" : "#dbeafe";
      return (
        <div style={{ position: "fixed", bottom: 16, left: 16, background: bg, padding: 8, borderRadius: 8, boxShadow: "var(--shadow)" }}>
          {node.props.message}
        </div>
      );
    }
    case "Spinner":
      return (
        <div className="stack stack--h" style={{ gap: 8, alignItems: "center" }}>
          <div style={{ width: 16, height: 16, border: "2px solid var(--border)", borderTopColor: "var(--primary)", borderRadius: "50%", animation: "spin 1s linear infinite" }} />
          {node.props.label && <span>{node.props.label}</span>}
        </div>
      );
    case "Audio":
      return <audio src={node.props.src} controls={node.props.controls ?? true} autoPlay={!!node.props.autoplay} style={{ width: "100%" }} />;
    case "Video":
      return <video src={node.props.src} controls={node.props.controls ?? true} autoPlay={!!node.props.autoplay} style={{ width: "100%", borderRadius: 8 }} />;
    case "Form": {
      const submitEnabled = node.props?.events?.submit;
      return (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submitEnabled && sendEvent(ws, node.id, "submit");
          }}
        >
          <div className="stack stack--v" style={{ gap: 8 }}>
            {node.children.map((c) => (
              <Node key={c.id} node={c} ws={ws} />
            ))}
            <div>
              <button type="submit" className="btn btn--primary">Submit</button>
            </div>
          </div>
        </form>
      );
    }
    case "Color": {
      const enabled = node.props?.events?.change;
      return (
        <input type="color" value={node.props.value ?? "#000000"} onChange={(e) => enabled && sendEvent(ws, node.id, "change", e.target.value)} />
      );
    }
    case "RangeSlider": {
      const enabled = node.props?.events?.change;
      const minV: number = node.props.minValue ?? 0;
      const maxV: number = node.props.maxValue ?? 100;
      const min = node.props.min ?? 0;
      const max = node.props.max ?? 100;
      const step = node.props.step ?? 1;
      return (
        <div className="stack stack--h" style={{ gap: 8, alignItems: "center" }}>
          <input type="range" min={min} max={max} step={step} value={minV} onChange={(e) => enabled && sendEvent(ws, node.id, "change", { min: parseFloat(e.target.value), max: maxV })} />
          <input type="range" min={min} max={max} step={step} value={maxV} onChange={(e) => enabled && sendEvent(ws, node.id, "change", { min: minV, max: parseFloat(e.target.value) })} />
          <span>{minV} - {maxV}</span>
        </div>
      );
    }
    case "DateTime": {
      const enabled = node.props?.events?.change;
      return (
        <input type="datetime-local" className="input" value={node.props.value ?? ""} onChange={(e) => enabled && sendEvent(ws, node.id, "change", e.target.value)} />
      );
    }
    case "Checkbox": {
      const enabled = node.props?.events?.change;
      return (
        <label className="checkbox">
          <input
            type="checkbox"
            checked={!!node.props.checked}
            onChange={(e) => enabled && sendEvent(ws, node.id, "change", e.target.checked)}
          />
          {node.props.label}
        </label>
      );
    }
    case "Select": {
      const enabled = node.props?.events?.change;
      const options: string[] = node.props.options ?? [];
      return (
        <select
          value={node.props.value ?? ""}
          onChange={(e) => enabled && sendEvent(ws, node.id, "change", e.target.value)}
          className="select"
        >
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      );
    }
    case "Tabs": {
      const titles: string[] = node.props.titles ?? [];
      const activeIndex: number = node.props.activeIndex ?? 0;
      const changeEnabled = node.props?.events?.change;
      return (
        <div className="tabs">
          <div className="tabs__list">
            {titles.map((t, i) => (
              <button
                key={i}
                onClick={() => changeEnabled && sendEvent(ws, node.id, "change", i)}
                className={["tabs__tab", i === activeIndex && "tabs__tab--active"].filter(Boolean).join(" ")}
              >
                {t}
              </button>
            ))}
          </div>
          <div className="tabs__panel">{node.children[activeIndex] && <Node node={node.children[activeIndex]} ws={ws} />}</div>
        </div>
      );
    }
    case "DataTable": {
      const cols: string[] = node.props.columns ?? [];
      const rows: any[][] = node.props.rows ?? [];
      return (
        <div style={{ overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                {cols.map((c) => (
                  <th key={c}>
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, idx) => (
                <tr key={idx}>
                  {r.map((cell, j) => (
                    <td key={j}>{String(cell)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }
    case "Markdown": {
      const html = marked.parse(node.props.md ?? "");
      return <div dangerouslySetInnerHTML={{ __html: html }} />;
    }
    case "Chart": {
      const ref = React.useRef<HTMLDivElement | null>(null);
      React.useEffect(() => {
        if (!ref.current) return;
        const instance = echarts.init(ref.current);
        instance.setOption(node.props.options ?? {});
        const onResize = () => instance.resize();
        window.addEventListener("resize", onResize);
        return () => {
          window.removeEventListener("resize", onResize);
          instance.dispose();
        };
      }, [node.props.options]);
      return <div ref={ref} style={{ width: "100%", height: 300 }} />;
    }
    case "Card": {
      const actions: UINode[] = node.props.actions ?? [];
      const footer: UINode[] = node.props.footer ?? [];
      return (
        <div className="card">
          {(node.props.title || actions.length > 0) && (
            <div className="stack stack--h" style={{ justifyContent: "space-between", marginBottom: 8 }}>
              {node.props.title && <h3 className="card__title">{node.props.title}</h3>}
              {actions.length > 0 && (
                <div className="stack stack--h" style={{ gap: 8 }}>
                  {actions.map((a) => (
                    <Node key={a.id} node={a} ws={ws} />
                  ))}
                </div>
              )}
            </div>
          )}
          <div>
            {node.children.map((c) => (
              <Node key={c.id} node={c} ws={ws} />
            ))}
          </div>
          {footer.length > 0 && (
            <div style={{ marginTop: 10, borderTop: "1px solid var(--border)", paddingTop: 8 }}>
              <div className="stack stack--h" style={{ gap: 8, justifyContent: "flex-end" }}>
                {footer.map((f) => (
                  <Node key={f.id} node={f} ws={ws} />
                ))}
              </div>
            </div>
          )}
        </div>
      );
    }
    case "Divider":
      return <hr className="divider" />;
    case "Spacer":
      return <div className="spacer" style={{ height: node.props.height ?? 8, width: node.props.width }} />;
    case "Grid": {
      const gap = node.props.gap ?? 12;
      const cols = node.props.columns ?? { sm: 1, md: 2, lg: 3 };
      const template = `repeat(${cols.lg ?? 3}, minmax(0, 1fr))`;
      return (
        <div className="grid" style={{ gridTemplateColumns: template, gap }}>
          {node.children.map((c) => (
            <Node key={c.id} node={c} ws={ws} />
          ))}
        </div>
      );
    }
    case "Columns": {
      const gap = node.props.gap ?? 12;
      const weights: number[] | null = node.props.weights ?? null;
      const columns = node.children;
      const hasWeights = Array.isArray(weights) && weights.length === columns.length;
      return (
        <div className="stack stack--h" style={{ gap, alignItems: "stretch" }}>
          {columns.map((c, idx) => (
            <div key={c.id} style={{ flex: hasWeights ? String(weights![idx]) : "1 1 0" }}>
              <Node node={c} ws={ws} />
            </div>
          ))}
        </div>
      );
    }
    case "Columns": {
      const gap = node.props.gap ?? 12;
      const weights: number[] | null = node.props.weights ?? null;
      const columns = node.children;
      const total = weights && weights.length === columns.length ? weights.reduce((a, b) => a + b, 0) : null;
      return (
        <div className="stack stack--h" style={{ gap, alignItems: "stretch" }}>
          {columns.map((c, idx) => (
            <div key={c.id} style={{ flex: total ? String(weights![idx]) : "1 1 0" }}>
              <Node node={c} ws={ws} />
            </div>
          ))}
        </div>
      );
    }
    case "Theme": {
      const mode = node.props.mode ?? "light";
      const density = node.props.density ?? "comfortable"; // comfortable | dense
      const brand = node.props.brand ?? "blue"; // blue | teal | purple
      const glass: boolean = !!node.props.glass;
      return (
        <div className={[
          "theme",
          mode === "dark" && "theme--dark",
          density === "dense" && "theme--dense",
          brand === "teal" && "theme--brand-teal",
          brand === "purple" && "theme--brand-purple",
          glass && "theme--glass",
        ].filter(Boolean).join(" ") }>
          {node.children.map((c) => (
            <Node key={c.id} node={c} ws={ws} />
          ))}
        </div>
      );
    }
    case "AppShell": {
      const [sidebar, header, content] = node.children;
      const collapsed: boolean = !!node.props.collapsed;
      const toggleEnabled = node.props?.events?.toggle;
      return (
        <div className="shell">
          <div className="shell__sidebar">
            <div className="card" style={{ height: "100%", width: collapsed ? 72 : 260, transition: "width 200ms ease" }}>
              <div className="stack stack--h" style={{ justifyContent: "space-between", marginBottom: 8 }}>
                <div className="card__title">{collapsed ? "" : "APPUI"}</div>
                <button className="btn btn--ghost" onClick={() => toggleEnabled && sendEvent(ws, node.id, "toggle", !collapsed)}>
                  <Icon name={collapsed ? "arrow-right" : "arrow-left"} />
                </button>
              </div>
              {sidebar && <Node node={sidebar} ws={ws} />}
            </div>
          </div>
          <div className="shell__header">
            <div className="appbar container">
              <div className="stack stack--h" style={{ gap: 8 }}>
                <strong>APPUI</strong>
                <span className="muted">/ {node.props.route || "home"}</span>
              </div>
              <div className="stack stack--h" style={{ gap: 8 }}>
                <button className="btn btn--outline">Share</button>
                <button className="btn btn--primary">Run</button>
              </div>
            </div>
          </div>
          <div className="shell__content container">{content && <Node node={content} ws={ws} />}</div>
        </div>
      );
    }
    case "NavLink": {
      const active: boolean = !!node.props.active;
      return (
        <button
          className={["navlink", active && "navlink--active"].filter(Boolean).join(" ")}
          onClick={() => {
            const targetPath = String(node.props.path || "");
            // Push URL change for deep links
            if (targetPath) {
              const newPath = "/" + String(targetPath).replace(/^\//, "");
              window.history.pushState({}, "", newPath);
            }
            sendEvent(ws, node.id, "navigate", node.props.path);
          }}
        >
          {node.props.icon && <span style={{ marginRight: 8 }}>{node.props.icon}</span>}
          {node.props.text}
        </button>
      );
    }
    case "NavSection":
      return <div className="nav__section">{node.props.title}</div>;
    case "CommandPalette": {
      const items: { title: string; shortcut?: string; action?: string }[] = node.props.items ?? [];
      const runEnabled = node.props?.events?.run;
      const [query, setQuery] = React.useState("");
      const filtered = items.filter((i) => i.title.toLowerCase().includes(query.toLowerCase()));
      React.useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
          if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
            e.preventDefault();
            const el = document.getElementById("cmdk-input");
            (el as HTMLInputElement | null)?.focus();
          }
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
      }, []);
      return (
        <div className="card" style={{ position: "fixed", bottom: 24, right: 24, width: 320, boxShadow: "var(--shadow-lg)" }}>
          <input id="cmdk-input" className="input" placeholder="Search (Ctrl/⌘+K)" value={query} onChange={(e) => setQuery(e.target.value)} />
          <div className="stack stack--v" style={{ gap: 6, marginTop: 8, maxHeight: 240, overflowY: "auto" }}>
            {filtered.map((it, idx) => (
              <button key={idx} className="navlink" onClick={() => runEnabled && sendEvent(ws, node.id, "run", it)}>
                {it.title} {it.shortcut && <span style={{ marginLeft: "auto", opacity: 0.6 }}>{it.shortcut}</span>}
              </button>
            ))}
            {filtered.length === 0 && <div style={{ color: "var(--muted)", padding: 8 }}>No results</div>}
          </div>
        </div>
      );
    }
    case "KPI": {
      return (
        <div className="card">
          <div className="card__title" style={{ marginBottom: 8 }}>{node.props.title}</div>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{node.props.value}</div>
          {node.props.trend && <div style={{ color: "var(--muted)" }}>{node.props.trend}</div>}
        </div>
      );
    }
    case "Chat": {
      const [draft, setDraft] = React.useState("");
      const sendEnabled = node.props?.events?.send;
      const messages: { role: string; content: string }[] = node.props.messages ?? [];
      const onSend = () => {
        if (!draft.trim()) return;
        sendEnabled && sendEvent(ws, node.id, "send", draft);
        setDraft("");
      };
      return (
        <div className="card">
          <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 360, overflowY: "auto" }}>
            {messages.map((m, i) => (
              <div key={i} style={{ alignSelf: m.role === "user" ? "flex-end" : "flex-start", background: "var(--card-bg)", border: "1px solid var(--border)", borderRadius: 8, padding: 8, maxWidth: "75%" }}>
                <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 4 }}>{m.role}</div>
                <div>{m.content}</div>
              </div>
            ))}
          </div>
          <div className="stack stack--h" style={{ gap: 8, marginTop: 8 }}>
            <input className="input" placeholder="Type a message" value={draft} onChange={(e) => setDraft(e.target.value)} />
            <button className="btn btn--primary" onClick={onSend}>Send</button>
          </div>
        </div>
      );
    }
    case "FileUpload": {
      const multiple: boolean = !!node.props.multiple;
      const label: string = node.props.label ?? "Upload";
      const inputRef = React.useRef<HTMLInputElement | null>(null);
      const onPick = () => inputRef.current?.click();
      const onChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files || files.length === 0) return;
        for (const f of Array.from(files)) {
          const form = new FormData();
          form.append("file", f);
          await fetch("/upload", { method: "POST", body: form });
          // Notify backend about uploaded file metadata
          sendEvent(ws, node.id, "uploaded", { filename: f.name, size: f.size, type: f.type });
        }
      };
      return (
        <div>
          <input ref={inputRef} type="file" style={{ display: "none" }} multiple={multiple} onChange={onChange} />
          <button onClick={onPick} className="btn">{label}</button>
        </div>
      );
    }
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


