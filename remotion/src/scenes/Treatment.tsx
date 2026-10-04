import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { color } from "../brand/theme";
import { phoneView, remainingAt, viewTracked } from "../components/amethyst/appPose";
import { toCanvas } from "../components/amethyst/Device";
import { Phone } from "../components/amethyst/Phone";
import { therapyProgress, therapyUI } from "../components/amethyst/screens";
import { POD, Stage, worldToCanvas } from "../components/amethyst/Stage";
import { PATCH_REST, armOffset, camera, patchState, shadowState, stageTracked } from "../components/amethyst/stagePose";
import { FPS, T, fr, mix } from "../components/amethyst/time";
import { Captions, StepHeader } from "../components/amethyst/ui";
import { plan } from "../data/assessment";
import { AdaptiveMotionBlur, speedFromPose } from "../studio/MotionBlur";
import { land } from "../studio/motion";

// 04 Treat. The therapy screen runs live (real per-second captures). Focus:
// the countdown ring, then the agent's plan as the app shows it. Then the
// app's ring leaves the phone and lands on the pod while the patch rises
// back in; on the warm hit the patch starts its slow violet breathing.

const FROM = T.cut("scene5");
const TO = T.cut("scene6");

const ringT = (f: number) =>
  interpolate(f, [T.start("ringToPatch"), T.end("ringToPatch")], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const ringGeometry = (f: number) => {
  const v = phoneView(f);
  const cam = camera(f);
  const t = ringT(f);
  const c0 = toCanvas(v, [therapyUI.ring.cx, therapyUI.ring.cy]);
  const c1 = worldToCanvas(cam, PATCH_REST);
  return {
    c: [mix(c0[0], c1[0], t), mix(c0[1], c1[1], t)] as [number, number],
    r: mix(therapyUI.ring.r * v.k, POD.ring * cam.scale, t),
    w: mix(therapyUI.ring.stroke * v.k, 8 * cam.scale, t),
    progress: mix(therapyProgress(remainingAt(f)), 1, t),
  };
};

const Shot: React.FC = () => {
  const f = useCurrentFrame() + FROM;
  const stageOn = f >= T.start("ringToPatch");
  const carrying = stageOn && f < T.end("ringToPatch");
  const g = ringGeometry(f);
  const circ = 2 * Math.PI * g.r;
  return (
    <>
      {stageOn ? (
        <Stage id="s5" cam={camera(f)} armOffset={armOffset(f)} patch={patchState(f)} shadow={shadowState(f)} background={color.surface} />
      ) : null}
      <StepHeader
        frame={f}
        step="04"
        name="Treat"
        lines={["Ultrasound breaks up biofilm. Violet", "light kills bacteria. No drugs."]}
        start={T.start("treatHeader")}
        duration={T.len("treatHeader")}
        out={land(f, FPS, T.beat(54.25), fr(24))}
      />
      <Captions
        frame={f}
        items={[
          { start: T.start("focusTimer"), end: T.start("focusPlan") - fr(6), lines: ["405 nm violet light is running.", "The countdown is live in the app."] },
          {
            start: T.start("focusPlan"),
            end: T.start("ringToPatch") - fr(12),
            lines: [
              `The agent's plan: ${plan.ultrasound_frequency_khz} kHz ultrasound`,
              `for ${plan.ultrasound_minutes} min, then ${plan.violet_light_minutes} min of violet light,`,
              `${plan.sessions_per_day} sessions a day.`,
            ],
          },
        ]}
      />
      {f < T.end("ringToPatch") ? <Phone f={f} view={phoneView(f)} /> : null}
      {carrying ? (
        <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
          <circle cx={g.c[0]} cy={g.c[1]} r={g.r} fill="none" stroke={color.line} strokeWidth={g.w} />
          <circle
            cx={g.c[0]}
            cy={g.c[1]}
            r={g.r}
            fill="none"
            stroke={color.brand}
            strokeWidth={g.w}
            strokeLinecap="round"
            strokeDasharray={`${circ * g.progress} ${circ}`}
            transform={`rotate(-90 ${g.c[0]} ${g.c[1]})`}
          />
        </svg>
      ) : null}
    </>
  );
};

const tracked = (f: number) => {
  const g = ringGeometry(f);
  return [...viewTracked(phoneView(f)), ...stageTracked(f), g.c, [g.c[0] + g.r, g.c[1]] as const];
};

export const Treatment: React.FC = () => (
  <AdaptiveMotionBlur name="04 Treat" from={FROM} durationInFrames={TO - FROM} speed={speedFromPose(tracked)}>
    <Shot />
  </AdaptiveMotionBlur>
);
