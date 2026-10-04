import React from "react";
import { color, inter, mono } from "../../brand/theme";
import { land } from "../../studio/motion";
import { RiseText } from "./RiseText";
import { FPS, fr } from "./time";

// Type system for the explainer (one family, Inter; JetBrains Mono only for
// readings and tool names, as the brand guide specifies).
export const text = {
  eyebrow: { fontFamily: inter, fontWeight: 600, fontSize: 24, letterSpacing: "0.1em", textTransform: "uppercase", color: color.brand },
  headline: { fontFamily: inter, fontWeight: 600, fontSize: 46, lineHeight: 1.12, letterSpacing: "-0.025em", color: color.ink },
  body: { fontFamily: inter, fontWeight: 500, fontSize: 30, lineHeight: 1.3, letterSpacing: "-0.01em", color: color.inkMuted },
  label: { fontFamily: inter, fontWeight: 500, fontSize: 24, color: color.inkMuted },
  value: { fontFamily: mono, fontWeight: 500, fontSize: 27, color: color.ink },
  code: { fontFamily: mono, fontWeight: 500, fontSize: 25, color: color.ink },
} satisfies Record<string, React.CSSProperties>;

export const MARGIN = 120;
export const HEADER_TOP = 92;

/** "01 · Sense" + one or two headline lines, top-left. */
export const StepHeader: React.FC<{
  frame: number;
  step: string;
  name: string;
  lines: readonly string[];
  start: number;
  duration: number;
  out?: number;
  width?: number;
}> = ({ frame, step, name, lines, start, duration, out = 0, width = 900 }) => (
  <div style={{ position: "absolute", left: MARGIN, top: HEADER_TOP, width }}>
    <RiseText frame={frame} lines={[`${step} · ${name}`]} start={start} duration={duration} out={out} style={text.eyebrow} />
    <div style={{ height: 14 }} />
    <RiseText frame={frame} lines={lines} start={start + fr(3)} duration={duration} stagger={fr(3)} out={out} style={text.headline} />
  </div>
);

const ROW_H = 62;
/** Height of a card rolled up to its title and first row. */
export const COMPACT_H = 86 + ROW_H + 12;

/** A flat card with rows that rise in one after another. */
export const RowsCard: React.FC<{
  frame: number;
  title: string;
  rows: readonly { label: string; value: string; at?: number }[];
  start: number;
  stagger?: number;
  x: number;
  y: number;
  w: number;
  /** Reveal of the card body itself (0..1): grows from the top. */
  open: number;
  footer?: { lines: readonly string[]; at: number };
  accentRow?: number;
  /** 0..1: rolls the card up to its first row (used before a handoff). */
  collapse?: number;
}> = ({ frame, title, rows, start, stagger = fr(4), x, y, w, open, footer, accentRow, collapse = 0 }) => {
  const rowH = ROW_H;
  const full = 86 + rows.length * rowH + (footer ? 40 + footer.lines.length * 28 : 12);
  const h = full + (COMPACT_H - full) * collapse;
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w,
        height: h,
        borderRadius: 24,
        backgroundColor: color.surfaceRaised,
        clipPath: `inset(0 0 ${(1 - open) * 100}% 0 round 24px)`,
        overflow: "hidden",
        padding: "26px 32px",
        boxSizing: "border-box",
      }}
    >
      <RiseText frame={frame} lines={[title]} start={start} duration={fr(30)} style={{ ...text.label, color: color.ink, fontWeight: 600 }} />
      <div style={{ height: 14 }} />
      {rows.map((row, i) => {
        const at = row.at ?? start + fr(6) + i * stagger;
        const p = land(frame, FPS, at, fr(30));
        // Rise a full row height so no part of the text peeks above the row
        // line before its move starts (a % of the text's own height did).
        const rise = { transform: `translateY(${(1 - p) * rowH}px)`, display: "inline-block", visibility: frame < at ? "hidden" : "visible" } as const;
        return (
          <div
            key={row.label}
            style={{
              height: rowH,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              borderTop: `1px solid ${color.line}`,
              overflow: "hidden",
            }}
          >
            <span style={{ ...text.label, ...rise }}>{row.label}</span>
            <span style={{ ...text.value, color: i === accentRow ? color.brand : color.ink, ...rise }}>{row.value}</span>
          </div>
        );
      })}
      {footer ? (
        <div style={{ marginTop: 18 }}>
          <RiseText frame={frame} lines={footer.lines} start={footer.at} duration={fr(30)} style={{ ...text.label, fontSize: 20, lineHeight: "28px" }} />
        </div>
      ) : null}
    </div>
  );
};

/** Left-column captions that hand over to each other with the focus. */
export const Captions: React.FC<{
  frame: number;
  items: readonly { start: number; end?: number; lines: readonly string[] }[];
  top?: number;
}> = ({ frame, items, top = 440 }) => (
  <div style={{ position: "absolute", left: MARGIN, top, width: 980 }}>
    {items.map((it) => (
      <div key={it.lines.join("|")} style={{ position: "absolute", left: 0, top: 0 }}>
        <RiseText
          frame={frame}
          lines={it.lines}
          start={it.start}
          duration={fr(36)}
          stagger={fr(3)}
          out={it.end === undefined ? 0 : land(frame, FPS, it.end, fr(24))}
          style={{ ...text.body, fontSize: 38, color: color.ink }}
        />
      </div>
    ))}
  </div>
);
