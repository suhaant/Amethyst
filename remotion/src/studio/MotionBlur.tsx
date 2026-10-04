import { HtmlInCanvasMotionBlur } from "@remotion/motion-blur";
import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";

const SHUTTER_ANGLE = 180;

/**
 * Samples scale with how far things travel while the shutter is open:
 * still frames get 1 sample (sharp, cheap), the fastest moments get up to 64
 * (one sample per ~2px of smear, so the trail is smooth, not stepped).
 * The sampler centers the shutter on the frame, so changing the sample
 * count between frames never shifts time.
 */
export const samplesForSpeed = (pxPerFrame: number): number => {
  const smear = pxPerFrame * (SHUTTER_ANGLE / 360);
  if (smear < 1) {
    return 1;
  }
  return Math.min(64, Math.max(6, Math.ceil(smear / 2)));
};

/**
 * Motion blur for a whole layer. `speed(frame)` returns the fastest
 * on-screen point's velocity in px/frame, derived from the same pose
 * function that drives the picture.
 */
export const AdaptiveMotionBlur: React.FC<{
  /** Speed in px/frame at a parent-timeline frame. */
  readonly speed: (frame: number) => number;
  /**
   * Bound the layer to one shot. Samples are clamped to this range, so blur
   * never mixes frames from either side of a cut.
   */
  readonly from?: number;
  readonly durationInFrames?: number;
  readonly name?: string;
  readonly children: React.ReactNode;
}> = ({ speed, from, durationInFrames, name, children }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  return (
    <HtmlInCanvasMotionBlur
      width={width}
      height={height}
      from={from}
      durationInFrames={durationInFrames}
      name={name}
      shutterAngle={SHUTTER_ANGLE}
      samples={samplesForSpeed(speed(frame))}
    >
      {children}
    </HtmlInCanvasMotionBlur>
  );
};

/** Max displacement of any tracked point across one frame, centered on `frame`. */
export const speedFromPose =
  (pose: (frame: number) => readonly (readonly [number, number])[]) =>
  (frame: number): number => {
    const a = pose(frame - 0.5);
    const b = pose(frame + 0.5);
    let max = 0;
    for (let i = 0; i < a.length; i++) {
      max = Math.max(max, Math.hypot(b[i][0] - a[i][0], b[i][1] - a[i][1]));
    }
    return max;
  };
