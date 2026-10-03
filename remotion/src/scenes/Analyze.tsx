import React from "react";
import { useCurrentFrame } from "remotion";
import { color } from "../brand/theme";
import { READING_W, readingCardPos } from "../components/amethyst/readingCard";
import { Stage, worldToCanvas } from "../components/amethyst/Stage";
import { PATCH_REST, armOffset, camera, patchState, shadowState, stageTracked } from "../components/amethyst/stagePose";
import { T, move } from "../components/amethyst/time";
import { RowsCard, StepHeader } from "../components/amethyst/ui";
import { readingRows } from "../data/assessment";
import { AdaptiveMotionBlur, speedFromPose } from "../studio/MotionBlur";
import { land } from "../studio/motion";

// 01 Sense. A still beat, then the pod light comes on (activation tone) and a
// violet line passes beneath the pad. The reading appears beside the patch:
// the five signals the agent takes (agent-reasoning: SensorReading), with the
// values of its sample reading. The patch then drops away and the reading
// card carries on into the agent diagram.

const FROM = T.cut("scene2");
const TO = T.cut("scene3");

const Shot: React.FC = () => {
  const f = useCurrentFrame() + FROM;
  const cam = camera(f);
  const [cx, cy] = readingCardPos(f);
  const pod = worldToCanvas(cam, PATCH_REST);
  const link = land(f, 60, T.start("readingCard") - 6, 24) * (1 - move(f, "patchOut"));
  const linkEnd: [number, number] = [cx, cy + 200];
  return (
    <>
      <Stage id="s2" cam={cam} armOffset={armOffset(f)} patch={patchState(f)} shadow={shadowState(f)} background={color.surface} />
      <StepHeader
        frame={f}
        step="01"
        name="Sense"
        lines={["Every few minutes, the patch takes", "one reading of five signals."]}
        start={T.start("senseHeader")}
        duration={T.len("senseHeader")}
        out={move(f, "senseOut")}
      />
      {link > 0.001 ? (
        <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
          <line
            x1={pod[0] + 150}
            y1={pod[1]}
            x2={pod[0] + 150 + (linkEnd[0] - pod[0] - 150) * link}
            y2={pod[1] + (linkEnd[1] - pod[1]) * link}
            stroke={color.inkMuted}
            strokeWidth={2}
            strokeDasharray="2 8"
            strokeLinecap="round"
          />
        </svg>
      ) : null}
      <RowsCard
        frame={f}
        title="Sensor reading"
        rows={readingRows}
        start={T.start("readingCard")}
        x={cx}
        y={cy}
        w={READING_W}
        open={move(f, "readingCard")}
      />
    </>
  );
};

const tracked = (f: number) => [...stageTracked(f), readingCardPos(f)];

export const Analyze: React.FC = () => (
  <AdaptiveMotionBlur name="01 Sense" from={FROM} durationInFrames={TO - FROM} speed={speedFromPose(tracked)}>
    <Shot />
  </AdaptiveMotionBlur>
);
