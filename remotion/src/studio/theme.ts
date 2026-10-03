import { loadFont } from "@remotion/google-fonts/InstrumentSans";

// One type family, one accent, one spacing scale. Projects may swap these
// values per brand, but never add a second accent or family.
const { fontFamily } = loadFont("normal", {
  weights: ["500", "600"],
  subsets: ["latin"],
});

export const theme = {
  font: fontFamily,
  color: {
    paper: "#EEECE6",
    ink: "#16151A",
    muted: "#8A8790",
    accent: "#5A2FD9",
  },
  /** 8px base. Use these, never ad-hoc numbers. */
  space: [0, 8, 16, 24, 32, 48, 64, 96, 128, 192] as const,
  /** Reels-safe margins (px at 1080x1920). */
  safe: { top: 220, bottom: 420, left: 96, right: 160 },
} as const;

export const REELS = { width: 1080, height: 1920, fps: 60 } as const;
