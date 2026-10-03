import React from "react";
import { useCurrentFrame } from "remotion";
import { color } from "../brand/theme";
import { phoneView, viewTracked } from "../components/amethyst/appPose";
import { toCanvas } from "../components/amethyst/Device";
import { Phone } from "../components/amethyst/Phone";
import { alertUI } from "../components/amethyst/screens";
import { T, mix, move } from "../components/amethyst/time";
import { COMPACT_H, Captions, StepHeader, text } from "../components/amethyst/ui";
import { prob } from "../data/assessment";
import { AdaptiveMotionBlur, speedFromPose } from "../studio/MotionBlur";
import { land } from "../studio/motion";
import { COL_C } from "./AgentReasoning";

// 03 Alert. The assessment card (rolled up to its probability) shrinks into
// the app's own risk-score card as the phone slides in. Focus walks the real
// alert screen: status, then the score with every signal the agent read,
// then the disclaimer and the one-tap "Start therapy now" (real tap: tick).

const FROM = T.cut("scene4");
const TO = T.cut("scene5");

const cardRect = (f: number) => {
  const t = move(f, "cardToPhone");
  const v = phoneView(f);
  const [rx, ry, rw, rh] = alertUI.riskCard;
  const [x1, y1] = toCanvas(v, [rx, ry]);
  return {
    x: mix(COL_C.x, x1, t),
    y: mix(COL_C.y, y1, t),
    w: mix(COL_C.w, rw * v.k, t),
    h: mix(COMPACT_H, rh * v.k, t),
    t,
  };
};

const Shot: React.FC = () => {
  const f = useCurrentFrame() + FROM;
  const c = cardRect(f);
  const s = c.w / COL_C.w;
  const morphing = f < T.end("cardToPhone");
  return (
    <>
      <StepHeader
        frame={f}
        step="03"
        name="Alert"
        lines={["The app turns the assessment into", "an alert the patient can act on."]}
        start={T.start("alertHeader")}
        duration={T.len("alertHeader")}
        out={land(f, 60, T.beat(44), 24)}
      />
      <Captions
        frame={f}
        items={[
          { start: T.start("focusStatus"), end: T.start("focusScore") - 6, lines: ["Status: Warning.", "Infection risk is rising."] },
          { start: T.start("focusScore"), end: T.start("focusButton") - 6, lines: ["Risk score 82 / 100, with all", "five signals the agent read."] },
          { start: T.start("focusButton"), end: T.beat(44), lines: ["An early warning, not a diagnosis.", "One tap starts therapy."] },
        ]}
      />
      <Phone f={f} view={phoneView(f)} />
      {morphing ? (
        <div
          style={{
            position: "absolute",
            left: c.x,
            top: c.y,
            width: c.w,
            height: c.h,
            borderRadius: mix(24, 12 * 1.18, c.t),
            backgroundColor: color.surfaceRaised,
            overflow: "hidden",
          }}
        >
          <div style={{ width: COL_C.w, transform: `scale(${s})`, transformOrigin: "0 0", padding: "26px 32px", boxSizing: "border-box" }}>
            <div style={{ ...text.label, color: color.ink, fontWeight: 600 }}>Assessment</div>
            <div style={{ height: 14 }} />
            <div style={{ height: 62, display: "flex", alignItems: "center", justifyContent: "space-between", borderTop: `1px solid ${color.line}` }}>
              <span style={text.label}>Infection probability</span>
              <span style={{ ...text.value, color: color.brand }}>{prob}</span>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
};

const tracked = (f: number): [number, number][] => {
  const c = cardRect(f);
  return [...viewTracked(phoneView(f)), [c.x, c.y], [c.x + c.w, c.y + c.h]];
};

export const AppAnalysis: React.FC = () => (
  <AdaptiveMotionBlur name="03 Alert" from={FROM} durationInFrames={TO - FROM} speed={speedFromPose(tracked)}>
    <Shot />
  </AdaptiveMotionBlur>
);
