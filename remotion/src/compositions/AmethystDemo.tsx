import { Audio } from "@remotion/media";
import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { color } from "../brand/theme";
import { CANVAS } from "../components/amethyst/canvas";
import { AgentReasoning } from "../scenes/AgentReasoning";
import { Analyze } from "../scenes/Analyze";
import { AppAnalysis } from "../scenes/AppAnalysis";
import { ApplyPatch } from "../scenes/ApplyPatch";
import { EndCard } from "../scenes/EndCard";
import { Treatment } from "../scenes/Treatment";
import { durationInFrames } from "../studio/beats";
import { TimelineSfx } from "../studio/Sfx";
import { timeline } from "../timeline/amethyst-demo";

// Amethyst · 30s landscape explainer (1920x1080, for the slideshow), built
// to be talked over: 01 Sense -> 02 Reason (AI agent) -> 03 Alert -> 04 Treat. All timing: src/timeline/amethyst-demo.ts.

export type AmethystDemoProps = {
  /** "sfx" mutes the music bed (used by the sync check). */
  readonly stem: "all" | "sfx";
};

export const AmethystDemo: React.FC<AmethystDemoProps> = ({ stem }) => (
  <AbsoluteFill style={{ backgroundColor: color.surface }}>
    <ApplyPatch />
    <Analyze />
    <AgentReasoning />
    <AppAnalysis />
    <Treatment />
    <EndCard />
    {stem === "all" ? (
      <Audio name="music bed" src={staticFile(`audio/${timeline.id}-bed.wav`)} volume={0.9} />
    ) : null}
    <TimelineSfx timeline={timeline} />
  </AbsoluteFill>
);

export const amethystDemoComposition = {
  id: timeline.id,
  component: AmethystDemo,
  durationInFrames: durationInFrames(timeline),
  fps: timeline.fps,
  width: CANVAS.w,
  height: CANVAS.h,
  defaultProps: { stem: "all" } as AmethystDemoProps,
} as const;
