// Beat math shared by picture (components) and sound (scripts/studio.mjs).
// No runtime imports: this file is also loaded directly by Node.

export type Cue = {
  /** Start, in beats from the top of the piece. */
  readonly at: number;
  /** Length, in beats. */
  readonly beats: number;
};

export type Hit = {
  readonly name: string;
  /** File in public/sfx (synthesized) or assets/audio. */
  readonly sfx: string;
  readonly at: number;
  readonly volume?: number;
};

export type Timeline = {
  readonly id: string;
  readonly bpm: number;
  readonly fps: number;
  /** Frame where beat 0 falls (a pickup before the first beat). Default 0. */
  readonly offsetFrames?: number;
  /** Where beats.json is written, relative to the project root. Default: next to the timeline. */
  readonly beatsJson?: string;
  /** Exact composition length in frames, if it should not end on a beat. */
  readonly durationFrames?: number;
  readonly beatsPerBar: number;
  readonly durationBeats: number;
  readonly cues: Readonly<Record<string, Cue>>;
  readonly hits: readonly Hit[];
};

export const framesPerBeat = (tl: Timeline): number => (60 / tl.bpm) * tl.fps;

/** Exact (possibly fractional) frame for a beat position. */
export const beatToFrameExact = (tl: Timeline, beats: number): number =>
  (tl.offsetFrames ?? 0) + beats * framesPerBeat(tl);

/** Frame index for a beat position. Cuts and hits use this. */
export const beatToFrame = (tl: Timeline, beats: number): number =>
  Math.round(beatToFrameExact(tl, beats));

export const cueStart = (tl: Timeline, name: string): number =>
  beatToFrameExact(tl, getCue(tl, name).at);

export const cueLength = (tl: Timeline, name: string): number =>
  getCue(tl, name).beats * framesPerBeat(tl);

export const cueEnd = (tl: Timeline, name: string): number =>
  cueStart(tl, name) + cueLength(tl, name);

export const durationInFrames = (tl: Timeline): number =>
  tl.durationFrames ?? beatToFrame(tl, tl.durationBeats);

const getCue = (tl: Timeline, name: string): Cue => {
  const cue = tl.cues[name];
  if (!cue) {
    throw new Error(`Unknown cue "${name}" in timeline ${tl.id}`);
  }
  return cue;
};

/** The beats.json shape: everything sound and review tooling need. */
export const toBeatsJson = (tl: Timeline) => {
  const total = durationInFrames(tl);
  const fpb = framesPerBeat(tl);
  const beats = [];
  for (let b = 0; (tl.offsetFrames ?? 0) + b * fpb < total; b++) {
    beats.push({
      beat: b,
      frame: beatToFrame(tl, b),
      time: beatToFrame(tl, b) / tl.fps,
    });
  }
  return {
    id: tl.id,
    bpm: tl.bpm,
    fps: tl.fps,
    offsetFrames: tl.offsetFrames ?? 0,
    durationInFrames: total,
    beats,
    downbeats: beats.filter((b) => b.beat % tl.beatsPerBar === 0),
    hits: tl.hits.map((h) => ({
      name: h.name,
      sfx: h.sfx,
      beat: h.at,
      frame: beatToFrame(tl, h.at),
      time: beatToFrame(tl, h.at) / tl.fps,
    })),
  };
};
