import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame } from "remotion";
import { facets } from "../../brand/Logo";
import { color, inter } from "../../brand/theme";
import { cueEnd, cueLength, cueStart, durationInFrames } from "../../studio/beats";
import { land, pushIn, stagger } from "../../studio/motion";
import { AdaptiveMotionBlur, speedFromPose } from "../../studio/MotionBlur";
import { TimelineSfx } from "../../studio/Sfx";
import { timeline as tl } from "./timeline";

// Amethyst title intro (1920x1080 @ 60). Arc borrowed from the Quest intro:
// product orbits in 3D -> dive into its light -> violet whiteout -> logo slam
// with shake and burst -> settles into the centred logo (wordmark + crystal,
// nothing else) -> holds -> slides out to the right into the demo.

const { fps } = tl;
const W = 1920;
const H = 1080;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Patch photo (public/intro/patch.png, cropped from the title card).
const PATCH = { w: 862, h: 1070, ring: [383, 624] as const, ringR: 28 };

// Crystal: viewBox of the mark, its centre, and the two poses it holds.
const VB = { x: 6, y: 3, w: 53, h: 57 };
const GEM_C = [VB.x + VB.w / 2, VB.y + VB.h / 2] as const;
const GEM_HERO = { cx: W / 2, cy: H / 2, h: 380 };
// The lockup (wordmark + crystal) sits centred on the frame. Measured from a
// render: the ink spans x 98..1196, y 202..444 in the slide layout, so it
// moves right 313 and down 217 from there.
const CENTRE = { dx: 313, dy: 217 };
const GEM_FINAL = { cx: 1075 + CENTRE.dx, cy: 327 + CENTRE.dy, h: 245 };
const WORD = { x: 104 + CENTRE.dx, top: 232 + CENTRE.dy, size: 192 };
/** How far the lockup travels to clear the right edge on its way out. */
const EXIT_DX = W - WORD.x + 80;

const T = {
  patchIn: cueStart(tl, "patchIn"),
  ringGlow: cueStart(tl, "ringGlow"),
  dive: cueStart(tl, "dive"),
  slam: cueStart(tl, "slam"),
  lockup: cueStart(tl, "lockup"),
  logoOut: cueStart(tl, "logoOut"),
  logoGone: cueEnd(tl, "logoOut"),
};
const END = durationInFrames(tl);

const centroid = (points: string): [number, number] => {
  const pts = points.split(" ").map((p) => p.split(",").map(Number));
  const sx = pts.reduce((a, p) => a + p[0], 0);
  const sy = pts.reduce((a, p) => a + p[1], 0);
  return [sx / pts.length, sy / pts.length];
};

// Each facet flies in from outside along its own direction, spun a little.
const FACET_FLIGHT = facets.map((f, i) => {
  const [cx, cy] = centroid(f.points);
  const dx = cx - GEM_C[0];
  const dy = cy - GEM_C[1];
  const len = Math.hypot(dx, dy) || 1;
  return { cx, cy, ux: dx / len, uy: dy / len, spin: (i % 2 === 0 ? -1 : 1) * (28 + i * 6) };
});

// ── Act 1: patch orbits, ring glows, camera dives into the ring ──────────
const PatchShot: React.FC<{ f: number }> = ({ f }) => {
  const enter = land(f, fps, T.patchIn, cueLength(tl, "patchIn"));
  const glow = interpolate(f, [T.ringGlow, cueEnd(tl, "ringGlow")], [0, 1], { ...clamp, easing: Easing.out(Easing.quad) });
  const breathe = 0.5 + 0.5 * Math.sin((f - T.ringGlow) / 9);
  const d = interpolate(f, [T.dive, T.slam], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const dive = Math.pow(22, d);

  const orbitY = interpolate(f, [0, T.dive], [-26, 0], { ...clamp, easing: Easing.inOut(Easing.quad) });
  const orbitX = interpolate(f, [0, T.dive], [16, 0], { ...clamp, easing: Easing.out(Easing.quad) });
  const scale = interpolate(enter, [0, 1], [0.78, 1]) * interpolate(f, [T.patchIn, T.dive], [1, 1.12], clamp) * dive;
  const lift = (1 - enter) * 160;

  // Place the photo so the ring sits dead centre; everything scales around it.
  const left = W / 2 - PATCH.ring[0];
  const top = H / 2 - PATCH.ring[1];
  const ringWidth = 5 + glow * 2 + breathe * glow * 1.5;

  return (
    <AbsoluteFill style={{ perspective: 1400 }}>
      {/* Soft violet spotlight behind the patch, grows with the glow. */}
      <div
        style={{
          position: "absolute",
          left: W / 2 - 520,
          top: H / 2 - 520,
          width: 1040,
          height: 1040,
          borderRadius: "50%",
          background: `radial-gradient(circle, rgba(183,155,224,${0.08 + glow * 0.22}) 0%, transparent 65%)`,
          transform: `scale(${0.8 + glow * 0.4})`,
        }}
      />
      <div
        style={{
          position: "absolute",
          left,
          top,
          width: PATCH.w,
          height: PATCH.h,
          transformOrigin: `${PATCH.ring[0]}px ${PATCH.ring[1]}px`,
          transform: `translateY(${lift}px) rotateY(${orbitY}deg) rotateX(${orbitX}deg) scale(${scale})`,
          transformStyle: "preserve-3d",
        }}
      >
        <Img
          src={staticFile("intro/patch.png")}
          style={{
            width: PATCH.w,
            height: PATCH.h,
            maskImage: "radial-gradient(ellipse 50% 45% at 44% 58%, #000 45%, transparent 100%)",
            WebkitMaskImage: "radial-gradient(ellipse 50% 45% at 44% 58%, #000 45%, transparent 100%)",
          }}
        />
        {/* The pod's light ring, re-drawn on top so it can glow. */}
        <svg
          width={PATCH.w}
          height={PATCH.h}
          style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}
        >
          <defs>
            <radialGradient id="ringHalo">
              <stop offset="0%" stopColor={color.brandGlow} stopOpacity={0.9} />
              <stop offset="100%" stopColor={color.brandGlow} stopOpacity={0} />
            </radialGradient>
          </defs>
          <circle
            cx={PATCH.ring[0]}
            cy={PATCH.ring[1]}
            r={PATCH.ringR * (2.2 + breathe * 0.4)}
            fill="url(#ringHalo)"
            opacity={glow * 0.55}
          />
          <circle
            cx={PATCH.ring[0]}
            cy={PATCH.ring[1]}
            r={PATCH.ringR - 4}
            fill="none"
            stroke={color.brand}
            strokeWidth={ringWidth}
            opacity={glow}
          />
          {/* Ring fills with light as the camera dives in. */}
          <circle cx={PATCH.ring[0]} cy={PATCH.ring[1]} r={PATCH.ringR - 4} fill={color.brandGlow} opacity={d * 0.9} />
        </svg>
      </div>
    </AbsoluteFill>
  );
};

// ── Act 2+3: crystal slams together, then moves into the lockup ──────────
const Gem: React.FC<{ f: number }> = ({ f }) => {
  const s = f - T.slam;
  const L = land(f, fps, T.lockup, cueLength(tl, "lockup"));
  const cx = interpolate(L, [0, 1], [GEM_HERO.cx, GEM_FINAL.cx]);
  const cy = interpolate(L, [0, 1], [GEM_HERO.cy, GEM_FINAL.cy]);
  const h = interpolate(L, [0, 1], [GEM_HERO.h, GEM_FINAL.h]);
  const w = (h * VB.w) / VB.h;
  const unit = h / VB.h; // px per viewBox unit

  // Shake once the last facet lands.
  const shakeX = interpolate(s, [9, 11, 13, 15, 17], [0, -8, 7, -3, 0], clamp);
  const shakeY = interpolate(s, [9, 11, 13, 15, 17], [0, 4, -4, 2, 0], clamp);
  // Gentle orbit while it holds centre stage; flattens as it lands in the lockup.
  const tiltY = interpolate(f, [T.slam + 10, T.lockup], [-10, 8], clamp) * (1 - L);
  const tiltX = Math.sin(f / 22) * 4 * (1 - L);
  const hold = interpolate(f, [T.slam + 14, T.lockup], [1, 1.05], { ...clamp, easing: Easing.inOut(Easing.quad) });
  const scale = interpolate(L, [0, 1], [hold, 1]);

  return (
    <div
      style={{
        position: "absolute",
        left: cx - w / 2,
        top: cy - h / 2,
        width: w,
        height: h,
        transform: `translate(${shakeX}px, ${shakeY}px) perspective(900px) rotateY(${tiltY}deg) rotateX(${tiltX}deg) scale(${scale})`,
      }}
    >
      <svg width={w} height={h} viewBox={`${VB.x} ${VB.y} ${VB.w} ${VB.h}`} style={{ overflow: "visible" }}>
        {facets.map((facet, i) => {
          const fl = FACET_FLIGHT[i];
          const t = spring({ frame: s - i * 2, fps, config: { damping: 11, stiffness: 170, mass: 0.7 } });
          const dist = (520 / unit) * (1 - t);
          const tx = fl.ux * dist;
          const ty = fl.uy * dist;
          const rot = fl.spin * (1 - t);
          const sc = interpolate(t, [0, 1], [0.35, 1]);
          return (
            <polygon
              key={facet.id}
              points={facet.points}
              fill={facet.fill}
              opacity={interpolate(s - i * 2, [0, 3], [0, 1], clamp)}
              transform={`translate(${tx} ${ty}) rotate(${rot} ${fl.cx} ${fl.cy}) translate(${fl.cx} ${fl.cy}) scale(${sc}) translate(${-fl.cx} ${-fl.cy})`}
              stroke={facet.fill}
              strokeWidth={0.35}
              strokeLinejoin="round"
            />
          );
        })}
      </svg>
    </div>
  );
};

// Burst rays and a ring shockwave (the pod ring, echoed) on the slam.
const Burst: React.FC<{ f: number }> = ({ f }) => {
  const s = f - T.slam;
  if (s < 0 || s > 40) return null;
  const rayOp = interpolate(s, [6, 10, 30], [0, 0.75, 0], clamp);
  const rayScale = interpolate(s, [6, 30], [0.4, 2.1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const waveR = interpolate(s, [8, 38], [120, 760], { ...clamp, easing: Easing.out(Easing.cubic) });
  const waveOp = interpolate(s, [8, 12, 38], [0, 0.6, 0], clamp);
  return (
    <AbsoluteFill>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <circle cx={W / 2} cy={H / 2} r={waveR} fill="none" stroke={color.brandLight} strokeWidth={6} opacity={waveOp} />
        <g transform={`translate(${W / 2} ${H / 2}) scale(${rayScale})`} opacity={rayOp}>
          {Array.from({ length: 16 }, (_, i) => (
            <rect
              key={i}
              x={-1.5}
              y={-300}
              width={3}
              height={80}
              rx={1.5}
              fill={i % 2 === 0 ? color.brand : color.brandGlow}
              transform={`rotate(${i * 22.5})`}
            />
          ))}
        </g>
      </svg>
    </AbsoluteFill>
  );
};

// Letters rise out of a clip line, one every few frames.
const RiseLetters: React.FC<{ f: number; text: string; start: number; style: React.CSSProperties }> = ({ f, text, start, style }) => (
  <div style={{ display: "flex", overflow: "hidden", paddingBottom: "0.3em", marginBottom: "-0.3em", ...style }}>
    {text.split("").map((ch, i) => {
      const t = land(f, fps, stagger(start, i, 3), 30);
      return (
        <span key={i} style={{ display: "inline-block", transform: `translateY(${(1 - t) * 150}%)`, whiteSpace: "pre" }}>
          {ch}
        </span>
      );
    })}
  </div>
);

const Wordmark: React.FC<{ f: number }> = ({ f }) => (
  <RiseLetters
    f={f}
    text="amethyst"
    start={T.lockup + 6}
    style={{
      position: "absolute",
      left: WORD.x,
      top: WORD.top,
      fontFamily: inter,
      fontWeight: 600,
      fontSize: WORD.size,
      lineHeight: 1,
      letterSpacing: "-0.02em",
      color: color.ink,
    }}
  />
);

/** Lockup exit: starts slow, leaves fast (it is gone when the demo cuts in). */
const exitX = (f: number) =>
  interpolate(f, [T.logoOut, T.logoGone], [0, EXIT_DX], { ...clamp, easing: Easing.bezier(0.5, 0, 0.9, 0.4) });

export const AmethystIntro: React.FC = () => {
  const f = useCurrentFrame();

  // Violet light floods in during the dive, then clears to white on the slam.
  const violet =
    f < T.slam
      ? interpolate(f, [T.dive + 12, T.slam], [0, 1], { ...clamp, easing: Easing.in(Easing.quad) })
      : interpolate(f, [T.slam, T.slam + 16], [1, 0], { ...clamp, easing: Easing.out(Easing.quad) });
  const flash = interpolate(f, [T.slam - 3, T.slam, T.slam + 10], [0, 0.9, 0], clamp);
  const camera = f >= T.lockup ? pushIn(f - T.lockup, T.logoOut - T.lockup, 0.025) : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: color.surface, overflow: "hidden" }}>
      {f < T.slam + 2 ? <PatchShot f={f} /> : null}
      <AdaptiveMotionBlur name="Logo out" speed={speedFromPose((t) => [[exitX(t), 0]])}>
        <AbsoluteFill style={{ transform: `translateX(${exitX(f)}px) scale(${camera})`, transformOrigin: "50% 50%" }}>
          {f >= T.slam - 2 ? <Wordmark f={f} /> : null}
          {f >= T.slam - 2 ? <Gem f={f} /> : null}
        </AbsoluteFill>
      </AdaptiveMotionBlur>
      <Burst f={f} />
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% 50%, ${color.brandGlow} 0%, ${color.brandLight} 55%, ${color.brand} 100%)`,
          opacity: violet,
        }}
      />
      <AbsoluteFill style={{ backgroundColor: "#FFFFFF", opacity: flash }} />
      <TimelineSfx timeline={tl} />
    </AbsoluteFill>
  );
};

export const amethystIntroComposition = {
  id: tl.id,
  component: AmethystIntro,
  durationInFrames: END,
  fps,
  width: W,
  height: H,
} as const;
