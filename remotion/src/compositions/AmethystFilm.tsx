import React from "react";
import { AbsoluteFill, Series } from "remotion";
import { color } from "../brand/theme";
import { CANVAS } from "../components/amethyst/canvas";
import { amethystIntroComposition } from "../projects/amethyst-intro/AmethystIntro";
import { AmethystDemo, type AmethystDemoProps, amethystDemoComposition } from "./AmethystDemo";

// The full film for the slide: the intro ends on the centred logo, which
// slides out to the right; on the next frame the demo's arm is already
// sweeping in from the left. Each part keeps its own timeline, music and SFX.

const INTRO = amethystIntroComposition.durationInFrames;
const DEMO = amethystDemoComposition.durationInFrames;

export const AmethystFilm: React.FC<AmethystDemoProps> = ({ stem }) => (
  <AbsoluteFill style={{ backgroundColor: color.surface }}>
    <Series>
      <Series.Sequence durationInFrames={INTRO} name="Intro">
        <amethystIntroComposition.component />
      </Series.Sequence>
      <Series.Sequence durationInFrames={DEMO} name="Demo">
        <AmethystDemo stem={stem} />
      </Series.Sequence>
    </Series>
  </AbsoluteFill>
);

export const amethystFilmComposition = {
  id: "AmethystFilm",
  component: AmethystFilm,
  durationInFrames: INTRO + DEMO,
  fps: amethystDemoComposition.fps,
  width: CANVAS.w,
  height: CANVAS.h,
  defaultProps: { stem: "all" } as AmethystDemoProps,
} as const;
