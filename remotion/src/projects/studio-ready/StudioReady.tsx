import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { cueLength, cueStart, durationInFrames } from "../../studio/beats";
import { land, pushIn, stagger } from "../../studio/motion";
import { AdaptiveMotionBlur, speedFromPose } from "../../studio/MotionBlur";
import { TimelineSfx } from "../../studio/Sfx";
import { REELS, theme } from "../../studio/theme";
import { timeline as tl } from "./timeline";

const { fps } = tl;
const DOT = 176;
const FONT_SIZE = 108;
const WORDS = ["Studio", "ready"];
const WORD_GAP = 3; // frames
const LEFT = theme.safe.left;
const CENTER_Y = 860;
const RISE_FROM = REELS.height - CENTER_Y + DOT; // fully below frame
// Only used to estimate speed for blur sampling; layout is CSS-driven.
const PILL_EST_WIDTH = 800;

const pose = (frame: number) => {
  const rise = land(frame, fps, cueStart(tl, "rise"), cueLength(tl, "rise"));
  const stretch = land(
    frame,
    fps,
    cueStart(tl, "stretch"),
    cueLength(tl, "stretch"),
  );
  const words = WORDS.map((_, i) =>
    land(
      frame,
      fps,
      stagger(cueStart(tl, "words"), i, WORD_GAP),
      cueLength(tl, "words"),
    ),
  );
  const y = interpolate(rise, [0, 1], [RISE_FROM, 0]);
  return {
    y,
    stretch,
    words,
    camera: pushIn(frame, durationInFrames(tl)),
  };
};

// Squash and stretch from vertical speed: the dot elongates while it flies
// and relaxes as it lands. Area-preserving, so it never reads as a bounce.
const elongation = (frame: number) => {
  const vy = Math.abs(pose(frame + 0.5).y - pose(frame - 0.5).y);
  return 1 + Math.min(0.28, vy / 260);
};

const trackedPoints = (frame: number) => {
  const p = pose(frame);
  const right = LEFT + DOT + (PILL_EST_WIDTH - DOT) * p.stretch;
  return [
    [LEFT, CENTER_Y + p.y] as const,
    [right, CENTER_Y + p.y] as const,
    ...p.words.map((w) => [LEFT, (1 - w) * FONT_SIZE * 1.12 * 1.1] as const),
  ];
};

const Scene: React.FC = () => {
  const frame = useCurrentFrame();
  const p = pose(frame);
  const e = elongation(frame);

  return (
    <AbsoluteFill
      style={{
        transform: `scale(${p.camera})`,
        // Push in on the pill's center: the focal point once it has opened.
        transformOrigin: `${LEFT + PILL_EST_WIDTH / 2}px ${CENTER_Y}px`,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: LEFT,
          top: CENTER_Y - DOT / 2,
          height: DOT,
          display: "flex",
          alignItems: "center",
          paddingLeft: theme.space[6] - 4,
          paddingRight: theme.space[6] - 4,
          backgroundColor: theme.color.accent,
          borderRadius: DOT / 2,
          transform: `translateY(${p.y}px) scale(${1 / Math.sqrt(e)}, ${e})`,
          transformOrigin: `${DOT / 2}px 50%`,
          // Dot -> pill: reveal from the left, keeping a full circle at 0.
          clipPath: `inset(0 calc((100% - ${DOT}px) * ${1 - p.stretch}) 0 0 round ${DOT / 2}px)`,
        }}
      >
        <div
          style={{
            display: "flex",
            gap: "0.26em",
            overflow: "hidden",
            // Mask hugs the line so words rise out of the pill's center line.
            paddingBottom: "0.04em",
            fontFamily: theme.font,
            fontWeight: 600,
            fontSize: FONT_SIZE,
            lineHeight: 1.12,
            letterSpacing: "-0.025em",
            color: theme.color.paper,
            whiteSpace: "nowrap",
          }}
        >
          {WORDS.map((word, i) => (
            <span
              key={word}
              style={{
                display: "inline-block",
                transform: `translateY(${(1 - p.words[i]) * 110}%)`,
              }}
            >
              {word}
            </span>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const StudioReady: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: theme.color.paper }}>
    <AdaptiveMotionBlur speed={speedFromPose(trackedPoints)}>
      <Scene />
    </AdaptiveMotionBlur>
    <TimelineSfx timeline={tl} />
  </AbsoluteFill>
);

export const studioReadyComposition = {
  id: tl.id,
  component: StudioReady,
  durationInFrames: durationInFrames(tl),
  fps: tl.fps,
  width: REELS.width,
  height: REELS.height,
} as const;
