import React from "react";
import { AbsoluteFill, Img } from "remotion";
import { color } from "../../brand/theme";
import { CANVAS } from "./canvas";
import { SCREEN } from "./screens";
import { mix, mixPt } from "./time";

// A plain phone frame around a real screenshot. The view says how many canvas
// px one screen css px is (k), and which screen point sits where on canvas.
// Screenshots keep their exact 390:844 proportion; k never exceeds the
// capture density (4), so they stay sharp.

export type View = {
  readonly k: number;
  readonly focus: readonly [number, number];
  readonly at: readonly [number, number];
};

export const mixView = (a: View, b: View, t: number): View => ({
  k: a.k * Math.pow(b.k / a.k, t),
  focus: mixPt(a.focus, b.focus, t),
  at: mixPt(a.at, b.at, t),
});

export const toCanvas = (v: View, p: readonly [number, number]): [number, number] => [
  v.at[0] + (p[0] - v.focus[0]) * v.k,
  v.at[1] + (p[1] - v.focus[1]) * v.k,
];

const BEZEL = 11;
const SCREEN_RADIUS = 44;

export const Device: React.FC<{
  view: View;
  /** Layers inside the screen. Given k so they can size themselves in
   *  real pixels (no CSS scale: images rasterize at full resolution). */
  children: (k: number) => React.ReactNode;
}> = ({ view, children }) => {
  const [x, y] = toCanvas(view, [0, 0]);
  const k = view.k;
  return (
    <div
      style={{
        position: "absolute",
        left: x - BEZEL * k,
        top: y - BEZEL * k,
        width: (SCREEN.w + BEZEL * 2) * k,
        height: (SCREEN.h + BEZEL * 2) * k,
        borderRadius: (SCREEN_RADIUS + BEZEL) * k,
        backgroundColor: color.ink,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: BEZEL * k,
          top: BEZEL * k,
          width: SCREEN.w * k,
          height: SCREEN.h * k,
          borderRadius: SCREEN_RADIUS * k,
          overflow: "hidden",
          backgroundColor: color.surface,
        }}
      >
        {children(k)}
      </div>
    </div>
  );
};

/** A full-screen screenshot layer, optionally clipped (clip in css px). */
export const Shot: React.FC<{
  src: string;
  k: number;
  clip?: { x: number; y: number; w: number; h: number; r: number };
}> = ({ src, k, clip }) => (
  <AbsoluteFill
    style={{
      clipPath: clip
        ? `inset(${clip.y * k}px ${(SCREEN.w - clip.x - clip.w) * k}px ${(SCREEN.h - clip.y - clip.h) * k}px ${clip.x * k}px round ${clip.r * k}px)`
        : undefined,
    }}
  >
    <Img src={src} style={{ width: SCREEN.w * k, height: SCREEN.h * k, display: "block" }} />
  </AbsoluteFill>
);

/** Vector overlay in screen css coordinates (390x844), scaled crisply. */
export const ScreenOverlay: React.FC<{ k: number; children: React.ReactNode }> = ({ k, children }) => (
  <svg
    width={SCREEN.w * k}
    height={SCREEN.h * k}
    viewBox={`0 0 ${SCREEN.w} ${SCREEN.h}`}
    style={{ position: "absolute", left: 0, top: 0 }}
  >
    {children}
  </svg>
);

/** Flat panel behind the device that drifts slower than it (parallax). */
export const ParallaxPanel: React.FC<{ view: View; depth?: number }> = ({ view, depth = 0.35 }) => {
  const [cx, cy] = toCanvas(view, [195, 422]);
  const k = mix(1, view.k / 1.1, depth);
  const w = 1380 * k;
  const h = 880 * k;
  const px = CANVAS.w / 2 + (cx - CANVAS.w / 2) * depth;
  const py = CANVAS.h / 2 + 20 + (cy - CANVAS.h / 2) * depth;
  return (
    <div
      style={{
        position: "absolute",
        left: px - w / 2,
        top: py - h / 2,
        width: w,
        height: h,
        borderRadius: 64 * k,
        backgroundColor: color.surfaceRaised,
      }}
    />
  );
};
