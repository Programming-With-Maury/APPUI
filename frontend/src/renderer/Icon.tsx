import React from "react";

type IconName = "home" | "chart" | "widgets" | "chat" | "settings" | "arrow-left" | "arrow-right";

const paths: Record<IconName, JSX.Element> = {
  home: (<path d="M3 10.5 12 3l9 7.5V21a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1v-10.5Z"/>),
  chart: (<path d="M4 20h16M7 16v-6m5 6V8m5 12V4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>),
  widgets: (<path d="M4 4h8v8H4V4Zm8 8h8v8h-8v-8ZM4 14h8v8H4v-8Zm8-10h8v8h-8V4Z"/>),
  chat: (<path d="M4 6h16v10H7l-3 3V6Z"/>),
  settings: (<path d="M12 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8Zm8-1-2 1 1 2-1 2 2 1-2 4-2-1-2 1-2-1-2 1-2-4 2-1-1-2 1-2-2-1 2-4 2 1 2-1 2 1 2-1 2 4Z"/>),
  "arrow-left": (<path d="M14 6l-6 6 6 6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>),
  "arrow-right": (<path d="M10 6l6 6-6 6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>),
};

export function Icon({ name, size=16 }: { name: IconName; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" aria-hidden>
      {paths[name]}
    </svg>
  );
}


