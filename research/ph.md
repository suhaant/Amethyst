# Wound pH vs bacterial infection — extracted data

Evidence: H = human clinical, A = animal, V = in vitro/bench.

| Value | Context | Ev | Source |
|---|---|---|---|
| Intact skin 5.67 ± 0.53 (4.61–7.20) | n=117 pts, ISFET | H | https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/ |
| Acute wound 6.59 ± 0.62; chronic 7.11 ± 0.66 | Wound centre | H | same |
| Healing 6.82 ± 0.81; non-healing 7.04 ± 0.69 | p=.028 | H | same |
| Phase: inflammation 7.05, granulation 6.90, epithelialisation 6.56 | Same cohort | H | same |
| **Infected 7.53 ± 0.59 (centre), 7.57 ± 0.46 (edge); colonised 7.05 ± 0.64; non-infected 6.90 ± 0.88** | n=21 infected meas. | H | same |
| Organisms: S. aureus 6/11, P. aeruginosa 3/11, E. coli 3/11 | Cultures | H | same |
| Healing decline −0.088 pH/week (healing), −0.03/week (non-healing), −0.053 overall | ≤127 days | H | same |
| Centre 7.03, edge 7.07, surrounding skin 6.66 | Spatial | H | same |
| DFU healed: bed 6.28 ± 0.70, edge 6.47; not healed: bed 7.10 ± 0.86, edge 7.48. Healing cutoff bed <6.7 (AUC 0.78) | n=187 DFU | H | https://pmc.ncbi.nlm.nih.gov/articles/PMC13097620/ |
| Infected (no necrosis) 7.2 vs non-infected 6.5; necrotic tissue 6.1 ± 0.6 (necrosis lowers pH) | Metcalf 2019 / Schneider 2007, secondhand | H | same |
| Leg ulcers 8.9 ± 0.6; critically colonised 9.25 ± 0.61 | Romanelli/Strohal, secondhand | H | https://pmc.ncbi.nlm.nih.gov/articles/PMC9493238/ |
| Burns: pH rose BEFORE clinical infection signs | 6/26 infected | H | https://pubmed.ncbi.nlm.nih.gov/25468471/ |
| P. aeruginosa culture 6.5 → 9.0 over 18 h; S. aureus dips to 6.0 at 8 h then ~7.0 | Snippet only, verify | V | https://www.tandfonline.com/doi/full/10.1080/05704928.2018.1558232 |
| Rat S. aureus: pH up at 6 h, rising over 4 days (~7.0 → 8.0); temp 32.5 → 33.7 °C | Figure values | A | https://pmc.ncbi.nlm.nih.gov/articles/PMC11216007/ |
| Diabetic rat MRSA + P. aeruginosa: pH/temp rise daily, peak days 3–4, back near baseline ~3 d after treatment; uninfected flat | Gao 2023, figures only | A | https://www.science.org/doi/10.1126/sciadv.adf7388 |
| Horse: inoculation NO effect on pH (p=0.75) | Negative result | A | https://pmc.ncbi.nlm.nih.gov/articles/PMC6709944/ |
| Rat burns 7.5 (d1) → 8.0–8.2 (d2) → 7.8 (d3) | Colorimetric | A | https://pmc.ncbi.nlm.nih.gov/articles/PMC10275586 |
| Thresholds: normal 4–6, warning 6–7.5, infection 7.5–9 | Review restatement, not validated | V/A | https://pmc.ncbi.nlm.nih.gov/articles/PMC12222607/ |
| pH ≤7.6 → 30% shrink in 2 wk; ≥8.0 → wounds grew | Gethin, n=20 | H | https://wounds-uk.com/wp-content/uploads/2023/02/content_9150.pdf |
| Meter accuracy ±0.1–0.2 pH | Clinical meters | H | above |
| PANI sensor 59.7 mV/pH; M-PANI 61.5 mV/pH (pH 4–8) but 20.45 mV/pH (pH 8–10); 4.8% loss/48 h | Sensors | V | sciadv.adf7388; https://pmc.ncbi.nlm.nih.gov/articles/PMC11647034/ |
| Drift <2 mV/h ≈ 0.04 pH/h; stretch error <0.2 pH | Su 2024 | V | PMC11216007 |
| Textile sensor drift ~1%/day, resolution 0.2 pH | Bench | V | https://pmc.ncbi.nlm.nih.gov/articles/PMC8294608/ |

## Gaps
- No continuous pH-per-hour data after infection onset in text; anchors only: rise at 6 h (rat), peak day 3–4 (rat), rise before clinical signs (human burns). Digitise Gao 2023 Fig 5E and Su 2024 Fig 6C with WebPlotDigitizer for real curves.
- S. aureus may acidify first; necrosis lowers pH; colonised overlaps non-infected (SD 0.6–0.9). pH alone weak.
- No in-vivo multi-day sensor drift data.
