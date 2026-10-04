import React from "react";
import { land } from "../../studio/motion";
import { FPS, fr } from "./time";

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
}> = ({ frame, lines, start, duration, stagger = fr(3), out = 0, style }) => (
  <div style={{ display: "flex", flexDirection: "column" }}>
    {lines.map((line, i) => {
      const at = start + i * stagger;
      const p = land(frame, FPS, at, duration);
      const y = (1 - p) * 112 + out * 112;
      // Hidden outright before its move starts and once fully sent out, so no
      // sliver can show at the mask edge (motion-blur samples included).
      const shown = frame >= at && out < 1;
      return (
        <div key={line} style={{ overflow: "hidden", paddingBottom: "0.08em", marginBottom: "-0.08em" }}>
          <div style={{ ...style, transform: `translateY(${y}%)`, whiteSpace: "nowrap", visibility: shown ? "visible" : "hidden" }}>{line}</div>
        </div>
      );
    })}
  </div>
);
