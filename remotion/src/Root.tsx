import { Composition } from "remotion";
import { amethystDemoComposition } from "./compositions/AmethystDemo";
import { studioReadyComposition } from "./projects/studio-ready/StudioReady";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition {...amethystDemoComposition} />
      <Composition {...studioReadyComposition} />
    </>
  );
};
