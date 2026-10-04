import { Composition } from "remotion";
import { amethystDemoComposition } from "./compositions/AmethystDemo";
import { amethystFilmComposition } from "./compositions/AmethystFilm";
import { amethystIntroComposition } from "./projects/amethyst-intro/AmethystIntro";
import { studioReadyComposition } from "./projects/studio-ready/StudioReady";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition {...amethystFilmComposition} />
      <Composition {...amethystIntroComposition} />
      <Composition {...amethystDemoComposition} />
      <Composition {...studioReadyComposition} />
    </>
  );
};
