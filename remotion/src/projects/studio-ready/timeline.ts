// The only place timing lives for this piece. Everything is in beats.
// 120 bpm @ 60 fps -> 1 beat = 30 frames = 0.5s.
import type { Timeline } from "../../studio/beats";

export const timeline: Timeline = {
  id: "StudioReady",
  bpm: 120,
  fps: 60,
  beatsPerBar: 4,
  durationBeats: 6,
  cues: {
    // Dot is already mid-flight and readable on frame 0 (the hook).
    rise: { at: -0.375, beats: 1.25 },
    // Dot stretches into the pill on beat 2 (= 1.0s).
    stretch: { at: 2, beats: 1 },
    // Words slide up once the pill is ~85% open, so they never hit its edge.
    words: { at: 2.45, beats: 0.75 },
  },
  hits: [{ name: "beep", sfx: "beep.wav", at: 2 }],
};
