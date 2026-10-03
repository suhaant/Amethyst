// Music bed for AmethystDemo, synthesized from the shared timeline.
// Calm pulse every 2 beats, a soft pad that changes each bar, quiet precision
// ticks under the agent and app steps, a restrained tonal swell that breathes
// with the patch once treatment starts, and a resolve on the logo bar.
// Section boundaries come from timeline cues, never hard-coded frames.

const TAU = 2 * Math.PI;

const N = {
  G2: 98, A2: 110, B2: 123.47, D3: 146.83, E3: 164.81, Fs3: 185,
  A3: 220, Cs4: 277.18, D4: 293.66, E4: 329.63, Fs4: 369.99,
};

const BARS = [
  [N.D3, N.Fs3, N.A3, N.E4],
  [N.B2, N.D3, N.Fs3, N.A3],
  [N.G2, N.B2, N.D3, N.Fs3],
  [N.A2, N.D3, N.E3, N.A3],
];
const RESOLVE = [N.D3, N.A3, N.D4, N.Fs4];

export default function bed(tl, { SR, seconds, beatTime, mulberry32 }) {
  const cue = (name) => tl.cues[name].at;
  const len = Math.round(seconds * SR);
  const out = new Float32Array(len);
  const add = (startSec, durSec, fn) => {
    const s0 = Math.max(0, Math.round(startSec * SR));
    const s1 = Math.min(len, Math.round((startSec + durSec) * SR));
    for (let i = s0; i < s1; i++) out[i] += fn((i - s0) / SR, i / SR);
  };
  const lastBeat = tl.durationBeats;
  const resolveBar = Math.ceil(cue("scene6") / 4) * 4;
  const level = (b) =>
    b < cue("scene2") ? 0.8 : b < cue("scene3") ? 0.9 : b < cue("scene5") ? 1 : b < cue("scene6") ? 1.05 : 0.9;

  // Pad: one chord per bar, slow attack, overlapping release.
  for (let b = 0; b < lastBeat; b += 4) {
    const final = b >= resolveBar;
    const notes = final ? RESOLVE : BARS[(b / 4) % BARS.length];
    const start = beatTime(b);
    const dur = final ? seconds - start : beatTime(b + 4) - start + 0.45;
    add(start, dur, (t) => {
      const attack = Math.min(1, t / 0.4);
      const release = final ? Math.min(1, (dur - t) / 0.6) * Math.exp(-t / 3) : Math.min(1, (dur - t) / 0.45);
      let v = 0;
      for (const f of notes) {
        v += Math.sin(TAU * (f - 0.6) * t) + Math.sin(TAU * (f + 0.6) * t) + 0.2 * Math.sin(TAU * 2 * f * t);
      }
      return 0.022 * attack * release * v * level(b);
    });
  }

  // Felt low pulse every 2 beats (stops before the logo bar).
  for (let b = 0; b < resolveBar; b += 2) {
    add(beatTime(b), 0.5, (t) => {
      const e = Math.min(1, t / 0.003) * Math.exp(-t / 0.16);
      return 0.12 * level(b) * e * (Math.sin(TAU * 73.42 * t) + 0.25 * Math.sin(TAU * 146.83 * t));
    });
  }

  // Precision ticks on the off-beats under the agent and app steps.
  const rnd = mulberry32(5);
  for (let b = cue("scene3") + 0.5; b < cue("scene5"); b += 1) {
    let hp = 0;
    let prev = 0;
    add(beatTime(b), 0.05, (t) => {
      const n = rnd() * 2 - 1;
      hp = 0.85 * (hp + n - prev);
      prev = n;
      return 0.016 * hp * Math.min(1, t / 0.0005) * Math.exp(-t / 0.008);
    });
  }

  // Treatment: one restrained swell per bar, in step with the patch's
  // illumination (peaks 0.35s after the bar line).
  for (let b = cue("treatment"); b < lastBeat; b += 4) {
    add(beatTime(b), 1.5, (t) => {
      const e = t < 0.35 ? Math.sin((Math.PI / 2) * (t / 0.35)) ** 2 : Math.exp(-(t - 0.35) / 0.5);
      return 0.05 * e * (Math.sin(TAU * N.A3 * t) + 0.5 * Math.sin(TAU * N.E4 * t));
    });
  }

  // Master: click-free start, fade on the last 0.4s, normalize.
  let peak = 0;
  for (let i = 0; i < len; i++) {
    const t = i / SR;
    out[i] *= Math.min(1, t / 0.01) * Math.min(1, (seconds - t) / 0.4);
    peak = Math.max(peak, Math.abs(out[i]));
  }
  const gain = 0.4 / (peak || 1);
  for (let i = 0; i < len; i++) out[i] *= gain;
  return out;
}
