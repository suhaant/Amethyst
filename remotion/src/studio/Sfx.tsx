import { Audio } from "@remotion/media";
import React from "react";
import { staticFile } from "remotion";
import { beatToFrame, type Timeline } from "./beats";

/** Every hit in the timeline, each starting on its exact frame. */
export const TimelineSfx: React.FC<{ readonly timeline: Timeline }> = ({
  timeline,
}) => (
  <>
    {timeline.hits.map((hit) => (
      <Audio
        key={`${hit.name}-${hit.at}`}
        name={`sfx: ${hit.name}`}
        from={beatToFrame(timeline, hit.at)}
        src={staticFile(`sfx/${hit.sfx}`)}
        volume={hit.volume ?? 1}
      />
    ))}
  </>
);
