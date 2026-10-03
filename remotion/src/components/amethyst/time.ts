import { Easing, interpolate } from "remotion";
import {
  beatToFrame,
  beatToFrameExact,
  cueEnd,
  cueLength,
  cueStart,
} from "../../studio/beats";
import { land } from "../../studio/motion";
import { timeline } from "../../timeline/amethyst-demo";

export const FPS = timeline.fps;

/** Frame helpers bound to the AmethystDemo timeline. */
export const T = {
  start: (cue: string) => cueStart(timeline, cue),
  len: (cue: string) => cueLength(timeline, cue),
  end: (cue: string) => cueEnd(timeline, cue),
  beat: (b: number) => beatToFrameExact(timeline, b),
  /** Integer frame of a cue start: where cuts and hits land. */
  cut: (cue: string) => beatToFrame(timeline, timeline.cues[cue].at),
};

/** Arrive fast, land soft over a cue (0 -> 1). */
export const move = (frame: number, cue: string): number =>
  land(frame, FPS, T.start(cue), T.len(cue));

/** Symmetric ease-in-out over a cue (the "easy ease" float). */
export const easeInOut = (frame: number, cue: string): number =>
  interpolate(frame, [T.start(cue), T.end(cue)], [0, 1], {
    easing: Easing.bezier(0.45, 0, 0.25, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

export const mix = (a: number, b: number, t: number): number => a + (b - a) * t;

export const mixPt = (
  a: readonly [number, number],
  b: readonly [number, number],
  t: number,
): [number, number] => [mix(a[0], b[0], t), mix(a[1], b[1], t)];
