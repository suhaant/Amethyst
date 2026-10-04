import { Easing, interpolate } from "remotion";
import { land } from "../../studio/motion";
import {
  ARM,
  armLocalToWorld,
  type Camera,
  type PatchState,
  type Pt,
  worldToCanvas,
} from "./Stage";
import { CANVAS } from "./canvas";
import { easeInOut, END, FPS, fr, mix, mixPt, move, T } from "./time";

// Pure pose of the physical world (arm, patch, camera) for any frame.

export const PATCH_REST = armLocalToWorld(ARM.patchLocal);
const REST_ROT = ARM.angle;

/** Where the macro camera parks the pod on the canvas. Device shots that
 *  match-cut to/from the patch use the same point. */
export const MACRO_AT: Pt = [560, 610];
export const MACRO_SCALE = 2.0;
/** Where the patch waits below the frame (handoff out, treatment back in). The
 *  leveled forearm spans the full width, so it exits down, not sideways. */
const OFF_BELOW: Pt = [560, 1720];

const smooth = (f: number, a: number, b: number) =>
  interpolate(f, [a, b], [0, 1], {
    easing: Easing.bezier(0.45, 0, 0.55, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const mixCam = (a: Camera, b: Camera, t: number): Camera => ({
  focus: mixPt(a.focus, b.focus, t),
  at: mixPt(a.at, b.at, t),
  scale: a.scale * Math.pow(b.scale / a.scale, t),
  roll: mix(a.roll, b.roll, t),
});

const quad = (a: Pt, c: Pt, b: Pt, u: number): [number, number] => [
  (1 - u) * (1 - u) * a[0] + 2 * (1 - u) * u * c[0] + u * u * b[0],
  (1 - u) * (1 - u) * a[1] + 2 * (1 - u) * u * c[1] + u * u * b[1],
];

export const macroCam = (scale = MACRO_SCALE): Camera => ({
  focus: PATCH_REST,
  at: MACRO_AT,
  scale,
  roll: -REST_ROT,
});

export const heroCam: Camera = {
  focus: PATCH_REST,
  at: [1060, 800],
  scale: 1,
  roll: -REST_ROT,
};

export const camera = (f: number): Camera => {
  if (f < T.cut("scene3")) {
    // Wide, with a slow push, then the macro move that levels the patch.
    const wide: Camera = {
      focus: [640, 1030],
      at: [CANVAS.w / 2, CANVAS.h / 2],
      scale: 1.1 * (1 + 0.03 * smooth(f, 0, T.start("macro"))),
      roll: 0,
    };
    const macro = macroCam(MACRO_SCALE * (1 + 0.04 * smooth(f, T.end("macro"), T.start("patchOut"))));
    const cam = mixCam(wide, macro, move(f, "macro"));
    // The patch drops out of frame before the reading card moves on.
    return { ...cam, at: mixPt(cam.at, OFF_BELOW, move(f, "patchOut")) };
  }
  // Treatment: the patch rises back in as the ring lands on it.
  const treat = macroCam(MACRO_SCALE * (1 + 0.04 * smooth(f, T.start("ringToPatch"), T.cut("scene6"))));
  const back = { ...treat, at: mixPt(OFF_BELOW, MACRO_AT, move(f, "ringToPatch")) };
  if (f < T.cut("scene6")) {
    return back;
  }
  const end = macroCam(MACRO_SCALE * 1.04);
  const pulled = mixCam(end, heroCam, move(f, "heroIn"));
  // Almost imperceptible push while the end card settles.
  return { ...pulled, scale: pulled.scale * (1 + 0.01 * smooth(f, T.end("heroIn"), END)) };
};

/** Where the arm starts: off the left edge and just below the frame, so the
 *  hand sweeps in from the left (following the intro's logo, which leaves to
 *  the right) while the forearm, which runs off the lower right, rises in
 *  from under the bottom edge instead of popping in across the frame. */
const ARM_FROM: Pt = [-1300, 580];

export const armOffset = (f: number): [number, number] => {
  const t = move(f, "armIn");
  return [ARM_FROM[0] * (1 - t), ARM_FROM[1] * (1 - t)];
};

const FLOAT_FROM: Pt = [-280, 360];
const FLOAT_CTRL: Pt = [150, 520];
const HOVER: Pt = [PATCH_REST[0] - 24, PATCH_REST[1] - 150];

/** Treatment illumination: one breath per bar from beat 48 (matches the
 *  bed's tonal swell: rise 0.35s, decay 0.5s). */
export const treatmentGlow = (f: number): number => {
  const start = T.start("treatment");
  if (f < start) return 0;
  const bar = T.beat(4) - T.beat(0);
  const since = f - start;
  const t = (since % bar) / FPS;
  const swell = t < 0.35 ? Math.sin((Math.PI / 2) * (t / 0.35)) ** 2 : Math.exp(-(t - 0.35) / 0.5);
  // A floor fades in with the first breath so it never drops to dark.
  const floor = 0.18 * Math.min(1, since / fr(24));
  return Math.min(1, floor + 0.82 * swell);
};

export const patchState = (f: number): PatchState => {
  const u = easeInOut(f, "patchFloat");
  const v = easeInOut(f, "patchPress");
  const floatPos = quad(FLOAT_FROM, FLOAT_CTRL, HOVER, u);
  const pos = mixPt(floatPos, PATCH_REST, v);
  const rot = mix(mix(-24, REST_ROT + 4, u), REST_ROT, v);
  const scale = mix(mix(1.3, 1.1, u), 1, v);

  // Compression: 4 (authored) frames in, then it lands back softly as the
  // edges settle.
  const c0 = T.start("squash");
  const cIn = fr(4);
  const squash =
    f < c0 ? 0 : f < c0 + cIn ? Easing.out(Easing.quad)((f - c0) / cIn) : 1 - land(f, FPS, c0 + cIn, fr(20));

  const inScene2 = f >= T.cut("scene2") && f < T.cut("scene3");
  const scanT = interpolate(f, [T.start("scan"), T.end("scan")], [0, 1], {
    easing: Easing.inOut(Easing.sin),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scanning = f >= T.start("scan") && f <= T.end("scan");

  // Pod ring: lit by activation (scene 2). In the treatment the app's ring
  // arrives as an overlay and locks onto the pod at the end of the morph.
  const ring =
    f < T.cut("scene3")
      ? move(f, "activate") > 0.001 ? interpolate(move(f, "activate"), [0, 0.9], [0, 1], { extrapolateRight: "clamp" }) : 0
      : f >= T.end("ringToPatch")
        ? 1
        : 0;

  return {
    pos,
    rot,
    scale,
    squash: Math.max(0, squash),
    ring,
    scanX: inScene2 && scanning ? mix(-1, 1, scanT) : null,
    scanY: null,
    glow: treatmentGlow(f),
  };
};

export const shadowState = (f: number) => {
  const u = easeInOut(f, "patchFloat");
  const v = easeInOut(f, "patchPress");
  return {
    pos: PATCH_REST,
    spread: mix(1.25, 1, v),
    strength: 0.16 * v * Math.min(1, u),
  };
};

/** Points on screen whose speed drives motion-blur sampling. */
export const stageTracked = (f: number): Pt[] => {
  const cam = camera(f);
  const p = patchState(f);
  const off = armOffset(f);
  return [
    worldToCanvas(cam, armLocalToWorld([-300, 0], off)),
    worldToCanvas(cam, armLocalToWorld([900, 0], off)),
    worldToCanvas(cam, p.pos),
    worldToCanvas(cam, [p.pos[0] + 150 * p.scale, p.pos[1]]),
    worldToCanvas(cam, [0, 0]),
    worldToCanvas(cam, [CANVAS.w, CANVAS.h]),
  ];
};
