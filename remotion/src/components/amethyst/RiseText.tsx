import React from "react";
import { land } from "../../studio/motion";
import { FPS } from "./time";

/** Lines rise out of their own masks, staggered. `out` (0..1) sends them
 *  back down. No opacity fades. */
export const RiseText: React.FC<{
  frame: number;
  lines: readonly string[];
  start: number;
  /** Frames per line move (>= 18 = 0.3s). */
  duration: number;
  stagger?: number;
  out?: number;
  style: React.CSSProperties;
}> = ({ frame, lines, start, duration, stagger = 3, out = 0, style }) => (
  <div style={{ display: "flex", flexDirection: "column" }}>
    {lines.map((line, i) => {
      const p = land(frame, FPS, start + i * stagger, duration);
      const y = (1 - p) * 112 + out * 112;
      return (
        <div key={line} style={{ overflow: "hidden", paddingBottom: "0.08em", marginBottom: "-0.08em" }}>
          <div style={{ ...style, transform: `translateY(${y}%)`, whiteSpace: "nowrap" }}>{line}</div>
        </div>
      );
    })}
  </div>
);
