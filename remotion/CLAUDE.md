# Motion studio rules

## Render contract
- Every frame is a pure function of the frame number (useCurrentFrame). No Date.now, timers, requestAnimationFrame, CSS animations/transitions, or unseeded randomness — use Remotion's random(seed).
- All motion comes from spring()/interpolate() computed from the frame, so any frame renders on its own.
- Default 1080x1920 (Reels) unless I say otherwise, 60 fps, H.264, high quality.
- Motion blur on fast moves (@remotion/motion-blur); more samples on the fastest moments.
- All timing lives in one timeline file written in beats. Picture and sound both read it.
- Render a low-res draft before any full render.

## Look — ban the defaults
- No centered text on a gradient, no "everything fades in", no glow, glassmorphism, particles, bounce easing, or template SaaS look.
- One accent color, one type family, consistent spacing.
- Arrive fast, land soft. Nothing moves at constant speed or dead-stops; holds keep a slow push-in so nothing freezes.
- Moves last at least 0.3s (big moves 0.5–0.75s). Stagger grouped elements 2–4 frames.
- Text holds still at least 8 frames before moving. One focal point per frame.
- Cuts land on the beat or 2 frames early. Prefer morphs and match cuts over fades.
- Never invent product UI, numbers, claims, or testimonials. Use real screenshots and assets in ./assets.

## Sound
- No voiceover unless I ask. Music and SFX are synthesized in code, or come from ./assets/audio.
- Write beats.json (bpm, beats, downbeats, hits) and time the animation to it.
- Each SFX lands on the exact frame of its action: click on press, whoosh on morph, low hit on the logo.

## Loop before you show me anything
- Render one frame per beat into a contact sheet and look at it.
- Score 1–10 on: hook, readability at phone size, motion quality, variety, brand accuracy, sound sync.
- Fix the three worst problems, re-render, and repeat (up to 3 rounds) until everything is 8+. Report scores each round.
- Scan the final video for single-frame pops and fix them before the final render.

---

## How this studio is wired (use these, don't reinvent them)

- `src/projects/<name>/timeline.ts` — the one timing file per piece: `bpm`, `fps`, `cues` (`at`/`beats`, in beats) and `hits` (SFX on beats). Type-only imports; Node loads it directly.
- `src/projects/<name>/<Name>.tsx` — the composition. Compute a pure `pose(frame)` from cues and draw from it. Register it in `src/Root.tsx`.
- `src/studio/beats.ts` — beat→frame math and the `beats.json` shape.
- `src/studio/motion.ts` — `land()` (critically damped spring: arrive fast, land soft), `pushIn()`, `stagger()`.
- `src/studio/MotionBlur.tsx` — `AdaptiveMotionBlur` + `speedFromPose()`: samples scale with on-screen speed (1 when still, up to 64 at the fastest), shutter centered on the frame.
- `src/studio/Sfx.tsx` — `TimelineSfx` places every timeline hit on its exact frame.
- `src/studio/theme.ts` — the one accent, one family (Instrument Sans), spacing scale, Reels safe margins, `REELS` (1080x1920 @ 60).
- SFX are synthesized deterministically by `scripts/studio.mjs` into `public/sfx` (beep, click, whoosh, low-hit); files in `assets/audio` are copied alongside.

### Commands
- `npm run review -- <Id>` — draft (540x960) → `out/<Id>/contact.png` (one frame per beat) → pop scan → SFX sync check. Run this every round.
- `npm run final -- <Id>` — full-quality render to `out/<Id>/<Id>.mp4` (H.264, CRF 14, slow preset, PNG frames, AAC 320k).
- `npm run still -- <Id> <frame> [out.png]` — single PNG frame.
- `npm run popscan -- <video>` / `npm run sync -- <Id> [video]` — run checks on any render.
- `npm run dev` — Remotion Studio. Motion blur preview needs Chrome with `chrome://flags/#canvas-draw-element`; renders need nothing extra.

### Gotchas
- Remotion's bundled ffmpeg (`npx remotion ffmpeg`) is a minimal build without select/tile/drawtext; the review tools use `ffmpeg-static` instead.
- Keep SFX attacks ≤1 ms so the onset lands on the frame the hit is placed on.
- `@remotion/google-fonts` fetches the font at render time (needs network). Vendor it into `assets/` if offline renders are needed.
