# Wound temperature vs bacterial infection — extracted data

Evidence: H = human clinical, A = animal, B = bench. "secondary" = number seen via review/snippet only.

| Value | Context | Type | Source |
|---|---|---|---|
| Centre 28.66±1.90 °C (non-infected) vs 29.04±1.66 °C (colonized); surrounding skin 29.92±1.46 °C. No significant diff colonized vs not | 117 chronic-wound pts, probe ±0.5 °C | H | https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/ |
| Healthy contralateral asymmetry 0.3–0.4 °C | Normal bilateral symmetry (noise floor) | H secondary | https://www.researchgate.net/publication/216015612 |
| Non-infected wound +1.1–1.2 °C; inflammation +1.5–2.2 °C; infection +4–5 °C; after antibiotics +0.8–1.1 °C | Chanmugam 2017, LWIR, n=6 | H | https://pubmed.ncbi.nlm.nih.gov/28817451/ |
| >2 °F (1.1 °C) periwound vs contralateral associated with infection (F=44.24, P<.001) | Fierheller & Sibbald 2010, 40 ulcers | H | https://dx.doi.org/10.1097/01.ASW.0000383197.28192.98 |
| ≥3 °F (1.7 °C) vs mirror site, >8× likelihood deep infection (STONEES, needs ≥2 other signs) | Sibbald 2015 | H secondary | https://doi.org/10.1097/01.ASW.0000458991.58947.6b |
| ΔT 2.15 °C cutoff: sens 88.9%, spec 61.5%, AUC 0.846 | Diabetic foot infection n=52 vs 45 | H | https://pubmed.ncbi.nlm.nih.gov/32812820/ |
| 2.2 °C: sens 76%, spec 40%; 1.35 °C whole-foot mean: sens 89%, spec 78% | van Netten 2014, n=54 | H | https://pubmed.ncbi.nlm.nih.gov/25098361/ |
| Infected vs contralateral ~1.6 °C (very high variance); little change after 11.7 d antibiotics | SIDESTEP, n=332 | H | https://pmc.ncbi.nlm.nih.gov/articles/PMC7951616/ |
| Bacteria present +0.4 °C periwound; +0.95 °C per extra species | Venous leg ulcers n=57 | H secondary | https://onlinelibrary.wiley.com/doi/abs/10.1111/wrr.12781 |
| Wound–periwound ΔT vs infection rating r=0.32; FLIR One error ±2 °C | Collins 2025, 268 wounds | H | https://pmc.ncbi.nlm.nih.gov/articles/PMC12315627/ |
| Wound–abdomen gradient SSI 1.73 vs 1.12 °C (d2), 1.92 vs 1.09 (d7), 1.96 vs 1.56 (d15); OR ~2.3/°C; SSI diagnosed median day 18 (signal led by 11–16 d) | Post-caesarean n=50 | H | https://pmc.ncbi.nlm.nih.gov/articles/PMC6323776/ |
| Infected wounds COOLER days 1–2 post-op; no diff days 3–4 | Stoma closure n=60 | H | https://pubmed.ncbi.nlm.nih.gov/30791157/ |
| Infection: ~40 °C within 48 h of inoculation; sterile injury peaks ~7 d. Device threshold sustained >40 °C. Sensor err <0.15 °C | Pig (Pang 2020) | A | https://pmc.ncbi.nlm.nih.gov/articles/PMC7080536/ |
| Infected ~38.5 °C (S. aureus), 37.5–38 °C (gram-neg) vs 37 °C; peak days 4–6 | Rabbit | A | https://pmc.ncbi.nlm.nih.gov/articles/PMC8313280/ |
| ΔT +0.8–1.5 °C; biggest diff day 2, peak day 4, normal day 6 | Rabbit implant | A | https://pmc.ncbi.nlm.nih.gov/articles/PMC8820007/ |
| Temp (and pH) rose daily after MRSA/P. aeruginosa infection; peak days 3–4; baseline by day 7 after treatment; uninfected flat | Diabetic rat, Gao 2023 (figures only) | A | https://www.science.org/doi/10.1126/sciadv.adf7388 |
| Healing: centre −0.09 °C/wk, edge −0.11 °C/wk, healing wounds −0.19 °C/wk | Chronic wounds | H | PMC13035947 |
| Post-op normal: peak day 3 +3.1–4.4 °C; +0.5–0.7 °C at 30–60 d; 0 at 90 d | Hip/knee replacement | H | https://pmc.ncbi.nlm.nih.gov/articles/PMC3102809/ |
| Periwound >35 °C good healing, <34 °C poor | Pressure ulcers n=50 | H | https://pmc.ncbi.nlm.nih.gov/articles/PMC8269037/ |
| Wrist circadian amplitude 1.16–1.44 °C; heel 1.8–2.2 °C; peaks at night | iButton | H | https://pmc.ncbi.nlm.nih.gov/articles/PMC11353769/ |
| Water on skin ~−3.5 °C, recovers ~30 min | Sensor demo | H/B secondary | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4476093/ |
| Wearable sensor bias ~0.04–0.11 °C, LoA ±0.3–0.4 °C | Validation | H | https://pmc.ncbi.nlm.nih.gov/articles/PMC13394553/ |
| MAX30205 ±0.1 °C | Datasheet | B | https://www.analog.com/media/en/technical-documentation/data-sheets/MAX30205.pdf |
| Ulcer prediction (not infection): 2.2 °C alarm cut ulceration 12.2%→4.7%; 37-day lead | Lavery 2007 / Frykberg | H | https://pubmed.ncbi.nlm.nih.gov/18060924/ |

## Gaps
- No human continuous-wearable data on hourly rise before infection; time course from animals.
- Fierheller full text paywalled; 2026 cohort didn't report infected-group temps; Gao absolute ΔT only in figures.
- Human specificity typically 36–62% for temp alone; temp is weak alone, must combine with pH/moisture.
