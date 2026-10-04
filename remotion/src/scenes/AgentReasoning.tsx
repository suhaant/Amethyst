import React from "react";
import { useCurrentFrame } from "remotion";
import { color } from "../brand/theme";
import { READING_W, REASON_POS } from "../components/amethyst/readingCard";
import { RiseText } from "../components/amethyst/RiseText";
import { FPS, T, fr, move } from "../components/amethyst/time";
import { RowsCard, StepHeader, text } from "../components/amethyst/ui";
import { plan, prob, readingRows, threshold } from "../data/assessment";
import { AdaptiveMotionBlur, speedFromPose } from "../studio/MotionBlur";
import { land } from "../studio/motion";

// 02 Reason. How the wound agent (WolfHacks agent-reasoning, wound_agent/
// agent.py) works, exactly as the code does it:
//   reading -> Gemini agent calls get_sensor_reading -> predict_infection
//   (infection model -> probability vs threshold) -> plan_treatment (dose band)
//   -> the agent judges the evidence (its system prompt) -> Assessment.
// The agent never produces a number; the assessment card only fills in as
// each tool returns. Values are the agent's offline sample run.

const FROM = T.cut("scene3");
const TO = T.cut("scene4");

const COL_B = { x: 760, y: 380, w: 520 };
export const COL_C = { x: 1340, y: 380, w: 460 };

const TOOLS = [
  { cue: "tool1", call: "get_sensor_reading()", result: "Fetches the patch reading" },
  { cue: "tool2", call: "predict_infection()", result: `Infection model → ${prob} (threshold ${threshold})` },
  { cue: "tool3", call: "plan_treatment()", result: `Dose band → ${plan.band}` },
] as const;

const CHECKS = [
  "Checks each value for sensor faults",
  "Flags signals that disagree with the model",
  "Decides if a clinician should review",
  "Rates its confidence",
];

/** Which step is the focal point right now (0..3), for the accent bar. */
const activeStep = (f: number) =>
  f >= T.start("judge") ? 3 : f >= T.start("tool3") ? 2 : f >= T.start("tool2") ? 1 : 0;

const Arrow: React.FC<{ x1: number; x2: number; y: number; p: number }> = ({ x1, x2, y, p }) => {
  const x = x1 + (x2 - x1) * p;
  return p <= 0.001 ? null : (
    <g stroke={color.inkMuted} strokeWidth={2.5} strokeLinecap="round" fill="none">
      <line x1={x1} y1={y} x2={x} y2={y} />
      <path d={`M ${x - 9},${y - 8} L ${x},${y} L ${x - 9},${y + 8}`} opacity={p > 0.6 ? 1 : 0} />
    </g>
  );
};

const AgentPanel: React.FC<{ f: number; exit: number }> = ({ f, exit }) => {
  const open = move(f, "agentIn");
  const step = activeStep(f);
  const toolTop = (i: number) => 88 + i * 98;
  const barY = step < 3 ? toolTop(step) : 88 + 3 * 98 + 6;
  const barH = step < 3 ? 80 : 50 + CHECKS.length * 37;
  const barP = land(f, FPS, [T.start("tool1"), T.start("tool2"), T.start("tool3"), T.start("judge")][step], fr(24));
  return (
    <div
      style={{
        position: "absolute",
        left: COL_B.x - exit * 1100,
        top: COL_B.y,
        width: COL_B.w,
        height: 630,
        borderRadius: 24,
        border: `2px solid ${color.line}`,
        boxSizing: "border-box",
        padding: "26px 32px",
        clipPath: `inset(0 0 ${(1 - open) * 100}% 0 round 24px)`,
        backgroundColor: color.surface,
      }}
    >
      <RiseText frame={f} lines={["Gemini agent"]} start={T.start("agentIn")} duration={fr(30)} style={{ ...text.label, color: color.ink, fontWeight: 600 }} />
      {/* Accent bar marks the one step being explained. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: barY,
          width: 5,
          height: barH * barP,
          backgroundColor: color.brand,
          borderRadius: 3,
          opacity: f >= T.start("tool1") ? 1 : 0,
        }}
      />
      {TOOLS.map((t, i) => (
        <div key={t.call} style={{ position: "absolute", left: 32, top: toolTop(i), width: COL_B.w - 64 }}>
          <RiseText frame={f} lines={[t.call]} start={T.start(t.cue)} duration={T.len(t.cue)} style={{ ...text.code, color: step === i ? color.brand : color.ink }} />
          <div style={{ height: 8 }} />
          <RiseText frame={f} lines={[t.result]} start={T.start(t.cue) + fr(10)} duration={T.len(t.cue)} style={{ ...text.label, fontSize: 22 }} />
        </div>
      ))}
      <div style={{ position: "absolute", left: 32, top: 88 + 3 * 98 + 6, width: COL_B.w - 64 }}>
        <RiseText frame={f} lines={["Then it judges the evidence:"]} start={T.start("judge")} duration={T.len("judge")} style={{ ...text.label, color: color.ink, fontWeight: 600, fontSize: 23 }} />
        <div style={{ height: 10 }} />
        <RiseText frame={f} lines={CHECKS.map((c) => `✓  ${c}`)} start={T.start("judge") + fr(8)} duration={T.len("judge")} stagger={fr(4)} style={{ ...text.label, fontSize: 22, lineHeight: "37px" }} />
      </div>
    </div>
  );
};

const Shot: React.FC = () => {
  const f = useCurrentFrame() + FROM;
  const exit = move(f, "reasonOut");
  const t2 = T.start("tool2");
  const t3 = T.start("tool3");
  const assessmentRows = [
    { label: "Infection probability", value: prob, at: t2 + fr(14) },
    { label: "Infection detected", value: "yes", at: t2 + fr(18) },
    { label: "Dose band", value: plan.band, at: t3 + fr(14) },
    { label: "Violet light", value: `${plan.violet_light_minutes} min`, at: t3 + fr(18) },
    { label: "Ultrasound", value: `${plan.ultrasound_frequency_khz} kHz · ${plan.ultrasound_minutes} min`, at: t3 + fr(22) },
    { label: "Sessions", value: `${plan.sessions_per_day} / day`, at: t3 + fr(26) },
  ];
  return (
    <>
      <StepHeader
        frame={f}
        step="02"
        name="Reason"
        lines={["An AI agent works through three tools. It never", "makes up the probability or the dose."]}
        start={T.start("reasonHeader")}
        duration={T.len("reasonHeader")}
        out={exit}
        width={1200}
      />
      <div style={{ position: "absolute", inset: 0, transform: `translateX(${-exit * 1100}px)` }}>
        <RowsCard frame={f} title="Sensor reading" rows={readingRows} start={-999} x={REASON_POS[0]} y={REASON_POS[1]} w={READING_W} open={1} />
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, transform: `translateX(${-exit * 1100}px)` }}>
        <Arrow x1={REASON_POS[0] + READING_W + 8} x2={COL_B.x - 10} y={REASON_POS[1] + 200} p={land(f, FPS, T.start("tool1"), fr(22))} />
        <Arrow x1={COL_B.x + COL_B.w + 8} x2={COL_C.x - 10} y={REASON_POS[1] + 200} p={land(f, FPS, T.start("tool2") + fr(6), fr(22))} />
      </svg>
      <AgentPanel f={f} exit={exit} />
      <RowsCard
        frame={f}
        title="Assessment"
        rows={assessmentRows.map((r) => ({ ...r, at: r.at }))}
        start={t2}
        x={COL_C.x}
        y={COL_C.y}
        w={COL_C.w}
        open={move(f, "tool2")}
        accentRow={0}
        collapse={exit}
        footer={{ lines: ["Doses are placeholders pending", "clinical sign-off."], at: T.start("judge") + fr(24) }}
      />
    </>
  );
};

const tracked = (f: number): [number, number][] => {
  const x = -move(f, "reasonOut") * 1100;
  return [
    [REASON_POS[0] + x, REASON_POS[1]],
    [COL_B.x + x, COL_B.y],
  ];
};

export const AgentReasoning: React.FC = () => (
  <AdaptiveMotionBlur name="02 Reason" from={FROM} durationInFrames={TO - FROM} speed={speedFromPose(tracked)}>
    <Shot />
  </AdaptiveMotionBlur>
);
