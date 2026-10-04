# Amethyst film: talk-over script (45 s)

This is for `AmethystFilm`: the 5 s logo intro, then the 40 s demo. The output file is `out/AmethystFilm/AmethystFilm.mp4`.

- The intro runs on its own timeline: `src/projects/amethyst-intro/timeline.ts`.
- The demo is timed in `src/timeline/amethyst-demo.ts` at 90 bpm, so one beat is 0.667 s.
- Speaking pace is about 2.5 words per second.
- **Bold** words should land on the cue in the right-hand column.

| Time | On screen | Say |
| --- | --- | --- |
| 0:00 – 0:05 | Patch glows, the crystal slams together, the "amethyst" logo settles, then slides out right | *(let it play, or)* "We're **Amethyst**." |
| 0:05 – 0:10 | The arm sweeps in from the left; the patch floats down and sticks | "This is a smart patch that senses, predicts, and **treats** wound infection." |
| 0:10 – 0:16 | **01 Sense**: pod lights up, reading card | "Every few minutes it takes **one reading of five signals**: pH, moisture, temperature, heart rate, and glucose variability." |
| 0:16 – 0:27 | **02 Reason**: the agent calls three tools | "That reading goes to our Gemini agent. It runs our **infection model** (82 percent here), then **picks a dose**. Last, it **checks its own work**: sensor faults, conflicting signals, and whether a clinician should look." |
| 0:27 – 0:35 | **03 Alert**: phone shows the warning, risk score, tap | "The app turns that into an alert the patient can act on: a risk score of 82, every signal behind it, and **one tap** to start therapy." |
| 0:35 – 0:42 | **04 Treat**: countdown, plan, ring moves to the patch, patch glows | "Ultrasound breaks up the biofilm, then **violet light** kills the bacteria. No drugs." |
| 0:42 – 0:45 | Logo with the therapy screen | "**Amethyst**: caught early, treated on the spot." |

## Sync points

| Time | Event on screen | Word that lands there |
| --- | --- | --- |
| 0:01.8 | Crystal slams together (low hit) | *(intro)* |
| 0:04.4 | Logo starts sliding out (whoosh) | "Amethyst" |
| 0:07.7 | Patch sticks (contact sound) | "treats" |
| 0:11.3 | Pod lights up (activation tone) | "one reading of five signals" |
| 0:19.0 | `predict_infection()` shows 0.82 | "infection model" |
| 0:21.0 | `plan_treatment()` shows the dose band | "picks a dose" |
| 0:23.0 | Agent checks the evidence | "checks its own work" |
| 0:33.0 | "Start therapy now" is tapped (click) | "one tap" |
| 0:39.3 | Patch glows violet (warm hit) | "violet light" |
| 0:42.3 | Logo lands (resolve) | "Amethyst" |

The demo by itself (`AmethystDemo`, 40 s, no intro) uses the same table minus 5 seconds.

## Shorter version (one speaker, relaxed pace)

> "Amethyst is a smart patch. It reads five signals from the wound. Our AI agent runs the infection model and picks a dose. The app alerts the patient, one tap starts therapy, and ultrasound plus violet light treat it. No drugs."

## Numbers, if a judge asks

| Item | Value |
| --- | --- |
| Five signals | pH 7.3, moisture 68%, wound temp +2.3 °C vs skin, heart rate 94 bpm, glucose variability 31.5% |
| Infection probability | 0.82 (threshold 0.50), so a risk score of 82/100 |
| Plan, moderate band | Violet light 405 nm for 15 min, ultrasound 35 kHz for 7 min, 2 sessions a day |

The doses are placeholders pending clinical sign-off. The video shows this, so don't present them as validated.
