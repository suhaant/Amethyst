import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { color } from "../brand/theme";
import { AmethystLockup } from "../brand/Logo";
import { heroView, remainingAt, viewTracked } from "../components/amethyst/appPose";
import { Device, Shot } from "../components/amethyst/Device";
import { RiseText } from "../components/amethyst/RiseText";
import { therapyShot } from "../components/amethyst/screens";
import { Stage } from "../components/amethyst/Stage";
import { armOffset, camera, patchState, shadowState, stageTracked } from "../components/amethyst/stagePose";
import { T } from "../components/amethyst/time";
import { MARGIN, text } from "../components/amethyst/ui";
import { AdaptiveMotionBlur, speedFromPose } from "../studio/MotionBlur";

// Brand resolution. The camera pulls back from the breathing patch, the real
// therapy screen (still counting) returns beside it, the crystal builds facet
// by facet (Logo.tsx order), the wordmark follows once the mark has landed,
// then the approved closing line (pitch-content.md, slide 1). Settles by
// ~1.25s before the end; the camera keeps a near-still push.

const FROM = T.cut("scene6");
const TO = 1800;
const FACET_GAP = 4;
const FACET_IN = 8;

const Shot6: React.FC = () => {
  const f = useCurrentFrame() + FROM;
  const facetOpacity = Array.from({ length: 6 }, (_, i) =>
    interpolate(f, [T.start("mark") + i * FACET_GAP, T.start("mark") + i * FACET_GAP + FACET_IN], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  const wordOpacity = interpolate(f, [T.start("wordmark"), T.start("wordmark") + 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <>
      <Stage id="s6" cam={camera(f)} armOffset={armOffset(f)} patch={patchState(f)} shadow={shadowState(f)} background={color.surface} />
      <Device view={heroView(f)}>{(k) => <Shot src={therapyShot(remainingAt(f))} k={k} />}</Device>
      <div style={{ position: "absolute", left: MARGIN, top: 200 }}>
        <AmethystLockup height={128} facetOpacity={facetOpacity} wordOpacity={wordOpacity} />
      </div>
      <div style={{ position: "absolute", left: MARGIN, top: 390, width: 900 }}>
        <RiseText
          frame={f}
          lines={["Smart wound care that catches", "infection early and treats it", "on the spot."]}
          start={T.start("closingLine")}
          duration={T.len("closingLine")}
          style={{ ...text.body, fontSize: 46, lineHeight: 1.18 }}
        />
      </div>
    </>
  );
};

export const EndCard: React.FC = () => (
  <AdaptiveMotionBlur
    name="Logo"
    from={FROM}
    durationInFrames={TO - FROM}
    speed={speedFromPose((f) => [...stageTracked(f), ...viewTracked(heroView(f))])}
  >
    <Shot6 />
  </AdaptiveMotionBlur>
);
