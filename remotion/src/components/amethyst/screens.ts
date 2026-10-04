import { staticFile } from "remotion";

// Real Amethyst app screens, captured from the app source at 390x844 css px
// (4x: 1560x3376), with the app's mock data aligned to the wound agent's
// sample assessment (docs/app-agent-alignment.patch). Rects were measured
// from the live build in css px, so overlays land exactly on real UI.
export const SCREEN = { w: 390, h: 844, px: 4 } as const;

export type Rect = readonly [x: number, y: number, w: number, h: number];

export const screens = {
  alert: staticFile("screens/alert.png"),
} as const;

// The therapy screen counts down live in the app. One real capture per
// second, 09:00 -> 08:45 (remaining 540 -> 525 s of a 15 min dose).
export const THERAPY = { start: 540, last: 525, doseSeconds: 15 * 60 } as const;
export const therapyShot = (remaining: number): string => {
  const r = Math.max(THERAPY.last, Math.min(THERAPY.start, Math.round(remaining)));
  return staticFile(`screens/therapy/therapy-${r}.png`);
};
/** Ring progress exactly as TherapyScreen computes it. */
export const therapyProgress = (remaining: number): number =>
  1 - remaining / THERAPY.doseSeconds;

export const alertUI = {
  riskCard: [201, 442, 173, 87] as Rect,
  button: [16, 715.5, 358, 52] as Rect,
  buttonRadius: 10,
};

// Focus regions (css px), padded around real UI groups.
export const focus = {
  status: [8, 80, 374, 146] as Rect, // Warning + "Infection risk is rising" + reason
  score: [8, 434, 374, 194] as Rect, // risk score 82/100 + all five signals
  button: [8, 650, 374, 126] as Rect, // disclaimer + "Start therapy now"
  timer: [8, 134, 374, 300] as Rect, // ring + countdown + "405 nm violet light"
  plan: [8, 438, 374, 163] as Rect, // ultrasound 35 kHz · 7 min / violet light 15 min
} as const;

export const therapyUI = {
  ring: { cx: 195, cy: 256, r: 78, stroke: 10 },
};

export const center = (r: Rect): [number, number] => [
  r[0] + r[2] / 2,
  r[1] + r[3] / 2,
];
