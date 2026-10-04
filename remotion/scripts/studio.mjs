#!/usr/bin/env node
// Studio CLI: synth SFX, write beats.json, draft/final renders, review tools.
//
//   node scripts/studio.mjs sfx                  synthesize SFX into public/sfx
//   node scripts/studio.mjs beats                write beats.json for every project
//   node scripts/studio.mjs draft   <Id>         low-res draft -> out/<Id>/draft.mp4
//   node scripts/studio.mjs contact <Id>         one frame per beat -> out/<Id>/contact.png
//   node scripts/studio.mjs popscan <video>      flag single-frame pops
//   node scripts/studio.mjs sync    <Id>         render the SFX stem, check each hit lands on its frame
//   node scripts/studio.mjs still   <Id> <frame> [out.png]
//   node scripts/studio.mjs final   <Id>         full-quality render -> out/<Id>/<Id>.mp4
//   node scripts/studio.mjs bed                  synthesize music beds (scripts/beds/<Id>.mjs)
//   node scripts/studio.mjs review  <Id>         draft + contact + popscan + sync

import { spawnSync } from "node:child_process";
import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const BIN = path.join(ROOT, "node_modules", ".bin", "remotion");
const SR = 48000;

const run = (args, opts = {}) => {
  const res = spawnSync(BIN, args, { cwd: ROOT, stdio: "inherit", ...opts });
  if (res.status !== 0) {
    throw new Error(`remotion ${args.join(" ")} failed (${res.status})`);
  }
  return res;
};
// Remotion's bundled ffmpeg is a minimal build (no select/tile/drawtext), so
// review tools use the full build from ffmpeg-static.
const FFMPEG = createRequire(import.meta.url)("ffmpeg-static");
const ffmpeg = (args) => {
  const res = spawnSync(FFMPEG, ["-hide_banner", "-loglevel", "error", "-y", ...args], { cwd: ROOT, stdio: "inherit" });
  if (res.status !== 0) {
    throw new Error(`ffmpeg ${args.join(" ")} failed (${res.status})`);
  }
};

// ---------- projects ----------

// Timelines live in src/projects/<name>/timeline.ts or src/timeline/<name>.ts.
const timelineFiles = () => {
  const files = [];
  const projects = path.join(ROOT, "src", "projects");
  if (fs.existsSync(projects)) {
    for (const name of fs.readdirSync(projects)) {
      const f = path.join(projects, name, "timeline.ts");
      if (fs.existsSync(f)) files.push(f);
    }
  }
  const flat = path.join(ROOT, "src", "timeline");
  if (fs.existsSync(flat)) {
    for (const name of fs.readdirSync(flat)) {
      if (name.endsWith(".ts")) files.push(path.join(flat, name));
    }
  }
  return files;
};

const loadProjects = async () => {
  const out = {};
  for (const file of timelineFiles()) {
    const { timeline } = await import(pathToFileURL(file).href);
    const beatsFile = timeline.beatsJson
      ? path.join(ROOT, timeline.beatsJson)
      : path.join(path.dirname(file), "beats.json");
    out[timeline.id] = { timeline, beatsFile };
  }
  return out;
};

const readBeats = async (id) => {
  const { beatsFile } = await getProject(id);
  return JSON.parse(fs.readFileSync(beatsFile, "utf8"));
};

const getProject = async (id) => {
  const projects = await loadProjects();
  const p = projects[id];
  if (!p) {
    throw new Error(`No project "${id}". Known: ${Object.keys(projects).join(", ")}`);
  }
  return p;
};

const outDir = (id) => {
  const d = path.join(ROOT, "out", id);
  fs.mkdirSync(d, { recursive: true });
  return d;
};

// ---------- beats.json ----------

const writeBeats = async () => {
  const { toBeatsJson } = await import(
    pathToFileURL(path.join(ROOT, "src", "studio", "beats.ts")).href
  );
  const projects = await loadProjects();
  for (const { timeline, beatsFile: file } of Object.values(projects)) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, JSON.stringify(toBeatsJson(timeline), null, 2) + "\n");
    console.log(`beats.json -> ${path.relative(ROOT, file)}`);
  }
};

// ---------- SFX synthesis (deterministic) ----------

const mulberry32 = (seed) => () => {
  seed |= 0;
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const writeWav = (file, samples) => {
  const data = Buffer.alloc(samples.length * 2);
  for (let i = 0; i < samples.length; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    data.writeInt16LE(Math.round(s * 32767), i * 2);
  }
  const h = Buffer.alloc(44);
  h.write("RIFF", 0);
  h.writeUInt32LE(36 + data.length, 4);
  h.write("WAVE", 8);
  h.write("fmt ", 12);
  h.writeUInt32LE(16, 16);
  h.writeUInt16LE(1, 20);
  h.writeUInt16LE(1, 22);
  h.writeUInt32LE(SR, 24);
  h.writeUInt32LE(SR * 2, 28);
  h.writeUInt16LE(2, 32);
  h.writeUInt16LE(16, 34);
  h.write("data", 36);
  h.writeUInt32LE(data.length, 40);
  fs.writeFileSync(file, Buffer.concat([h, data]));
};

// Attack is <=1ms so the onset is on the frame the sound is placed on.
const synth = (seconds, fn) =>
  Float32Array.from({ length: Math.round(seconds * SR) }, (_, i) => fn(i / SR, i));
const env = (t, attack, decay, total) =>
  Math.min(1, t / attack) * Math.exp(-t / decay) * Math.min(1, (total - t) / 0.004);

const sine = (f, t) => Math.sin(2 * Math.PI * f * t);

const SFX = {
  // Soft tactile contact: a padded low thump with a short damped skin tap.
  "contact.wav": () => {
    const rnd = mulberry32(31);
    let lp = 0;
    return synth(0.28, (t) => {
      const a = 1 - Math.exp((-2 * Math.PI * 900) / SR);
      lp += a * (rnd() * 2 - 1 - lp);
      const tap = lp * env(t, 0.0008, 0.012, 0.28) * 1.6;
      const body = sine(92 + 40 * Math.exp(-t / 0.03), t) * env(t, 0.001, 0.07, 0.28);
      return 0.75 * (tap + body);
    });
  },
  // Precise activation tone: clean B5 with a quiet fifth, short tail.
  "activate.wav": () =>
    synth(0.55, (t) => {
      const e = env(t, 0.001, 0.16, 0.55);
      return 0.45 * e * (sine(987.77, t) + 0.25 * sine(1479.98, t) + 0.08 * sine(1975.53, t));
    }),
  // Restrained UI tick for a real tap.
  "tick.wav": () =>
    synth(0.04, (t) => {
      const e = env(t, 0.0004, 0.004, 0.04);
      return 0.55 * e * (sine(3200, t) + 0.5 * sine(1600, t));
    }),
  // Low, warm hit: soft sine body (D2) with a gentle octave, long decay.
  "warm-hit.wav": () => {
    let phase = 0;
    return synth(1.6, (t) => {
      const f = 73.42 + 18 * Math.exp(-t / 0.04);
      phase += (2 * Math.PI * f) / SR;
      const e = env(t, 0.001, 0.45, 1.6);
      return 0.8 * e * (Math.sin(phase) + 0.3 * Math.sin(2 * phase) + 0.06 * sine(587.33, t) * Math.exp(-t / 0.08));
    });
  },
  // Subtle sonic resolution on the logo: soft bell on D (D5 A5 D6).
  "resolve.wav": () =>
    synth(2.4, (t) => {
      const partial = (f, a, d) => a * sine(f, t) * Math.exp(-t / d);
      const e = Math.min(1, t / 0.001) * Math.min(1, (2.4 - t) / 0.05);
      return 0.32 * e * (partial(587.33, 1, 0.9) + partial(880, 0.55, 0.7) + partial(1174.66, 0.35, 0.5) + partial(1762, 0.1, 0.25));
    }),
  // Short clean beep: 880 Hz with a soft octave.
  "beep.wav": () =>
    synth(0.16, (t) => {
      const e = env(t, 0.001, 0.05, 0.16);
      return 0.55 * e * (Math.sin(2 * Math.PI * 880 * t) + 0.18 * Math.sin(2 * Math.PI * 1760 * t));
    }),
  // UI click for presses: very short filtered noise tick + body.
  "click.wav": () => {
    const rnd = mulberry32(7);
    return synth(0.05, (t) => {
      const e = env(t, 0.0005, 0.006, 0.05);
      return 0.6 * e * ((rnd() * 2 - 1) * 0.5 + Math.sin(2 * Math.PI * 2200 * t));
    });
  },
  // Whoosh for morphs: noise through a sweeping one-pole lowpass, swelling in.
  "whoosh.wav": () => {
    const rnd = mulberry32(11);
    let lp = 0;
    const total = 0.45;
    return synth(total, (t) => {
      const u = t / total;
      const cutoff = 300 + 5000 * Math.sin(Math.PI * u);
      const a = 1 - Math.exp((-2 * Math.PI * cutoff) / SR);
      lp += a * (rnd() * 2 - 1 - lp);
      const swell = Math.max(0.45 * Math.exp(-t / 0.06), Math.sin(Math.PI * Math.min(1, u * 1.4)));
      return 0.9 * lp * swell * Math.min(1, t / 0.001);
    });
  },
  // Low hit for logos: pitch-dropping sine thump + short noise transient.
  "low-hit.wav": () => {
    const rnd = mulberry32(23);
    let phase = 0;
    return synth(0.9, (t) => {
      const f = 45 + 70 * Math.exp(-t / 0.05);
      phase += (2 * Math.PI * f) / SR;
      const body = Math.sin(phase) * env(t, 0.001, 0.32, 0.9);
      const snap = (rnd() * 2 - 1) * env(t, 0.0005, 0.01, 0.9) * 0.4;
      return 0.85 * (body + snap);
    });
  },
};

const writeSfx = () => {
  const dir = path.join(ROOT, "public", "sfx");
  fs.mkdirSync(dir, { recursive: true });
  for (const [name, make] of Object.entries(SFX)) {
    writeWav(path.join(dir, name), make());
  }
  // Real audio assets are served next to the synthesized ones.
  const assets = path.join(ROOT, "assets", "audio");
  if (fs.existsSync(assets)) {
    for (const f of fs.readdirSync(assets)) {
      if (/\.(wav|mp3|m4a|aac|ogg|flac)$/i.test(f)) {
        fs.copyFileSync(path.join(assets, f), path.join(dir, f));
      }
    }
  }
  console.log(`sfx -> public/sfx (${fs.readdirSync(dir).join(", ")})`);
};

// ---------- music beds ----------
// scripts/beds/<Id>.mjs default-exports (timeline, kit) => Float32Array (mono, 48 kHz).

const writeBeds = async () => {
  const { beatToFrameExact, durationInFrames } = await import(
    pathToFileURL(path.join(ROOT, "src", "studio", "beats.ts")).href
  );
  const projects = await loadProjects();
  const dir = path.join(ROOT, "public", "audio");
  for (const { timeline } of Object.values(projects)) {
    const bedFile = path.join(ROOT, "scripts", "beds", `${timeline.id}.mjs`);
    if (!fs.existsSync(bedFile)) continue;
    const { default: bed } = await import(pathToFileURL(bedFile).href);
    const beatTime = (b) => beatToFrameExact(timeline, b) / timeline.fps;
    const seconds = durationInFrames(timeline) / timeline.fps;
    const samples = bed(timeline, { SR, seconds, beatTime, mulberry32 });
    fs.mkdirSync(dir, { recursive: true });
    writeWav(path.join(dir, `${timeline.id}-bed.wav`), samples);
    console.log(`bed -> public/audio/${timeline.id}-bed.wav`);
  }
};

// ---------- renders ----------

const prepare = async () => {
  writeSfx();
  await writeBeats();
  await writeBeds();
};

const draft = async (id) => {
  await getProject(id);
  await prepare();
  const out = path.join(outDir(id), "draft.mp4");
  run(["render", "src/index.ts", id, out, "--scale=0.5", "--crf=26", "--image-format=jpeg", "--jpeg-quality=80", "--x264-preset=veryfast"]);
  return out;
};

const final = async (id) => {
  await getProject(id);
  await prepare();
  const out = path.join(outDir(id), `${id}.mp4`);
  run(["render", "src/index.ts", id, out, "--crf=14", "--x264-preset=slow", "--image-format=png", "--audio-codec=aac", "--audio-bitrate=320k"]);
  return out;
};

const still = async (id, frame, out) => {
  await prepare();
  const file = out ?? path.join(outDir(id), `frame-${frame}.png`);
  run(["still", "src/index.ts", id, file, `--frame=${frame}`, "--image-format=png"]);
  return file;
};

// ---------- review ----------

const contact = async (id, video) => {
  const beats = await readBeats(id);
  const src = video ?? path.join(outDir(id), "draft.mp4");
  const frames = beats.beats.map((b) => b.frame);
  const cols = frames.length <= 6 ? frames.length : 10;
  const tileW = frames.length <= 6 ? 360 : 300;
  const rows = Math.ceil(frames.length / cols);
  const select = frames.map((f) => `eq(n\\,${f})`).join("+");
  const out = path.join(outDir(id), "contact.png");
  // Filter goes through a script file so no layer re-parses the commas.
  const filter = path.join(outDir("_tmp"), "contact.filter");
  const label = `drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:text='f%{eif\\:t*${beats.fps}\\:d}':x=8:y=8:fontsize=${frames.length <= 6 ? 22 : 16}:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=6`;
  fs.writeFileSync(filter, `select=${select},scale=${tileW}:-1,${label},tile=${cols}x${rows}:padding=12:margin=12:color=0x222222`);
  ffmpeg(["-i", src, "-filter_script:v", filter, "-frames:v", "1", "-fps_mode", "passthrough", out]);
  fs.rmSync(filter);
  console.log(`contact sheet (beats ${frames.join(", ")}) -> ${path.relative(ROOT, out)}`);
  return out;
};

const readRaw = (file) => {
  const buf = fs.readFileSync(file);
  fs.rmSync(file);
  return buf;
};

const popscan = (video) => {
  const W = 135;
  const H = 240;
  const tmp = path.join(outDir("_tmp"), "frames.gray");
  ffmpeg(["-i", video, "-vf", `scale=${W}:${H},format=gray`, "-f", "rawvideo", tmp]);
  const buf = readRaw(tmp);
  const n = buf.length / (W * H);
  const frame = (i) => buf.subarray(i * W * H, (i + 1) * W * H);
  const diff = (a, b) => {
    let s = 0;
    for (let i = 0; i < a.length; i++) s += Math.abs(a[i] - b[i]);
    return s / a.length;
  };
  const d = [0];
  for (let i = 1; i < n; i++) d.push(diff(frame(i - 1), frame(i)));
  const sorted = [...d].sort((a, b) => a - b);
  const median = sorted[Math.floor(sorted.length / 2)];
  const T = Math.max(1.5, 4 * median);
  const pops = [];
  for (let i = 1; i < n - 1; i++) {
    if (d[i] > T && d[i + 1] > T) {
      const skip = diff(frame(i - 1), frame(i + 1));
      if (skip < 0.5 * Math.min(d[i], d[i + 1])) {
        pops.push({ frame: i, in: +d[i].toFixed(2), out: +d[i + 1].toFixed(2), skip: +skip.toFixed(2) });
      }
    }
  }
  // Blank = a frame with (almost) no structure: one flat color.
  const blanks = [];
  for (let i = 0; i < n; i++) {
    const f = frame(i);
    let min = 255;
    let max = 0;
    for (let j = 0; j < f.length; j++) {
      if (f[j] < min) min = f[j];
      if (f[j] > max) max = f[j];
    }
    if (max - min < 6) blanks.push(i);
  }
  console.log(blanks.length ? `BLANK FRAMES: ${blanks.join(", ")}` : "popscan: no blank frames");
  const peak = d.reduce((m, v, i) => (v > m.v ? { v, i } : m), { v: 0, i: 0 });
  console.log(`popscan: ${n} frames, median diff ${median.toFixed(2)}, peak ${peak.v.toFixed(2)} @ frame ${peak.i}`);
  console.log(pops.length ? `POPS: ${JSON.stringify(pops)}` : "popscan: no single-frame pops");
  return pops;
};

const sync = async (id) => {
  const beats = await readBeats(id);
  // Render only the SFX stem (compositions mute their music bed when
  // stem = "sfx") so onsets are measured without the bed underneath.
  const src = path.join(outDir(id), "sfx-stem.wav");
  run(["render", "src/index.ts", id, src, "--codec=wav", `--props=${JSON.stringify({ stem: "sfx" })}`, "--log=error"]);
  const tmp = path.join(outDir("_tmp"), "audio.pcm");
  ffmpeg(["-i", src, "-vn", "-ac", "1", "-ar", String(SR), "-f", "s16le", tmp]);
  const buf = readRaw(tmp);
  const pcm = new Int16Array(buf.buffer, buf.byteOffset, buf.length / 2);
  // Onset = first sample over threshold after >=50ms of quiet.
  const thr = 0.02 * 32767;
  const quiet = 0.03 * SR;
  const onsets = [];
  let lastLoud = -Infinity;
  for (let i = 0; i < pcm.length; i++) {
    if (Math.abs(pcm[i]) > thr) {
      if (i - lastLoud > quiet) onsets.push(i);
      lastLoud = i;
    }
  }
  let ok = true;
  for (const hit of beats.hits) {
    const target = (hit.frame / beats.fps) * SR;
    const near = onsets.reduce((b, o) => (Math.abs(o - target) < Math.abs(b - target) ? o : b), Infinity);
    const frame = Math.floor((near / SR) * beats.fps);
    const ms = ((near - target) / SR) * 1000;
    const pass = frame === hit.frame;
    ok &&= pass;
    console.log(
      `sync: ${hit.name} target frame ${hit.frame} (${hit.time.toFixed(3)}s) -> onset ${(near / SR).toFixed(4)}s = frame ${frame} (${ms >= 0 ? "+" : ""}${ms.toFixed(2)} ms) ${pass ? "OK" : "MISS"}`,
    );
  }
  console.log(`sync: ${onsets.length} onsets total`);
  return ok;
};

// ---------- main ----------

const [cmd, ...args] = process.argv.slice(2);
const commands = {
  sfx: writeSfx,
  beats: writeBeats,
  draft: () => draft(args[0]),
  final: () => final(args[0]),
  still: () => still(args[0], args[1], args[2]),
  contact: () => contact(args[0], args[1]),
  popscan: () => popscan(args[0]),
  sync: () => sync(args[0]),
  bed: writeBeds,
  review: async () => {
    const video = await draft(args[0]);
    await contact(args[0], video);
    popscan(video);
    await sync(args[0]);
  },
};

if (!commands[cmd]) {
  console.log(fs.readFileSync(fileURLToPath(import.meta.url), "utf8").split("\n").slice(1, 14).join("\n"));
  process.exit(cmd ? 1 : 0);
}
await commands[cmd]();
