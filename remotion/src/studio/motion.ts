import { Easing, interpolate, spring } from "remotion";

/**
 * Arrive fast, land soft: a critically damped spring. Fast at the start,
 * eases into its target with no overshoot (no bounce) and no dead stop.
 */
export const land = (
  frame: number,
  fps: number,
  start: number,
  duration: number,
): number =>
  spring({
    frame: frame - start,
    fps,
    durationInFrames: duration,
    config: { damping: 200, stiffness: 100, mass: 1 },
  });

/** Slow camera push-in that keeps holds alive. Never constant speed. */
export const pushIn = (
  frame: number,
  total: number,
  amount = 0.035,
): number =>
  interpolate(frame, [0, total], [1, 1 + amount], {
    easing: Easing.bezier(0.45, 0, 0.55, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

/** Start frame of item i in a group. Rule: 2-4 frames apart. */
export const stagger = (start: number, i: number, gap = 3): number =>
  start + i * gap;
