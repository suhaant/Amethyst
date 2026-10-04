# Amethyst film (Remotion)

**AmethystFilm** (45 s, 1920x1080, 60 fps) is the video for the slide. It has two parts:
- **AmethystIntro** (5 s): the patch glows, the crystal slams together, and the "amethyst" logo settles and slides out to the right.
- **AmethystDemo** (40 s): the arm sweeps in from the left, then Sense → Reason (the wound agent) → Alert (the app) → Treat → logo.

Where things live:
- The rendered film is [renders/AmethystFilm.mp4](renders/AmethystFilm.mp4).
- The intro's timing is in `src/projects/amethyst-intro/timeline.ts`.
- The demo's timing is in `src/timeline/amethyst-demo.ts` (90 bpm).
- Music and sound effects are synthesized in code by `scripts/`.
- The talk-over script is in [docs/video-script.md](docs/video-script.md).
- House rules are in [CLAUDE.md](CLAUDE.md).

```bash
npm i
npm run dev                       # Remotion Studio
npm run review -- AmethystDemo    # draft + contact sheet + pop scan + SFX sync
npx remotion render src/index.ts AmethystFilm out/AmethystFilm/AmethystFilm.mp4 --crf=14 --x264-preset=slow --image-format=png --audio-codec=aac --audio-bitrate=320k
```
