# Amethyst demo video (Remotion)

This folder holds the 30 s product explainer: 1920x1080, 60 fps.
The film runs Sense → Reason (the wound agent) → Alert (the app) → Treat → logo.

- All timing lives in `src/timeline/amethyst-demo.ts`.
- Music and sound effects are synthesized in code by `scripts/`.
- The talk-over script is in [docs/video-script.md](docs/video-script.md).
- House rules are in [CLAUDE.md](CLAUDE.md).

```bash
npm i
npm run dev                       # Remotion Studio
npm run review -- AmethystDemo    # draft + contact sheet + pop scan + SFX sync
npm run final -- AmethystDemo     # full-quality H.264 → out/AmethystDemo/AmethystDemo.mp4
```
