import { mixPt, move } from "./time";

// The sensor-reading card is one object that travels from the patch (01 Sense)
// into the agent diagram (02 Reason).
export const READING_W = 560;
const SENSE_POS: [number, number] = [1240, 330];
export const REASON_POS: [number, number] = [120, 380];

export const readingCardPos = (f: number): [number, number] =>
  mixPt(SENSE_POS, REASON_POS, move(f, "handoff"));
