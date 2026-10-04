// The only place timing lives for the Amethyst intro. Everything is in beats.
// 120 bpm @ 60 fps -> 1 beat = 30 frames = 0.5s.
//
// Same arc as the Quest intro: the product floats in 3D with its light lit,
// the camera dives into the light, a violet whiteout flashes, the crystal
// slams together from its facets, then settles into the centred logo
// (wordmark + crystal only), holds, and slides out to the right, where the
// demo's arm takes over from the left (AmethystFilm).
import type { Timeline } from "../../studio/beats";

export const timeline: Timeline = {
  id: "AmethystIntro",
  bpm: 120,
  fps: 60,
  beatsPerBar: 4,
  durationBeats: 10,
  cues: {
    // Patch is already drifting in on frame 0 and orbits toward camera.
    patchIn: { at: -0.25, beats: 2 },
    // Pod ring lights up and breathes.
    ringGlow: { at: 0.5, beats: 2 },
    // Camera dives into the ring; violet light floods the frame.
    dive: { at: 2.5, beats: 1 },
    // Whiteout peaks, facets slam together.
    slam: { at: 3.5, beats: 0.75 },
    // Crystal travels to its lockup spot; wordmark rises letter by letter.
    lockup: { at: 5.5, beats: 1.25 },
    // The logo holds, then leaves to the right; the film cuts to the demo
    // on the last frame of this move.
    logoOut: { at: 8.75, beats: 1.25 },
  },
  hits: [
    { name: "whoosh: dive", sfx: "whoosh.wav", at: 2.75, volume: 0.8 },
    { name: "low hit: slam", sfx: "low-hit.wav", at: 3.5 },
    { name: "whoosh: lockup", sfx: "whoosh.wav", at: 5.5, volume: 0.5 },
    { name: "warm hit: logo lands", sfx: "warm-hit.wav", at: 6.75, volume: 0.6 },
    { name: "whoosh: logo out", sfx: "whoosh.wav", at: 8.75, volume: 0.35 },
  ],
};
