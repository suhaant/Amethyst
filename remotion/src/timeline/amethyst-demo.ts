// AmethystDemo: the only place timing lives. Picture (src/scenes) and sound
// (bed + SFX, scripts/studio.mjs) both read this file.
//
// 30 s explainer, 1920x1080 @ 60 fps, built to be talked over:
// 01 Sense -> 02 Reason (the AI agent) -> 03 Alert (app) -> 04 Treat -> logo.
// Grid: 120 bpm, one beat = 30 frames. frame = 30 * beat.
import type { Timeline } from "../studio/beats";

export const timeline: Timeline = {
  id: "AmethystDemo",
  bpm: 120,
  fps: 60,
  beatsPerBar: 4,
  durationBeats: 60,
  beatsJson: "public/audio/beats.json",
  cues: {
    // ── Hook · apply the patch (0:00–0:04) ──
    scene1: { at: 0, beats: 8 },
    armIn: { at: -0.4, beats: 1.4 },
    patchFloat: { at: 1, beats: 1.5 },
    patchPress: { at: 3, beats: 1 }, // contact on beat 4
    squash: { at: 4, beats: 1 },
    intro: { at: 4.5, beats: 0.75 }, // "A patch that senses, predicts, and treats."
    introOut: { at: 6.25, beats: 0.6 },
    macro: { at: 6.5, beats: 1.25 },

    // ── 01 Sense (0:04–0:08.5) ──
    scene2: { at: 8, beats: 9 },
    senseHeader: { at: 8.5, beats: 0.75 },
    activate: { at: 9.5, beats: 0.6 }, // pod light + activation tone
    scan: { at: 9.5, beats: 1.5 },
    readingCard: { at: 11, beats: 0.75 },
    senseOut: { at: 14.75, beats: 0.75 },
    // One move at a time: the patch drops out, then the reading card glides
    // into the agent diagram.
    patchOut: { at: 15, beats: 1.25 },
    handoff: { at: 15.5, beats: 1.5 },

    // ── 02 Reason · the agent (0:08.5–0:16.5) ──
    scene3: { at: 17, beats: 16 },
    reasonHeader: { at: 17, beats: 0.75 },
    agentIn: { at: 17.5, beats: 0.75 },
    tool1: { at: 18.5, beats: 0.75 }, // get_sensor_reading
    tool2: { at: 21, beats: 0.75 }, // predict_infection
    tool3: { at: 24, beats: 0.75 }, // plan_treatment
    judge: { at: 27, beats: 0.75 }, // the agent judges the evidence
    reasonOut: { at: 32, beats: 0.75 },

    // ── 03 Alert · the app (0:16.5–0:22.5) ──
    scene4: { at: 33, beats: 12 },
    // The assessment card opens into the phone (mask morph).
    cardToPhone: { at: 33, beats: 1.5 },
    alertHeader: { at: 33, beats: 0.75 },
    focusStatus: { at: 35, beats: 0.6 },
    focusScore: { at: 37, beats: 0.6 },
    focusButton: { at: 39.5, beats: 0.6 },
    press: { at: 42, beats: 0.4 }, // real tap: "Start therapy now"
    therapyReveal: { at: 42.25, beats: 1.5 },

    // ── 04 Treat (0:22.5–0:27.5) ──
    scene5: { at: 45, beats: 10 },
    treatHeader: { at: 45, beats: 0.75 },
    focusTimer: { at: 45.5, beats: 0.6 },
    focusPlan: { at: 47.5, beats: 0.6 },
    // The therapy ring leaves the phone and lands on the pod.
    ringToPatch: { at: 50, beats: 1.5 },
    treatment: { at: 51.5, beats: 8.5 }, // warm hit + slow violet breathing

    // ── Logo (0:27.5–0:30) ──
    scene6: { at: 55, beats: 5 },
    heroIn: { at: 55, beats: 1.5 },
    mark: { at: 55 + 1 / 3, beats: 0.75 }, // 5th facet lands on beat 56
    wordmark: { at: 56.5, beats: 0.75 },
    closingLine: { at: 57, beats: 0.75 },
  },
  hits: [
    { name: "contact", sfx: "contact.wav", at: 4, volume: 0.9 },
    { name: "activate", sfx: "activate.wav", at: 9.5, volume: 0.5 },
    { name: "whoosh: reading to agent", sfx: "whoosh.wav", at: 15.5, volume: 0.25 },
    { name: "tick: get_sensor_reading", sfx: "tick.wav", at: 18.5, volume: 0.3 },
    { name: "tick: predict_infection", sfx: "tick.wav", at: 21, volume: 0.3 },
    { name: "tick: plan_treatment", sfx: "tick.wav", at: 24, volume: 0.3 },
    { name: "whoosh: assessment to app", sfx: "whoosh.wav", at: 33, volume: 0.3 },
    { name: "tick: start therapy", sfx: "tick.wav", at: 42, volume: 0.5 },
    { name: "whoosh: ring to patch", sfx: "whoosh.wav", at: 50, volume: 0.28 },
    { name: "warm hit: treatment", sfx: "warm-hit.wav", at: 51.5, volume: 0.8 },
    { name: "resolve: logo", sfx: "resolve.wav", at: 56, volume: 0.5 },
  ],
};
