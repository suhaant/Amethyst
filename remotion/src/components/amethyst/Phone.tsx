import React from "react";
import { color, inter } from "../../brand/theme";
import { focusState, remainingAt } from "./appPose";
import { Device, ScreenOverlay, Shot, type View } from "./Device";
import { alertUI, screens, SCREEN, therapyShot } from "./screens";
import { mix, move, T } from "./time";

// The phone in 03 Alert / 04 Treat: the real alert screen, the app's own
// pressed state on the tap, then the real therapy screen opening out of the
// button, counting down second by second (one real capture per second).

const PRESS_FRAMES = 12;

export const Phone: React.FC<{ f: number; view: View; showFocus?: boolean }> = ({ f, view, showFocus = true }) => {
  const r = move(f, "therapyReveal");
  const [bx, by, bw, bh] = alertUI.button;
  const pressed = f >= T.cut("press") && f < T.cut("press") + PRESS_FRAMES;
  const therapyOn = f >= T.start("therapyReveal");
  const clip = {
    x: mix(bx, 0, r),
    y: mix(by, 0, r),
    w: mix(bw, SCREEN.w, r),
    h: mix(bh, SCREEN.h, r),
    r: mix(alertUI.buttonRadius, 44, r),
  };
  const { rect, dim } = focusState(f);
  const [hx, hy, hw, hh] = rect;
  return (
    <Device view={view}>
      {(k) => (
        <>
          {r < 1 ? <Shot src={screens.alert} k={k} /> : null}
          {pressed ? (
            <ScreenOverlay k={k}>
              <rect x={bx} y={by} width={bw} height={bh} rx={alertUI.buttonRadius} fill={color.brandDeep} />
              <text
                x={bx + bw / 2}
                y={by + bh / 2}
                textAnchor="middle"
                dominantBaseline="central"
                fontFamily={inter}
                fontWeight={600}
                fontSize={15}
                fill={color.onBrand}
              >
                Start therapy now
              </text>
            </ScreenOverlay>
          ) : null}
          {therapyOn ? <Shot src={therapyShot(remainingAt(f))} k={k} clip={r < 1 ? clip : undefined} /> : null}
          {showFocus && dim > 0.001 ? (
            <ScreenOverlay k={k}>
              <path
                d={`M0,0 H${SCREEN.w} V${SCREEN.h} H0 Z M${hx + 14},${hy} H${hx + hw - 14} Q${hx + hw},${hy} ${hx + hw},${hy + 14} V${hy + hh - 14} Q${hx + hw},${hy + hh} ${hx + hw - 14},${hy + hh} H${hx + 14} Q${hx},${hy + hh} ${hx},${hy + hh - 14} V${hy + 14} Q${hx},${hy} ${hx + 14},${hy} Z`}
                fillRule="evenodd"
                fill={color.surface}
                opacity={0.68 * dim}
              />
              <rect x={hx} y={hy} width={hw} height={hh} rx={14} fill="none" stroke={color.brand} strokeWidth={2.5} opacity={dim} />
            </ScreenOverlay>
          ) : null}
        </>
      )}
    </Device>
  );
};
