import { Easing, interpolate } from "remotion";
import { type View, toCanvas } from "./Device";
import { type Rect, focus, SCREEN, THERAPY } from "./screens";
import { fr, mix, mixPt, move, T } from "./time";

// The phone holds still on the right while the explanation runs on the left.
// Focus moves with a dimming mask that glides between real UI regions, so
// there is one focal point at a time and no zoom/pan churn.

export const V_PHONE: View = { k: 1.18, focus: [195, 422], at: [1420, 540] };
export const V_HERO: View = { k: 0.95, focus: [195, 422], at: [1590, 540] };

const OFF_RIGHT = 760;

const drift = (f: number, a: number, b: number) =>
  interpolate(f, [a, b], [0, 1], {
    easing: Easing.bezier(0.45, 0, 0.55, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

/** Phone view for 03 Alert + 04 Treat: slides in, holds (near-still push),
 *  slides out right as the ring carries to the patch. */
export const phoneView = (f: number): View => {
  const enter = move(f, "cardToPhone");
  const leave = move(f, "ringToPatch");
  const x = V_PHONE.at[0] + OFF_RIGHT * (1 - enter) + OFF_RIGHT * leave;
  const k = V_PHONE.k * (1 + 0.015 * drift(f, T.end("cardToPhone"), T.start("ringToPatch")));
  return { ...V_PHONE, k, at: [x, V_PHONE.at[1]] };
};

export const heroView = (f: number): View => {
  const p = move(f, "heroIn");
  return { ...V_HERO, at: mixPt([V_HERO.at[0] + 520, V_HERO.at[1]], V_HERO.at, p) };
};

const FULL: Rect = [0, 0, SCREEN.w, SCREEN.h];
const mixRect = (a: Rect, b: Rect, t: number): Rect => [
  mix(a[0], b[0], t),
  mix(a[1], b[1], t),
  mix(a[2], b[2], t),
  mix(a[3], b[3], t),
];

// Focus sequence: [cue that moves the focus there, region].
const STOPS: readonly [string, Rect][] = [
  ["focusStatus", focus.status],
  ["focusScore", focus.score],
  ["focusButton", focus.button],
  ["press", FULL],
  ["focusTimer", focus.timer],
  ["focusPlan", focus.plan],
];

/** Current focus hole (css px) and how strongly the rest is dimmed. */
export const focusState = (f: number): { rect: Rect; dim: number } => {
  let rect: Rect = FULL;
  for (const [cue, r] of STOPS) {
    rect = mixRect(rect, r, move(f, cue));
  }
  const releaseAt = T.start("ringToPatch") - fr(15);
  const dim =
    move(f, "focusStatus") * (1 - move(f, "press")) +
    move(f, "focusTimer") * (1 - drift(f, releaseAt, releaseAt + fr(15)));
  return { rect: dim > 0.001 ? rect : FULL, dim };
};

/** The therapy countdown in the app: one real capture per second since the
 *  screen opened (09:00, 08:59, ...). */
export const remainingAt = (f: number): number => {
  const elapsed = Math.max(0, Math.floor((f - T.start("therapyReveal")) / 60));
  return Math.max(THERAPY.last, THERAPY.start - elapsed);
};

export const viewTracked = (v: View): [number, number][] => [
  toCanvas(v, [0, 0]),
  toCanvas(v, [390, 844]),
];
