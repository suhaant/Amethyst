# Amethyst slide videos (Remotion)

This project makes the animated slides for the **Amethyst** hackathon pitch. Each slide is a 1920×1080, 30 fps Remotion composition. The finished MP4s (and a PNG still of each slide's final frame) get dropped into Canva, where the deck is presented.

Amethyst is both the company and the product: a smart wound patch that senses early infection (pH, moisture, temperature) and treats it with low-frequency ultrasound and 405 nm violet light. There is no other product name. Never write "PulsePatch".

Use the Remotion skills for all Remotion code (`/remotion-best-practices`).

## Brand rules (follow exactly)

- **Import brand values from `src/brand/theme.ts`** (`color`, `type`, `slide`, `motion`, fonts `inter` and `mono`) and the logo from `src/brand/Logo.tsx`. Never hard-code a hex value or font that isn't in theme.ts.
- **Light-first.** Slides sit on `color.surface` (white) with `color.ink` text. At most one slide may flip to a `color.brandDeep` ground with white text (the closing slide).
- **One accent.** `color.brand` (#6B3FA0) is spent on: the single number a slide is about, the Amethyst data line in a chart, and highlights. If more than ~10% of the frame is violet, pull back.
- **Type.** Inter only (SemiBold 600 headlines, Regular 400 body, Medium 500 labels); JetBrains Mono for sensor readings like "pH 7.8" or "40 kHz". Every slide has an `eyebrow` (uppercase, brand violet) above a `title`. Max ~25 words of body text per slide.
- **Layout.** 64px side margins, 56px top. Footer on every slide except the title: `AmethystMark` at 28px bottom-left, slide number in `inkMuted` bottom-right.
- **Logo.** The lockup is always the wordmark **then** the crystal on the right. Use `<AmethystLockup>` (or `public/brand/amethyst-lockup.svg` via `staticFile`). Never recolor the facets, never put the crystal on the left, never add gradients, glows or drop shadows to it.
- **Status colors** (`riskNormal`, `riskWarning`, `riskInfection` with their `-Bg` pairs) always come with a word and icon: "Normal", "Warning", "Infection". Never color alone.
- **Flat.** No gradients (especially no purple-to-blue), no glows, no glassmorphism, no emoji. Shapes are flat facets like the crystal.
- **Charts.** Amethyst data in `brand` at 3px; everything else `inkMuted` or `line`. Label axes; cite the source in `type.source` at the bottom of the slide.

## Motion rules

- Quick and precise: elements enter with a 6–10 frame fade + 24px rise using `spring({ config: motion.spring })` (no overshoot). Stagger lists by `motion.stagger` frames. Nothing bounces, spins or zooms.
- **Logo reveal:** facets appear one at a time in the order of `facets` in Logo.tsx (three terminal faces, then the base), ~4 frames apart, then the wordmark fades in.
- Every slide finishes animating by frame 150 (5 s) and then **holds still** until its end (frame 180), so the last frame works as a static slide and the presenter can talk over the hold.
- Numbers count up (interpolate) only for the one hero stat on a slide.

## Files

- `public/brand/` logos (SVG + PNG), `public/screens/` app screenshots (pair, home, alert, therapy, trends .png)
- `src/brand/tokens.json` full token list from the Amethyst design system
- `pitch-content.md` the approved words and numbers for each slide. **Use only these facts and figures; do not invent stats.**

## Output

- Compositions named `Slide1Title`, `Slide2Problem`, `Slide3Solution`, `Slide4Demo`, `Slide5Market`, `Slide6Plan`, each 180 frames.
- Render each to `out/<id>.mp4` (`npx remotion render <id> out/<id>.mp4`) and its last frame to `out/<id>.png` (`npx remotion still <id> out/<id>.png --frame=179`).
