import React from "react";
import { color } from "../../brand/theme";
import { facets } from "../../brand/Logo";
import { CANVAS } from "./canvas";

// The physical world of the film: a black-and-white cartoon arm (as directed)
// and the Amethyst patch in flat brand colors. World units = canvas px at the
// wide shot. One SVG, so the macro camera stays vector-sharp.

export type Pt = readonly [number, number];

export type Camera = {
  /** World point placed at `at` on the canvas. */
  readonly focus: Pt;
  readonly at: Pt;
  readonly scale: number;
  /** Degrees. */
  readonly roll: number;
};

export const worldToCanvas = (cam: Camera, p: Pt): [number, number] => {
  const dx = (p[0] - cam.focus[0]) * cam.scale;
  const dy = (p[1] - cam.focus[1]) * cam.scale;
  const a = (cam.roll * Math.PI) / 180;
  return [
    cam.at[0] + dx * Math.cos(a) - dy * Math.sin(a),
    cam.at[1] + dx * Math.sin(a) + dy * Math.cos(a),
  ];
};

// ── Arm ──────────────────────────────────────────────────────────────────
// Local space: wrist at (0,0), forearm runs to +x, hand points to -x,
// seen from above (back of the hand), thumb on top.
export const ARM = {
  wrist: [300, 1000] as Pt,
  angle: 10, // degrees; elbow exits lower right
  /** Where the patch sits on the forearm, in arm-local space. */
  patchLocal: [330, -6] as Pt,
};

export const armLocalToWorld = (p: Pt, offset: Pt = [0, 0]): [number, number] => {
  const a = (ARM.angle * Math.PI) / 180;
  return [
    ARM.wrist[0] + offset[0] + p[0] * Math.cos(a) - p[1] * Math.sin(a),
    ARM.wrist[1] + offset[1] + p[0] * Math.sin(a) + p[1] * Math.cos(a),
  ];
};

const INK = color.ink;
const LINE = 8;

// Proportions follow a real hand: fingers about as long as the palm, tapering
// to the tip, two joint creases each, nails, a slight natural fan.
const forearm =
  "M 0,-104 C 300,-112 800,-142 1700,-164 L 1700,168 C 800,150 300,116 0,104 Z";
const palm =
  "M 10,-104 C -30,-110 -70,-118 -110,-114 C -150,-110 -185,-110 -204,-104 C -236,-84 -246,-40 -248,0 C -246,40 -236,76 -206,98 C -170,110 -110,118 -60,112 C -30,108 -8,105 10,104 Z";

type FingerSpec = { cy: number; len: number; wb: number; wt: number; rot: number };
const fingers: FingerSpec[] = [
  { cy: -78, len: 214, wb: 46, wt: 37, rot: 5.5 }, // index
  { cy: -26, len: 240, wb: 48, wt: 39, rot: 1.5 }, // middle
  { cy: 25, len: 224, wb: 45, wt: 36, rot: -2.5 }, // ring
  { cy: 73, len: 172, wb: 38, wt: 31, rot: -8 }, // little
];
const KNUCKLE_X = -200;

/** Tapered finger pointing to -x from (0,0): base width wb, tip width wt. */
const fingerPath = (len: number, wb: number, wt: number) => {
  const r = wt / 2;
  const tipX = -len + r;
  return `M 24,${-wb / 2} L ${tipX},${-r} A ${r},${r} 0 0 0 ${tipX},${r} L 24,${wb / 2} Z`;
};

const Finger: React.FC<{ f: FingerSpec }> = ({ f }) => {
  const crease = (at: number, w: number) => {
    const x = -f.len * at;
    const h = w * 0.24;
    return `M ${x + 3},${-h} q -6,${h} 0,${h * 2}`;
  };
  const wAt = (t: number) => f.wb + (f.wt - f.wb) * t;
  const nailLen = f.len * 0.16;
  const nailW = f.wt * 0.6;
  const nailX = -f.len + 9;
  return (
    <g transform={`translate(${KNUCKLE_X} ${f.cy}) rotate(${f.rot})`}>
      <path d={fingerPath(f.len, f.wb, f.wt)} fill="#FFFFFF" stroke={INK} strokeWidth={LINE} strokeLinejoin="round" />
      <path d={crease(0.36, wAt(0.36))} fill="none" stroke={INK} strokeWidth={LINE * 0.42} strokeLinecap="round" />
      <path d={crease(0.66, wAt(0.66))} fill="none" stroke={INK} strokeWidth={LINE * 0.42} strokeLinecap="round" />
      <rect
        x={nailX}
        y={-nailW / 2}
        width={nailLen}
        height={nailW}
        rx={nailW / 2}
        fill="none"
        stroke={INK}
        strokeWidth={LINE * 0.42}
      />
    </g>
  );
};

// Thumb: on the top edge, angled out and forward (rot is clockwise from -x).
const THUMB = { x: -86, y: -88, len: 150, wb: 54, wt: 39, rot: 21 };
const thumbPath = fingerPath(THUMB.len, THUMB.wb, THUMB.wt);
const Thumb: React.FC<{ fill?: boolean; stroke?: number }> = ({ fill, stroke }) => (
  <path
    d={thumbPath}
    transform={`translate(${THUMB.x} ${THUMB.y}) rotate(${THUMB.rot})`}
    fill={fill ? "#FFFFFF" : "none"}
    stroke={stroke ? INK : "none"}
    strokeWidth={stroke ?? 0}
    strokeLinejoin="round"
  />
);

// Cartoon hatching along the underside of the forearm.
const hatches = Array.from({ length: 28 }, (_, i) => {
  const x = 110 + i * 56;
  const yEdge = 104 + (x / 1700) * 64;
  return `M ${x},${yEdge - 10} l 20,-30`;
}).join(" ");

export const Arm: React.FC<{ offset: Pt }> = ({ offset }) => (
  <g
    transform={`translate(${ARM.wrist[0] + offset[0]} ${ARM.wrist[1] + offset[1]}) rotate(${ARM.angle})`}
  >
    {/* Outline pass (double width) so forearm + palm + thumb read as one
        silhouette with a single outer line. */}
    <path d={forearm} fill="none" stroke={INK} strokeWidth={LINE * 2} strokeLinejoin="round" />
    <path d={palm} fill="none" stroke={INK} strokeWidth={LINE * 2} strokeLinejoin="round" />
    <Thumb stroke={LINE * 2} />
    {fingers.map((f) => (
      <Finger key={f.cy} f={f} />
    ))}
    {/* Fill pass */}
    <Thumb fill />
    <path d={forearm} fill="#FFFFFF" />
    <path d={palm} fill="#FFFFFF" />
    {/* Thumb joint crease and nail */}
    <g transform={`translate(${THUMB.x} ${THUMB.y}) rotate(${THUMB.rot})`}>
      <path d={`M ${-THUMB.len * 0.55 + 3},-10 q -6,10 0,20`} fill="none" stroke={INK} strokeWidth={LINE * 0.42} strokeLinecap="round" />
      <rect x={-THUMB.len + 9} y={-THUMB.wt * 0.3} width={THUMB.len * 0.15} height={THUMB.wt * 0.6} rx={THUMB.wt * 0.3} fill="none" stroke={INK} strokeWidth={LINE * 0.42} />
    </g>
    {/* Knuckles, tendons, wrist bone */}
    {fingers.map((f) => (
      <path
        key={`k${f.cy}`}
        d={`M ${KNUCKLE_X + 16},${f.cy - f.wb * 0.22} q -8,${f.wb * 0.22} 0,${f.wb * 0.44}`}
        fill="none"
        stroke={INK}
        strokeWidth={LINE * 0.42}
        strokeLinecap="round"
      />
    ))}
    {fingers.slice(0, 3).map((f) => (
      <path
        key={`t${f.cy}`}
        d={`M ${KNUCKLE_X + 50},${f.cy * 0.92} L ${KNUCKLE_X + 120},${f.cy * 0.6}`}
        fill="none"
        stroke={INK}
        strokeWidth={LINE * 0.3}
        strokeLinecap="round"
        opacity={0.55}
      />
    ))}
    <path d="M 26,78 q 14,10 30,6" fill="none" stroke={INK} strokeWidth={LINE * 0.5} strokeLinecap="round" />
    <path d={hatches} fill="none" stroke={INK} strokeWidth={LINE * 0.55} strokeLinecap="round" />
  </g>
);

// ── Patch ────────────────────────────────────────────────────────────────

export const PAD = { w: 300, h: 186, r: 46 };
export const POD = { r: 54, ring: 70 };

export type PatchState = {
  readonly pos: Pt;
  readonly rot: number;
  readonly scale: number;
  /** Contact compression 0..1. */
  readonly squash: number;
  /** Pod light ring lit, 0..1 (draws around the pod). */
  readonly ring: number;
  /** Scan line position across the pad, -1..1; null = no scan. */
  readonly scanX: number | null;
  /** Horizontal line position top→bottom, -1..1; null = none. */
  readonly scanY: number | null;
  /** Violet illumination beneath the surface, 0..1. */
  readonly glow: number;
};

const Mark: React.FC<{ size: number }> = ({ size }) => (
  // Official crystal (src/brand/Logo.tsx facets), centered on 0,0.
  <g transform={`scale(${size / 53}) translate(-32.5 -31.5)`}>
    {facets.map((f) => (
      <polygon key={f.id} points={f.points} fill={f.fill} strokeLinejoin="round" />
    ))}
  </g>
);

export const Patch: React.FC<{ s: PatchState; id: string }> = ({ s, id }) => {
  const sx = 1 + 0.06 * s.squash;
  const sy = 1 - 0.1 * s.squash;
  const ringLen = 2 * Math.PI * POD.ring;
  return (
    <g
      transform={`translate(${s.pos[0]} ${s.pos[1]}) rotate(${s.rot}) scale(${s.scale * sx} ${s.scale * sy})`}
    >
      <defs>
        <clipPath id={`pad-${id}`}>
          <rect x={-PAD.w / 2} y={-PAD.h / 2} width={PAD.w} height={PAD.h} rx={PAD.r} />
        </clipPath>
      </defs>
      <rect
        x={-PAD.w / 2}
        y={-PAD.h / 2}
        width={PAD.w}
        height={PAD.h}
        rx={PAD.r}
        fill={color.surfaceTint}
      />
      <g clipPath={`url(#pad-${id})`}>
        {/* Illumination beneath the surface: flat violet, no bloom. */}
        {s.glow > 0 ? (
          <rect
            x={-PAD.w / 2}
            y={-PAD.h / 2}
            width={PAD.w}
            height={PAD.h}
            fill={color.brand}
            opacity={0.34 * s.glow}
          />
        ) : null}
        {s.scanX !== null ? (
          <>
            <rect
              x={(s.scanX * (PAD.w / 2 + 40)) - 70}
              y={-PAD.h / 2}
              width={70}
              height={PAD.h}
              fill={color.brand}
              opacity={0.12}
            />
            <rect
              x={(s.scanX * (PAD.w / 2 + 40)) - 2.5}
              y={-PAD.h / 2}
              width={5}
              height={PAD.h}
              fill={color.brand}
            />
          </>
        ) : null}
        {s.scanY !== null ? (
          <rect
            x={-PAD.w / 2}
            y={s.scanY * (PAD.h / 2) - 2.5}
            width={PAD.w}
            height={5}
            fill={color.brand}
          />
        ) : null}
      </g>
      <rect
        x={-PAD.w / 2}
        y={-PAD.h / 2}
        width={PAD.w}
        height={PAD.h}
        rx={PAD.r}
        fill="none"
        stroke={INK}
        strokeWidth={6}
      />
      {/* Pod: snaps onto the pad; its light ring is the activation cue. */}
      <circle r={POD.ring} fill="none" stroke={color.line} strokeWidth={8} />
      <circle
        r={POD.ring}
        fill="none"
        stroke={color.brand}
        strokeWidth={8}
        strokeLinecap="round"
        strokeDasharray={`${ringLen * s.ring} ${ringLen}`}
        transform="rotate(-90)"
        opacity={s.ring > 0 ? 1 : 0}
      />
      <circle r={POD.r} fill="#FFFFFF" stroke={INK} strokeWidth={6} />
      <Mark size={60} />
    </g>
  );
};

export const PatchShadow: React.FC<{ pos: Pt; rot: number; spread: number; strength: number }> = ({
  pos,
  rot,
  spread,
  strength,
}) => (
  <ellipse
    cx={pos[0]}
    cy={pos[1]}
    rx={(PAD.w / 2 + 6) * spread}
    ry={(PAD.h / 2 + 6) * spread}
    transform={`rotate(${rot} ${pos[0]} ${pos[1]})`}
    fill={INK}
    opacity={strength}
  />
);

export const Stage: React.FC<{
  cam: Camera;
  armOffset: Pt;
  patch: PatchState;
  shadow?: { pos: Pt; spread: number; strength: number };
  background?: string;
  id: string;
}> = ({ cam, armOffset, patch, shadow, background = color.surfaceRaised, id }) => (
  <svg width={CANVAS.w} height={CANVAS.h} viewBox={`0 0 ${CANVAS.w} ${CANVAS.h}`} style={{ position: "absolute", inset: 0 }}>
    <rect width={CANVAS.w} height={CANVAS.h} fill={background} />
    <g
      transform={`translate(${cam.at[0]} ${cam.at[1]}) rotate(${cam.roll}) scale(${cam.scale}) translate(${-cam.focus[0]} ${-cam.focus[1]})`}
    >
      <Arm offset={armOffset} />
      {shadow ? (
        <PatchShadow pos={shadow.pos} rot={patch.rot} spread={shadow.spread} strength={shadow.strength} />
      ) : null}
      <Patch s={patch} id={id} />
    </g>
  </svg>
);
