# Amethyst demo video: talk-over script (30 s)

Times come from `src/timeline/amethyst-demo.ts` (120 bpm, so 1 beat = 0.5 s).
Speaking pace is about 2.7 words per second. **Bold** words land on the cue in the right-hand column.

| Time | On screen | Say |
| --- | --- | --- |
| 0:00 – 0:04 | Hand places the patch on the arm | "This is **Amethyst**, a smart patch that senses, predicts, and treats." |
| 0:04 – 0:08.5 | **01 Sense**: pod lights up, reading card | "Every few minutes it reads **five signals** from the wound: pH, temperature, moisture, and more." |
| 0:08.5 – 0:16.5 | **02 Reason**: agent calls three tools | "Our Claude agent takes that reading, runs our **infection model** (82 percent), **picks a dose**, then **checks its own work** for bad sensor data." |
| 0:16.5 – 0:22.5 | **03 Alert**: phone shows the warning | "The app turns that into a simple alert, risk score 82, and **one tap** starts therapy." |
| 0:22.5 – 0:27.5 | **04 Treat**: ring moves to the patch, patch glows | "Ultrasound breaks up the biofilm, **violet light** kills the bacteria. No drugs." |
| 0:27.5 – 0:30 | Logo | "**Amethyst**: caught early, treated on the spot." |

## Sync points

| Time | Event on screen | Word that lands there |
| --- | --- | --- |
| 0:02.0 | Patch sticks (contact sound) | "Amethyst" |
| 0:04.75 | Pod lights up (activation tone) | "five signals" |
| 0:10.5 | `predict_infection()` shows 0.82 | "infection model" |
| 0:12.0 | `plan_treatment()` shows the dose band | "picks a dose" |
| 0:13.5 | Agent checks the evidence | "checks its own work" |
| 0:21.0 | "Start therapy now" is tapped (click) | "one tap" |
| 0:25.75 | Patch glows violet (warm hit) | "violet light" |
| 0:28.0 | Logo lands (resolve) | "Amethyst" |

## Shorter version (one speaker, relaxed pace)

> "Amethyst is a smart patch. It reads five signals from the wound. Our AI agent runs the infection model and picks a dose. The app alerts the patient, one tap starts therapy, and ultrasound plus violet light treat it. No drugs."

## Numbers, if a judge asks

| Item | Value |
| --- | --- |
| Five signals | pH 7.3, moisture 68%, wound temp +2.3 °C vs skin, heart rate 94 bpm, glucose variability 31.5% |
| Infection probability | 0.82 (threshold 0.50), so a risk score of 82/100 |
| Plan, moderate band | Violet light 405 nm for 15 min, ultrasound 35 kHz for 7 min, 2 sessions a day |

The doses are placeholders pending clinical sign-off. The video shows this, so don't present them as validated.
