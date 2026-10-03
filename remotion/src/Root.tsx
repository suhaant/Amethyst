import { Composition } from "remotion";
import { amethystDemoComposition } from "./compositions/AmethystDemo";
import { amethystIntroComposition } from "./projects/amethyst-intro/AmethystIntro";
import { studioReadyComposition } from "./projects/studio-ready/StudioReady";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition {...amethystIntroComposition} />
      <Composition {...amethystDemoComposition} />
      <Composition {...studioReadyComposition} />
    </>
  );
};
