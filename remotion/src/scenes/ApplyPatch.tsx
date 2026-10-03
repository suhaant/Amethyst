import React from "react";
import { useCurrentFrame } from "remotion";
import { color } from "../brand/theme";
import { RiseText } from "../components/amethyst/RiseText";
import { Stage } from "../components/amethyst/Stage";
import { armOffset, camera, patchState, shadowState, stageTracked } from "../components/amethyst/stagePose";
import { T, move } from "../components/amethyst/time";
import { HEADER_TOP, MARGIN, text } from "../components/amethyst/ui";
import { AdaptiveMotionBlur, speedFromPose } from "../studio/MotionBlur";

// Hook. The arm sweeps in already moving on frame 0 and lands soft; the
// patch floats in on its own arc, eases down and sticks on beat 4 (contact),
// compresses and settles. One line frames the story (pitch-content.md,
// slide 3 title), then a macro move levels onto the patch.

const FROM = T.cut("scene1");
const TO = T.cut("scene2");

const Shot: React.FC = () => {
  const f = useCurrentFrame() + FROM;
  return (
    <>
      <Stage id="s1" cam={camera(f)} armOffset={armOffset(f)} patch={patchState(f)} shadow={shadowState(f)} background={color.surface} />
      <div style={{ position: "absolute", left: MARGIN, top: HEADER_TOP + 30 }}>
        <RiseText
          frame={f}
          lines={["A patch that senses,", "predicts, and treats."]}
          start={T.start("intro")}
          duration={T.len("intro")}
          out={move(f, "introOut")}
          style={{ ...text.headline, fontSize: 64 }}
        />
      </div>
    </>
  );
};

export const ApplyPatch: React.FC = () => (
  <AdaptiveMotionBlur name="Hook · apply" from={FROM} durationInFrames={TO - FROM} speed={speedFromPose(stageTracked)}>
    <Shot />
  </AdaptiveMotionBlur>
);
