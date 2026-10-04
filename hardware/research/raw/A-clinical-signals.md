# PulsePatch research A: which wound signals are worth sensing

Compiled 2026-10-03. Scope: clinical evidence that a measurable signal detects wound infection or predicts healing / non-healing, and how the answer shifts for military / austere and low-resource / tropical settings.

## 0. How to read this document

**Evidence grades**

- **A** = RCT or meta-analysis of RCTs, or part of routine clinical criteria.
- **B** = human observational cohort / diagnostic-accuracy study. Meta-analyses of observational studies whose own authors rate certainty as low are graded B here, not A.
- **C** = animal, or small human pilot (n < 30).
- **D** = in vitro only, or no human wound data found.

A grade always refers to a specific claim (for example "predicts ulceration" is not the same claim as "detects infection"). Where one signal has different grades for different claims, both are shown.

**Markers**

- `[n]` = numbered source in section 7. Numbers and quotes were read in the source during this review unless marked otherwise.
- `[search-summary]` = the number was seen only in a search-engine result summary; the source page itself was not opened or was blocked. Treat as probable, not confirmed.
- `UNVERIFIED` = stated from background knowledge or engineering reasoning, not confirmed in a source during this review.
- `Inference` = a design implication drawn from the cited evidence; it is not itself a clinical finding.

**Access limits.** PubMed, PMC and NICE pages returned CAPTCHA / 403 responses. Abstracts and open-access full texts were therefore read through the Europe PMC REST API (same records, same PMIDs). Paywalled full texts were not read; for those, only abstract-level numbers are reported.

**The single most important framing fact.** A 2024 systematic review of diagnostic-accuracy studies for infection in chronic wounds found only four eligible studies (two of fluorescence imaging, one of wound-fluid enzymes, one of bacterial protease activity), with sensitivities of 50 to 75% and specificities of 47 to 100%, and concluded: "We have not identified any methods for diagnosing infection in chronic wounds with either a sufficient quality of evidence to recommend their use in community settings at present." [20] A 2024 scoping review of "smart" dressings for surgical site infection found sixteen eligible papers and "no studies in human participants." [21] No signal below is a validated stand-alone infection detector. The ranking is a ranking of the least-weak options.

---

## 1. Ranked table

Ranked by strength of human evidence for detecting infection or predicting healing, then by how early the signal moves. "Patch fit" is a separate column because several well-evidenced signals cannot be sensed by a small board.

| Rank | Signal | Best human evidence (design, n, numbers) | Lead time | Grade | Patch fit | Verdict |
|---|---|---|---|---|---|---|
| 1 | **Increasing pain (patient-reported)** | JAMA systematic review, 15 studies, 985 participants, 1,056 wounds: increasing pain LR+ 11 to 20; LR− 0.64 to 0.88 [18]. In 36 quantitatively cultured wounds, increasing pain and wound breakdown each had specificity 100% [19]. | Concurrent; no lead-time data | A (systematic review) | No sensor; one app question | Capture in software. Fails in neuropathy and painless disease (Buruli) [6][79]. |
| 2 | **Differential skin temperature** (vs contralateral or periwound reference) | Pre-ulcer inflammation: 5 RCTs, 772 participants, RR 0.51 (95% CI 0.31 to 0.84), GRADE low [1]. Infection in chronic leg ulcers: n = 40 ulcers + 20 controls, F = 44.2, P < .001 [7]; n = 112, elevated temperature "eight times more likely" to have moderate/heavy growth [8]; n = 267, r = 0.32 with clinician-judged infection [10]. SSI: n = 50, day-2 AUROC 0.70 [12]. | DFU: about 37 days before ulcer [2]. SSI: day-2 image predicts infection within 30 days [12]. Chronic-wound infection: none measured | A for pre-ulcer prevention; B for infection | Excellent (thermistors) | Core signal. IWGDF/IDSA 2023 nonetheless suggests **not** using temperature to diagnose diabetic foot soft-tissue infection [6]. |
| 3 | **Bacterial autofluorescence under 405 nm (imaging)** | Multicentre diagnostic study, n = 350: sensitivity for > 10^4 CFU/g rose from 15.3% (clinical signs) to 61.0% (signs + imaging); specificity 84.1%; PPV 96.0%, NPV 32.0% [54]. Pilot RCT n = 56: 12-week healing 45% vs 22% [56]. | Finds high bacterial load in wounds with no clinical signs; days not quantified | B (one pilot RCT) | Imaging only. Non-imaging photodiode use: D | Evidence supports a camera read by a trained person. A point sensor is an experiment, not a validated signal. |
| 4 | **Systemic signs** (heart rate, core temperature, respiratory rate) | Part of the IWGDF/IDSA severity criteria: temperature > 38 °C or < 36 °C, heart rate > 90/min, respiratory rate > 20/min [6]. Used in NEWS for sepsis screening in prolonged casualty care [72]. | Late for local infection; "uncommon in patients with a DFI" [6] | A (routine criteria) | Heart rate by PPG: yes. Core temperature: no | Low value at home, high value in austere care. |
| 5 | **Offloading adherence / plantar pressure / activity** | RCT, 58 completers: pressure-alert insole, ulcer incidence rate ratio 0.29 (95% CI 0.09 to 0.93) [53]. Cohort n = 79: adherence 59 ± 22% of activity; better adherence predicted smaller ulcer at 6 weeks [52]. n = 20: device worn for 28% of daily activity [51]. | Not an infection signal | A/B for healing and recurrence; none for infection | Accelerometer: excellent. Pressure: site-dependent | Strong healing predictor for plantar and pressure wounds only. |
| 6 | **Protease activity** (host elastase / MMP; bacterial proteases) | Host: 290 swabs, AUC 0.69 to 0.82 for non-healing [37]. Bacterial: n = 366, "majority of wounds tested positive ... prior to exhibiting at least three CSS" [38]; n = 266, elevated activity lowered 12-week healing probability [39]. | Before clinical criteria met; days not quantified | B | Poor. Validated as single-use swab assays, not continuous sensors | Good biology, wrong form factor. |
| 7 | **Sub-epidermal moisture** (capacitance / bioimpedance of intact skin) | Systematic review, 17 studies: detects pressure damage 4.61 days earlier than visual assessment (95% CI 3.94 to 5.28); sensitivity 48.3 to 100%, specificity 24.4 to 83.0% [47]. Works in dark skin: n = 66, OR 1.88 per 100 units [48]. | 4.6 days (pressure injury) | B (pressure injury); none for infection | Good; can share electrodes with a moisture sensor | Worth adding for pressure-injury use; no infection data. |
| 8 | **Tissue oxygenation / perfusion** (TcPO2, hyperspectral, NIRS) | TcPO2 meta-analysis: diagnostic odds ratio 15.81 (95% CI 3.36 to 74.45) for healing, "overall quality of the evidence is low" [43]. Hyperspectral, 54 patients / 73 ulcers: sensitivity 80%, specificity 74% [44]. | Predicts healing weeks ahead; not infection | B | TcPO2: no (heated electrode). Optical: instrument-grade | Predicts healing potential, not infection. |
| 9 | **Odour / volatile compounds (e-nose)** | Pilot n = 77: sensitivity 91%, specificity 71% vs clinical judgment; 81% / 63% vs culture [34]. Foul odour was one of four valid signs in [19]. | None measured | B (single pilot) | Poor today (bench instrument) | Promising, not ready. Ask about odour in the app. |
| 10 | **Wound pH** | 120 samples: infection proportion rose with pH, but "not sufficient to promote the use of elevated pH alone as an indicator for wound infection" [24]. n = 97: pH fell 8.34 to 7.71 over 4 weeks as area fell 62%, no accuracy statistics [25]. n = 100 infected DFUs: "No association" between microflora and pH [26]. | None measured | B, weak to negative for infection | Sensor exists but drifts and fouls [28] | Weakest of the three currently planned signals. |
| 11 | **Exudate lactate** | Diabetic foot ulcers: median 21.03 mM (5.58 to 80.40); higher when infected (P = 0.001); lower baseline in ulcers that healed (P = 0.007); n not in abstract [30]. | None measured | B/C | Enzyme electrode; stability unproven in exudate | Not ready. |
| 12 | **Moisture / dressing saturation** | n = 30, 588 readings: 44.9% of dressing changes happened at optimal moisture [29]. No link to infection reported. | None | B for dressing-change timing; none for infection | Excellent (two electrodes) | Keep for logistics and bleed-through, not as an infection signal. |
| 13 | **Erythema / colour** | Classic sign, but reported in 13.4% (light), 7.2% (medium), 2.3% (dark skin) "despite comparable bacterial loads"; clinical-sign sensitivity 2.9% in the darkest group [55]. | Concurrent | B, with documented skin-tone bias | Needs imaging | Do not rely on it. |
| 14 | **Exudate uric acid, glucose** | Uric acid: raised in venous-ulcer fluid, tracks chronicity; no infection outcome, n not in abstract [31]. Glucose: 8 patients, lower in wound fluid than serum [32][search-summary]. | None | C | Enzyme electrodes | Not ready. |
| 15 | **Wound-bed bioimpedance** | 4 acute wounds [49]; 7 patients / 18 ulcers, r = −0.86 with wound area [50]. | None | C | Good | Tracks closure (which a ruler also does); no infection data. |
| 16 | **Pyocyanin (electrochemical)** | 14 samples: sensitivity 71%, specificity 57% for *Pseudomonas* [33]. | None | C | Good electrode fit | One organism, near-chance specificity. |
| 17 | **Nitric oxide, H2O2, cytokines in exudate** | Wearable tested in "20 patients with chronic wounds and in two patients before and after surgery"; no accuracy statistics in abstract [35]. Press coverage claims 1 to 3 days' lead [36]. | 1 to 3 days (press claim only) | C | Research prototype with microfluidics | Not ready. |
| 18 | **Swelling / strain, PPG perfusion at the wound, ammonia** | No human wound-infection studies found. PPG evidence is free-flap monitoring pilots [46][search-summary]. | — | D | — | Skip. |

---

## 2. Per-signal detail

### 2.1 Temperature

**(a) Human evidence**

*Diabetic foot, before an ulcer exists (the "2.2 °C / 4 °F rule").*
- Meta-analysis of 5 RCTs, 772 participants at IWGDF risk 2 or 3. Hotspot definition: "temperature differences >2.2°C on two consecutive days between similar locations in both feet." Relative risk of ulcer 0.51 (95% CI 0.31 to 0.84). GRADE certainty low; three trials at high risk of bias. Amputation: "Only two trials reported amputation outcomes with no significant difference between groups." All trials were in Europe and the US [1].
- Remote smart mat, 129 participants, 37 ulcers over 34 weeks: at 2.22 °C asymmetry the system detected 97% of ulcers with a 37-day lead time and a 57% false-positive rate; at 3.20 °C, sensitivity 70% and false-positive rate 32% [2].
- Diagnostic study, n = 54: a 2.2 °C contralateral-spot difference gave "sensitivity, 76%; specificity, 40%" for any foot complication; a 1.35 °C mean difference between feet gave "sensitivity, 89%; specificity, 78%" for urgency of treatment [3].
- Single readings are unreliable: in 20 patients measuring four times a day for six days, a > 2.2 °C difference appeared in 8.5% of measurements but was confirmed the next day in only 0.3% [4].
- IWGDF 2023 prevention guideline: consider coaching moderate / high-risk patients to self-monitor foot temperature daily, acting on > 2.2 °C on two consecutive days (Conditional; Moderate) [5][search-summary].

*Infection in an existing wound.*
- Chronic leg ulcers, 40 ulcers plus 20 controls without wounds, handheld infrared thermometer on periwound skin (reference site described in a secondary source as the opposing limb or body area [search-summary]): "a statistically significant relationship between increased periwound skin temperature and wound infection" (F = 44.238, P = .000) [7]. The abstract gives no threshold. Secondary sources quote the threshold from this study as 3 °F [search-summary] and as 1.1 °C [10]; the primary full text was not available to settle which.
- NERDS / STONEES validation, n = 112: wounds with "elevated temperature were eight times more likely to have moderate or heavy bacterial growth." Three-sign combinations reached sensitivity 73.3% / specificity 80.5% (light growth) and 90% / 69.4% (moderate to heavy growth) against semi-quantitative swab culture [8].
- Cross-sectional, 267 patients / 268 chronic wounds, smartphone thermal camera: wound-minus-periwound temperature correlated with clinician-judged infection at Pearson r = 0.32, described by the authors as "fair." No sensitivity, specificity or threshold reported [10].
- Retrospective thermography case series: infected wounds +4 to 5 °C above healthy skin, inflamed wounds +1.5 to 2.2 °C, normal controls +1.1 to 1.2 °C; sample size not in abstract [11].
- Low-cost infrared thermometers agree with a reference device (n = 108, intraclass correlation > 0.95), so the measurement itself is cheap and reliable [9].

*Surgical site infection.*
- 50 obese women after caesarean section, 14 (28%) developed SSI. Wound-minus-abdomen temperature difference: day-2 AUROC 0.697 (95% CI 0.538 to 0.857), sensitivity 92.9% and specificity 38.9% at the sensitivity-optimised cut-off; day-7 AUROC 0.687. Direction matters: "Mean abdominal temperature was lower in women who subsequently developed SSI" (32.5 °C vs 33.5 °C at day 7) [12]. The predictive pattern here was a cooler reference region and a wider gap, not simply a hot wound.
- Scoping review of thermography in surgical / traumatic wounds, 19 studies: surgical wounds are normally warm for 1 to 2 weeks; "If a secondary temperature peak happens during the healing phase of a surgical wound, it is likely that infection has occurred," but "firm evidence supporting infection thermography surveillance of surgical wounds as a technique is missing" [13]. A second scoping review (76 studies) flags small samples, retrospective designs and no accounting for skin tone as barriers [14].
- Rural Rwanda, caesarean wounds photographed with a phone thermal module: median AUC 0.90 for a transfer-learning model on thermal images (0.86 for a naive model), described as "the first reported work using thermal imaging to predict infection" [15]. This is camera imaging plus a neural network, not a contact sensor.

*The contrary guideline.* IWGDF/IDSA 2023, Recommendation 4: "For diagnosing diabetes-related foot soft-tissue infection, we suggest not using foot temperature (however measured) or quantitative microbial analysis. (Conditional; Low)." Rationale: "employing either infrared or digital thermography does not appear to provide substantial help in diagnosing infection or predicting the clinical outcome in patients with a DFU seen in the hospital setting" [6]. The strongest temperature evidence is therefore for pre-ulcer inflammation, not for diagnosing infection in an open diabetic wound.

**(b) Lead time.** About 37 days before a diabetic plantar ulcer [2]. Day 2 after surgery for SSI diagnosed within 30 days [12]. No lead-time data for infection of chronic wounds; every study is cross-sectional.

**(c) Confounders and failure modes**
- Blunted inflammation: "signs and symptoms of inflammation may, however, be masked by the presence of peripheral neuropathy, peripheral artery disease (PAD), or immune dysfunction" and "clinically significant foot ischaemia makes both diagnosis and treatment of infection considerably more difficult" [6].
- Other causes of local warmth: the IWGDF criteria require "no other cause of an inflammatory response of the skin (e.g., trauma, gout, acute Charcot neuro-arthropathy, fracture, thrombosis, or venous stasis)" [6].
- Dressing changes: across 133 dressing episodes wound beds averaged 32.7 °C under the dressing, fell to 29.9 °C during the change, and took about 23 minutes to recover [16].
- Environment: the n = 267 study lists room temperature, humidity, emissivity, viewing angle and dead skin as confounders of infrared readings [10]. Left-right foot differences were "not significantly correlated with walking activity, environmental temperature or time of day" in a temperate-climate study [4], so a differential is far more robust than an absolute value.
- Normal post-operative warmth for 1 to 2 weeks masks early SSI [13].
- `Inference`: the patch's own 405 nm LEDs and ultrasound transducer deposit heat. Temperature must be sampled with therapy off and after thermal recovery, or the device will detect itself.

**(d) Grade.** Absolute skin temperature: not supported. Differential temperature: **A** for pre-ulcer prevention in the diabetic foot, **B** for infection in chronic wounds and surgical sites.

### 2.2 Wound bed / exudate pH

**(a) Human evidence.** The popular claim that alkaline pH marks infection rests mostly on in vitro work and narrative reviews.
- Descriptive review: healthy skin pH 4.2 to 5.6, chronic wounds 7.2 to 8.9. Conclusion: "while pH is not sufficiently understood to be translated into current practice as a metric for infection, the pH scale does have potential." Only one prospective human intervention study was included, and "The quality of the studies was not formally assessed" [23].
- 120 wound samples compared against expert clinical judgment and neutrophil enzyme activity: infection proportion increased with pH, but "The strength of the relationship ... is not sufficient to promote the use of elevated pH alone as an indicator for wound infection" [24].
- 97 patients, weekly for four weeks (72% acute wounds, pH strips): mean pH 8.34 ± 0.32 to 7.71 ± 1.11 while area fell 62%. Uncontrolled; no threshold, no accuracy statistics, and "no significant difference in pH between acute and hard-to-heal wounds" at baseline [25].
- 100 infected diabetic foot ulcers: "No association was found between the associated microflora and the pH of the wounds"; chronicity was associated with alkaline pH (P = 0.013) [26].
- Conference abstract, 55 diabetic foot ulcers: pH range 6.2 to 8.5; states pH influences presence of clinical signs but gives no infected vs non-infected values [27].

No study was found that reports sensitivity, specificity or AUC for a pH cut-off against a microbiological reference standard. Thresholds such as "pH > 7.3 means infection" are not validated.

**(b) Lead time.** None measured.

**(c) Confounders.** Chronic non-infected wounds are also alkaline (7.2 to 8.9) [23], so pH separates chronic from healing better than infected from colonised. Sensor side: a textile pH sensor showed 1% daily drift but "a 19% variation of the estimated pH" over 15 days in simulated exudate, the authors expect protein fouling "after prolonged use in real samples," and it was never tested in humans [28]. Topical agents and cleansers with their own pH are an obvious confounder (`UNVERIFIED`, not checked in a source).

**(d) Grade.** **B, weak** for tracking healing trajectory. **B, negative** as a stand-alone infection indicator.

### 2.3 Moisture / exudate volume / dressing saturation

**(a)** One observational study with a commercial in-dressing moisture sensor: 30 patients (19 diabetic foot, 11 pressure ulcers), 588 readings; "44·9% of the dressing moisture readings fell within the optimum" range at the moment the dressing was changed anyway, implying many unnecessary changes. No relationship to infection or healing was reported [29]. "Serous exudate" was among the secondary signs examined in 36 cultured chronic wounds, but the four signs reported as valid were increasing pain, friable granulation, foul odour and wound breakdown [19].

**(b)** None measured. **(c)** Sweat, incontinence, irrigation fluid, blood. `Inference`: occlusion in hot humid climates raises baseline moisture. **(d)** **B** for dressing-change timing; no evidence for infection detection.

### 2.4 Uric acid, lactate, glucose in exudate

- **Lactate:** see table row 11 [30]. Authors call it "helpful for confirming the suspicion," i.e. an adjunct, in a preliminary report.
- **Uric acid:** elevated in venous-ulcer wound fluid "with relative concentrations correlating with wound chronicity"; mechanism via xanthine oxidase. No infection outcome and no accuracy data [31]. It is popular in smart-bandage papers mainly because it is easy to oxidise on an electrode (`UNVERIFIED` characterisation).
- **Glucose:** eight patients with leg ulcers; glucose lower in wound fluid than serum and rising as healing begins [32][search-summary]. Blood glucose in diabetic patients confounds it directly.

**Grade:** lactate **B/C**; uric acid and glucose **C**. Enzyme electrodes in protein-rich exudate over days remain unproven (see pH drift, [28]).

### 2.5 Oxygenation and perfusion

- **TcPO2:** systematic review of tests predicting diabetic foot healing (37 studies across eight tests): pooled diagnostic odds ratio 15.81 (95% CI 3.36 to 74.45) for healing and 4.14 (2.98 to 5.76) for amputation; "The overall quality of the evidence is low" [43]. Measurement needs an electrode heated to about 44 °C, 15 to 20 minutes to stabilise, and is distorted by oedema and infection [search-summary]; not compatible with a wound patch.
- **Hyperspectral imaging:** 66 enrolled, 54 patients / 73 ulcers completed; healing index sensitivity 80% (43/54), specificity 74% (14/19), PPV 90%; false results came from osteomyelitis and callus [44].
- **NIRS:** 46 diabetic foot ulcers, sensitivity 0.9 and specificity 0.86 for predicting healing by four weeks [45][search-summary].
- **PPG / SpO2 near the wound:** no wound-infection or wound-healing studies found; published work is free-flap monitoring in 3 to 25 patients [46][search-summary].
- **Skin-tone bias (optical):** among patients reading 92 to 96% on pulse oximetry, arterial saturation was actually < 88% in 11.7% of Black vs 3.6% of White patients (second cohort: 17.0% vs 6.2%) [62].

**Lead time:** predicts healing potential at one visit; not an infection alarm. **Grade:** **B** for healing prognosis; none for infection.

### 2.6 Bioimpedance

- **Sub-epidermal moisture (intact skin, pressure injury):** table row 7 [47]. One study in the review reported "a 93% decrease in PU rates when staff acted on the results." In 66 nursing-home residents, higher readings predicted pressure damage one week later in people with dark skin tones (OR 1.88 per 100 units, P = .004), where visual redness is unreliable [48]. NICE's assessment of the commercial scanner could not be opened (403).
- **Wound-bed impedance:** rises toward intact-skin values as wounds close; shown in four acute wounds [49] and in 7 patients / 18 ulcers / 104 measurements (r = −0.86 with wound area, P < 0.001) [50]. No infection data.
- **Periwound oedema as an infection sign:** no human study found.

**Grade:** **B** for early pressure-injury detection; **C** for wound-bed healing tracking; none for infection.

### 2.7 Pressure / shear / offloading adherence

- Patients wore a removable cast walker for "only 28% of total daily activity"; even the most adherent subset reached 60% (n = 20) [51].
- 79 patients, six weeks: devices used during 59 ± 22% of activity; adherence independently predicted smaller ulcer size; postural instability predicted non-adherence [52].
- Proof-of-concept RCT of a pressure-sensing insole with smartwatch alerts: 90 recruited, 58 completed; 71% reduction in ulcer incidence (rate ratio 0.29, 95% CI 0.09 to 0.93; P = 0.037); 86% reduction among good compliers. The number of patients who ulcerated did not differ (6 of 26 vs 4 of 32; P = 0.29) [53].

**Relevance:** for plantar diabetic ulcers and pressure injuries, whether the wound is being loaded is one of the best-evidenced predictors of healing. It says nothing about infection. An accelerometer on the patch gives activity and wear-time; true plantar pressure needs the patch to be under the load. **Grade:** **A/B** for healing and recurrence.

### 2.8 Bacterial metabolites

- **Pyocyanin:** disposable electrode, 7.5 µL of wound fluid from chronic-wound patients, compared with 16S sequencing: "9 correct matches, 2 false negatives, and 3 false positives giving a sensitivity of 71% and specificity of 57%" [33]. Detects one species.
- **Volatile compounds / e-nose:** table row 9 [34]; authors: "A larger study is needed to confirm our results."
- **Ammonia:** no human wound studies found (not searched exhaustively).

**Grade:** pyocyanin **C**; e-nose **B** (single pilot).

### 2.9 Proteases and host markers

- **Host proteases:** 290 swabs from four US centres (healing status known for 211): AUC 0.69 (all) and 0.78 (most reliable trajectories) for neutrophil elastase, 0.70 and 0.82 for MMPs [37]. MMP-9 in diabetic foot ulcer fluid: lower in 23 ulcers that healed at 12 weeks than in 39 that did not; AUC 0.94 after adding TIMP-1 and TGF-β cut-offs [41].
- **Neutrophil enzymes for infection:** 81 patients; myeloperoxidase, elastase, lysozyme, cathepsin G models all significant (P ≤ 0.001) vs swab; notably "no correlation between clinical judgment and wound swab" [40].
- **Bacterial protease activity:** n = 366 across six US centres, positive in most wounds before three clinical signs appeared, but "some wounds with high bioburden were negative ... and others with low bioburden were positive" [38]; n = 266, elevated activity lowered 12-week healing probability [39].
- **Gelatinase rapid test:** 198 patients, sensitivity 96.84%, specificity 97.5% vs culture, read only from a repository summary; about 80% of the tested chronic wounds were culture-positive, so spectrum bias is likely [42].
- **Nitric oxide, H2O2, oxygen, cytokines:** table row 17 [35][36]. Interleukin-1β and TNF-α were higher in protease-positive wounds [38].
- **CRP:** serum (not exudate) CRP is "significantly higher in infected than noninfected DFUs"; guideline suggests serum CRP, ESR or procalcitonin when the examination is equivocal. "about half of the patients diagnosed with a DFI [have] a normal WBC" [6].

**Lead time:** bacterial protease positivity precedes clinical criteria [38]; days not quantified. **Grade:** **B**, but every validated format is a single-use swab or lateral-flow assay. No continuous in-dressing protease sensor has human data.

### 2.10 Bacterial autofluorescence under 405 nm

**(a) Human evidence (all with a handheld imaging device)**
- 350 patients, 14 US outpatient centres, biopsy quantitative culture as reference. 287 of 350 wounds (82%) had > 10^4 CFU/g. Clinical signs alone: sensitivity "15.33%". Signs plus fluorescence: "61.0% [95% CI, 55.3–66.6%]", specificity "84.1%". Fluorescence alone: PPV 96.0%, NPV 32.0%. Clinicians had to pass a colour-blindness and image-interpretation test [54]. A negative image does not rule out high bacterial load (NPV 32%).
- Mechanism: "Porphyrin-producing bacteria within the wound emit red fluorescence signals, Pseudomonas aeruginosa emits cyan fluorescence signals, and tissue components (e.g., collagen and fibrins) emit green fluorescence signals" [54].
- Limits stated by the authors: 1.5 mm excitation depth; cannot detect *Streptococcus*, *Enterococcus*, *Finegoldia* ("an estimated 12% of the most prevalent wound pathogens"); "Darkness is required"; does not distinguish biofilm from planktonic [54].
- *Pseudomonas*: cyan fluorescence in 28 wounds, culture-confirmed in 26 (PPV 92.9%); "does not provide information on negative predictive value, sensitivity or specificity" [57].
- Skin tone: sensitivity gain from imaging was 4.4-fold (light), 2.9-fold (medium) and 12-fold (dark); authors state fluorescence intensity "is not impacted by skin tone" [55].
- Outcomes: pilot RCT (n = 56) 12-week healing 45% vs 22%, wound-area reduction 91.3% vs 72.8% [56]. A 2025 systematic review of 17 studies concludes imaging improves detection but "further research is needed to clarify its impact on infection control and long-term healing outcomes" [58]. In vitro, 28 of 32 bacterial species fluoresced red [59][search-summary].

**Can the therapy LEDs plus a photodiode or spectral sensor reuse this?** The evidence supports imaging only.
- Every human study used a camera, and a trained reader judged the spatial pattern of red or cyan against the green tissue background [54]. No human or animal study of non-imaging (single-point) detection of wound bacterial fluorescence was found.
- A multi-channel spectral sensor could in principle separate a red band (the imaging devices pass roughly 601 to 664 nm [search-summary]) from cyan and green bands and report a red-to-green ratio. That is physically plausible and unvalidated.
- Unknowns that a point sensor cannot resolve without new data: detection threshold (the camera threshold is > 10^4 CFU/g [54]); blood, which absorbs violet light strongly (`UNVERIFIED`); fluorescent dressings or ointments (`UNVERIFIED`); and the loss of spatial contrast.
- The therapy and the signal share a mechanism. Antimicrobial 405 nm light works by exciting the same endogenous porphyrins ("protoporphyrin IX and coproporphyrin were the two most abundant species"; > 4-log kill at 216 J/cm²) [60][61]. `Inference`: red fluorescence will change after each therapy dose through both bacterial killing and porphyrin photobleaching, and the sensor cannot tell these apart. Read fluorescence before therapy, at low excitation dose.
- `Inference`: one point in favour is that the space under an opaque dressing is dark, which satisfies the darkness requirement.

**Grade:** imaging **B** (plus one pilot RCT). Photodiode / spectral point sensing **D**. Reasonable as a logged research channel since the LEDs already exist; not a basis for any clinical alert.

### 2.11 Colour / erythema, swelling, motion, systemic signs

- **Erythema** is in the IWGDF infection definition (> 0.5 cm around the wound; ≥ 2 cm marks moderate infection) [6] but is badly under-detected on dark skin [55]. Classic signs overall had mean sensitivity 0.38 in chronic wounds [19].
- **Swelling / strain:** "Local swelling or induration" is a defining sign [6]; no wearable strain-sensor study in human wounds found. **D.**
- **Motion / activity:** see 2.7.
- **Systemic signs:** "Systemic symptoms (e.g., feverishness or chills), marked leukocytosis, or major metabolic disturbances, are uncommon in patients with a DFI, but their presence denotes a more severe, potentially limb-threatening (or even life-threatening) infection" [6]. Useful as a severity alarm, not an early-detection signal, in home care.
- **Pain and odour** (patient-reported): the best-validated signs in chronic wounds [18][19]; see table row 1. The IWII 2022 consensus lists new or increasing pain and increasing malodour among the covert signs of local infection, alongside hypergranulation, friable granulation, pocketing, wound breakdown and delayed healing [22][search-summary].

---

## 3. Context shift: military / austere, delayed evacuation

### 3.1 What threatens life or limb

1. **Haemorrhage.** Of 4,596 battlefield fatalities (2001 to 2011), 87.3% died before reaching a treatment facility; 24.3% of those deaths (n = 976) were potentially survivable, and of these 90.9% were haemorrhage: truncal 67.3%, junctional 19.2%, extremity 13.5% [64].
2. **Compartment syndrome.** Diagnosis "in the deployed environment is primarily clinical and there is a very limited role for compartment pressure monitoring". Pain "is thought to be the most important clinical finding, but is often obscured in combat casualties due to altered mental status, heavy sedation, or mechanical ventilation." Oedema "peaks at 24-48 hours." "there is currently no sensitive or specific technique for establishing the diagnosis." Continuous-monitoring technologies "have not yielded acceptable diagnostic performance." Serial examinations "are repeated hourly when risk is high." Presentation after > 12 hours carries "markedly increased risk of complications after fasciotomy, including death and infection" [71].
3. **Wound infection and sepsis.** About 34% of evacuated US combat casualties developed an infection during initial hospitalisation (1,807 and 2,699-patient cohorts), half of them skin, soft tissue or bone [65][66]. Risk factors: large-volume transfusion (OR 10.68), high injury severity (OR 2.48), improvised-explosive-device mechanism (OR 1.84) [67]. "Unattended wounds can lead to acute infection and sepsis within days (or possibly within hours for very large and contaminated wounds)"; "Severe infection is often a greater risk than trauma in the PFC environment" [73].
4. **Multidrug-resistant organisms.** Infected combat wounds "most commonly grew Enterococcus faecium, Pseudomonas aeruginosa, Acinetobacter spp. or Escherichia coli" [65]. *Enterococcus* is one of the genera that does not fluoresce under 405 nm [54].
5. **Invasive fungal infection.** 6.8% overall among 1,133 casualties from Afghanistan, from 0.2% (ward) to 11.7% (ICU) [68]. In the first 37 cases: blast injury 100%, lower-extremity amputation 80%, three related deaths (8.1%), amputation revision 58%, median 11 debridements [69]. Risk factors: dismounted blast, above-knee amputation, perineal injury, transfusion of more than 10 units in 24 hours. Recognition: "recurrent tissue necrosis following at least two surgical debridements"; "often manifested by 'tinctorial' or color changes in a wound; early detection of such changes requires repeated inspection by an experienced clinician" [70]. Median 10 days from injury to diagnosis [search-summary]. Sources disagree on the transfusion threshold: an earlier analysis names "super-massive (>20 units)" transfusion as the independent predictor [75], while the current guideline uses more than 10 units [70].

### 3.2 What prolonged-care guidance tells the medic to watch

- Vital-sign trends: "fever or hypothermia; increase in heart rate; increase in respiratory rate; and, generally later rather than earlier, a decrease in blood pressure," plus mental status, SpO2, capillary refill [73]. NEWS (respiratory rate, SpO2, temperature, systolic pressure, heart rate, consciousness), with a score above 2 used as the trigger [72].
- Wound signs: "pain, redness warmth, purulent drainage, swelling" [73]; for burns, "changes in color of wound, possible foul smell of wound" [72].
- Distal perfusion: "Assess extremities distal to pressure dressings ... checking pulses and the skin color distal to the dressing" [72].
- Dressings: minimum "Reinforce dressings," better "Replace when soiled," best "Change every 24 hours"; irrigation every 24 hours [72]. Point-of-care lactate "every 6 hours until normal" is the "better" tier of sepsis monitoring [73].

### 3.3 Signals that matter here and not for a diabetic foot ulcer at home

| Signal | Why it matters in austere care | Evidence status |
|---|---|---|
| Dressing saturation, rapid rise | Re-bleeding under a dressing; "replace when soiled" [72]; haemorrhage is the leading survivable cause of death [64] | `Inference` from guideline tasks; no sensor trial |
| Heart-rate trend (PPG) | Core input to SIRS and NEWS [72][73]; changes before blood pressure does | Routine criteria (A); the patch is an unvalidated source |
| Skin temperature trend, local and differential | Local warmth is a listed wound sign [73] | B (section 2.1); unstudied in combat wounds; confounded by hypothermia wraps and environmental extremes |
| Pulse presence distal to a pressure dressing | A guideline task [72] | `Inference`; no validation of wound-patch PPG for this |
| Odour and colour change | Listed signs for burn-wound infection and fungal infection [70][72] | No patch-ready sensor (section 2.8) |

Signals that do **not** carry over: pH and offloading adherence have no role in the acute combat wound. Compartment syndrome is not detectable by any validated wearable; in a prospective blinded study "clinically useful NIRS data was available only about 9% of the time" versus > 85% for intramuscular pressure [74]. Fungal infection is recognised by repeated surgical inspection and histopathology [70], not by a surface sensor.

`Inference`: in this context the patch's value shifts from "detect infection early" to "reduce the number of times a medic must open the dressing and re-check vitals by hand."

---

## 4. Context shift: low-resource / tropical (sub-Saharan Africa)

### 4.1 Wound burden and types

- **Community wounds.** Rural Côte d'Ivoire, 3,842 people surveyed: wound prevalence 13.0%; 74.1% of patients under 15 years; causes "mechanical trauma (85.3%), furuncles (5.1%), burns (2.9%) and Buruli ulcer (2.2%)"; secondary bacterial infection in 22.0%; 35.5% of chronic wounds entirely neglected [78]. The typical patient is a child with a traumatic leg wound, not an older adult with diabetes.
- **Surgical site infection.** 12,539 patients, 343 hospitals, 66 countries: SSI after gastrointestinal surgery 9.4% (high-HDI), 14.0% (middle), 23.2% (low); adjusted odds ratio 1.60 for low-HDI; resistance to the prophylactic antibiotic in 35.9% of low-HDI infections vs 16.6% in high-HDI [76].
- **Diabetic foot disease.** Meta-analysis, 19 African countries, 56,173 patients: ulcer prevalence 13%, "increased over time"; about 15% of patients with foot lesions had major amputation and 14.2% died in hospital [77].
- **Burns.** "An estimated 180 000 deaths every year"; "almost two thirds occur in the WHO African and South-East Asia Regions" [81].
- **Snakebite.** 5.4 million bites a year, 81,410 to 137,880 deaths, and "around three times as many amputations and other permanent disabilities"; 435,000 to 580,000 bites needing treatment annually in Africa [80].
- **Buruli ulcer.** Reported in 33 countries; "often starts as a painless swelling (nodule), a large painless area of induration (plaque) or a diffuse painless swelling"; one third present as lesions over 15 cm [79]. Pain-based detection fails by definition.
- **Tropical ulcer.** Polymicrobial (fusobacteria, spirochaetes), lower leg, older children and young adults [84][search-summary]; no modern prevalence data found.

### 4.2 Constraints that change sensor choice

- **Skin pigmentation and optical sensing.** Erythema reporting falls from 13.4% to 2.3% and clinical-sign sensitivity to 2.9% in the darkest skin group [55]. Pulse oximetry misses hypoxaemia about three times as often in Black patients [62]. Forehead infrared thermometers had 26% lower odds of detecting fever in Black patients than oral thermometers (n = 4,375) [63]. Signals that do not depend on skin optics hold up: sub-epidermal moisture predicts damage in dark skin [48], and bacterial fluorescence gain was largest in dark skin [55]. `UNVERIFIED`: a contact thermistor measures conducted heat and should be pigment-independent.
- **Ambient heat.** `Inference`: as air temperature approaches skin temperature, the wound-to-reference difference shrinks. The only direct data found are veterinary: post-operative wound-minus-reference difference was 0.8 to 2.5 °C at about 11 °C ambient but 0.1 to 0.5 °C at about 20 °C (r = −0.51, P < 0.001) [17]. Human left-right differences were independent of environmental temperature in a temperate setting [4]; no human data above 30 °C ambient were found. Fixed thresholds from European and US trials [1] may not transfer; a per-patient baseline and an on-board ambient sensor are safer.
- **Humidity and sweat.** `Inference`: raises baseline moisture readings under occlusion; no clinical study found.
- **Phones and connectivity.** Sub-Saharan Africa, 2022: unique mobile subscribers 43% of the population; 25% connected to mobile internet, with a 59% usage gap and 15% coverage gap; smartphones 51% of connections (88% projected for 2030) [82]. A patch that only works through a smartphone app excludes a large share of users. `Inference`: provide an on-patch indicator.
- **Power.** About 600 million people in sub-Saharan Africa lack electricity, four in five of the global total [83]. `Inference`: primary-cell or very-low-duty-cycle design; no dependence on daily recharging.
- **Cost, reuse, cleaning.** No sourced cost-per-dressing or reuse data were found. `Inference`: a reusable electronics module with a cheap disposable contact layer is the only plausible architecture; thermistors and bare electrodes tolerate this, enzyme and pH chemistries do not.
- **Evidence base.** The temperature RCTs "took place in Europe and the US, therefore the overall effectiveness of this intervention outside of these continents remains uncertain" [1].

---

## 5. The 80/20 answer

### 5.1 Minimal signal set

1. **Differential temperature.** Two or more matched contact thermistors (periwound edge and a reference site several centimetres away or contralateral) plus one ambient-facing thermistor. Best-evidenced sensor signal [1][2][7][8][12], cheapest hardware, pigment-independent. Alert on a sustained difference from the patient's own baseline in either direction [12], confirmed across consecutive days [4]; blank the period after dressing changes [16] and after each therapy session. Literature thresholds sit between about 1.1 and 2.2 °C [1][3][10], so `Inference`: sensor matching of about ±0.1 °C is needed.
2. **Patient-reported pain and odour, asked daily in the app (or by a button on the patch).** Highest likelihood ratio of any infection indicator (11 to 20) [18], zero board area. Known blind spots: neuropathy [6], Buruli ulcer [79], sedated casualties [71].
3. **Moisture / dressing-saturation electrodes.** Not an infection detector, and should not be described as one. Earns its place because it is nearly free, tells the user when a dressing change is and is not needed [29], flags bleed-through in austere care [72], and provides context for interpreting other channels.

`Inference`: these three capture most of the achievable value because every better-evidenced alternative either needs a camera or a single-use assay, or predicts healing rather than infection.

### 5.2 Next signals if space allows

1. **Accelerometer.** Activity and wear-time; proxy for offloading adherence, one of the strongest healing predictors in plantar wounds [51][52][53]; also gates temperature readings on rest. Tiny and cheap.
2. **PPG heart rate.** Trend input for systemic deterioration [6][72][73]; mainly valuable in austere and post-surgical use. Report heart rate, not SpO2, given documented skin-tone bias [62].
3. **Fluorescence research channel reusing the 405 nm LEDs.** A multi-band spectral sensor read before each therapy dose. Log it; do not alert on it (section 2.10).
4. **Periwound impedance / sub-epidermal moisture,** sharing the moisture electrodes, if pressure-injury use is in scope [47][48].

### 5.3 What to do about pH

pH is the weakest of the three currently planned signals. The largest human dataset concludes it is insufficient alone [24], no validated threshold exists, non-infected chronic wounds are alkaline too [23], and the sensor is the least stable component over a multi-day wear [28]. If kept, treat it as a secondary healing-trend channel, never as the infection trigger, and do not let it displace differential temperature.

### 5.4 Attractive but not ready

| Signal | Why not yet |
|---|---|
| pH as an infection alarm | No accuracy data against a reference standard; negative largest study [24]; drift [28] |
| Uric acid, lactate, glucose | Small or abstract-only human data [30][31][32]; enzyme electrodes unproven in exudate |
| Pyocyanin | n = 14, specificity 57%, one species [33] |
| E-nose / VOC | One pilot, bench instrument [34] |
| Proteases (host or bacterial) | Good evidence [37][38][39] but only as single-use assays |
| Nitric oxide, H2O2, cytokines | One 20-patient feasibility study [35] |
| TcPO2 | Heated electrode and long stabilisation; predicts healing, not infection [43] |
| NIRS / hyperspectral oxygenation | Instrument-grade optics [44][45]; skin-tone questions [62]; failed for compartment syndrome [74] |
| Wound-bed impedance | n = 4 and n = 7 [49][50]; tracks closure only |
| Erythema / colour sensing | Fails on dark skin [55]; needs imaging |
| Photodiode bacterial fluorescence as a clinical signal | Zero non-imaging human data; confounded by the therapy itself [54][60] |
| Strain / swelling, ammonia | No human wound data found |

### 5.5 Does the answer change by context?

The minimal set holds in all three settings; the weighting changes.

- **US home care (diabetic foot, venous, pressure wounds):** differential temperature plus pain / odour check, then accelerometer.
- **Military / austere:** saturation and heart-rate trend move up; pH and offloading drop out; no patch signal addresses compartment syndrome or fungal infection.
- **Low-resource / tropical:** differential temperature stays first but needs ambient compensation and per-patient baselines; optical and colour-based signals are least trustworthy; an on-patch indicator and a reusable module matter more than any additional sensor.

---

## 6. Weakest claims / could not verify

1. **Infection threshold for periwound temperature.** Secondary sources attribute both 3 °F and 1.1 °C to the same primary study [7]; its abstract gives neither.
2. **Temperature for infection is contested.** IWGDF/IDSA advises against it for diabetic foot infection [6]; the supporting studies are small and mostly cross-sectional [7][8][10][11].
3. **No evidence for a contact temperature sensor under a dressing detecting infection in humans.** All human data are infrared thermometers or cameras on exposed skin.
4. **pH thresholds** (for example > 7.3) could not be traced to any diagnostic-accuracy study.
5. **Lactate [30] and uric acid [31] sample sizes** are not in the abstracts; full texts were not retrieved (server errors).
6. **Lead time is almost unmeasured.** Only three numbers exist: 37 days (pre-ulcer) [2], 4.6 days (pressure injury) [47], and a press-reported 1 to 3 days [36].
7. **Search-summary-only numbers:** IWGDF prevention wording [5]; TcPO2 measurement limits; NIRS 0.9 / 0.86 [45]; glucose in 8 patients [32]; 28 of 32 fluorescing species [59]; 601 to 664 nm passband; 10-day median to fungal diagnosis; tropical ulcer epidemiology [84]; IWII covert-sign list [22]; the 26-of-28 count behind the *Pseudomonas* PPV [57]; the "14 US outpatient centres" detail for [54].
8. **Gelatinase test (96.8% / 97.5%)** [42] read from a repository summary only; likely spectrum bias.
9. **FLAAG specificity:** 84.1% for signs plus imaging in the full text [54]; a search summary quoted 89% for imaging, not confirmed.
10. **Hot-climate temperature confounding** rests on one veterinary study [17] plus reasoning.
11. **Cost per patch, reuse and cleaning:** no sources found; all statements are inference.
12. **NICE assessments** (sub-epidermal moisture scanner, protease test) returned 403 and were not read.
13. **Regulatory status** of any device named here was not checked.
14. **All `UNVERIFIED` items:** blood absorption at 405 nm, fluorescent dressings / ointments, topical agents altering pH, pigment-independence of contact thermistors, why uric acid is popular in engineering papers.
15. **GSMA figures** [82] were read from text extracted from an infographic PDF; label-to-number matching is probable, not certain.
16. **WHO snakebite fact sheet** date was reported by the fetch tool as 17 September 2026 [80].
17. **Ammonia, strain sensing and wound-site PPG:** "none found" reflects one or two searches each, not an exhaustive search.

---

## 7. Sources

Europe PMC links resolve to the same record as the PubMed ID shown.

**Temperature**
1. Efficacy of at home monitoring of foot temperature for risk reduction of diabetes-related foot ulcer: a meta-analysis (2022). https://pmc.ncbi.nlm.nih.gov/articles/PMC9541448
2. Feasibility and efficacy of a smart mat technology to predict development of diabetic plantar ulcers. Diabetes Care 2017. PMID 28465454. https://europepmc.org/article/MED/28465454
3. van Netten JJ et al. Diagnostic values for skin temperature assessment to detect diabetes-related foot complications. Diabetes Technol Ther 2014. PMID 25098361. https://europepmc.org/article/MED/25098361
4. An explorative study on the validity of various definitions of a 2.2 °C temperature threshold as warning signal for impending diabetic foot ulceration. Int Wound J 2017. PMID 28990362. https://europepmc.org/article/MED/28990362
5. Guidelines on the prevention of foot ulcers in persons with diabetes (IWGDF 2023 update). PMID 37302121. https://pubmed.ncbi.nlm.nih.gov/37302121/
6. IWGDF/IDSA Guidelines on the diagnosis and treatment of diabetes-related foot infections (2023). https://iwgdfguidelines.org/wp-content/uploads/2023/07/IWGDF-2023-04-Infection-Guideline.pdf
7. Fierheller M, Sibbald RG. A clinical investigation into the relationship between increased periwound skin temperature and local wound infection in patients with chronic leg ulcers. Adv Skin Wound Care 2010. PMID 20631603. https://europepmc.org/article/MED/20631603
8. A cross-sectional validation study of using NERDS and STONEES to assess bacterial burden. Ostomy Wound Manage 2009. PMID 19717855. https://europepmc.org/article/MED/19717855
9. Validation of commercially available infrared thermometers for measuring skin surface temperature associated with deep and surrounding wound infection. Adv Skin Wound Care 2015. PMID 25502971. https://europepmc.org/article/MED/25502971
10. Wound bed temperature has potential to indicate infection status: a cross-sectional study. https://pmc.ncbi.nlm.nih.gov/articles/PMC12315627/
11. Chanmugam A et al. Relative temperature maximum in wound infection and inflammation as compared with a control subject using long-wave infrared thermography. Adv Skin Wound Care 2017. PMID 28817451. https://europepmc.org/article/MED/28817451
12. Childs C et al. The surgical wound in infrared: thermographic profiles and early stage test-accuracy to predict surgical site infection in obese women during the first 30 days after caesarean section. Antimicrob Resist Infect Control 2019. https://pmc.ncbi.nlm.nih.gov/articles/PMC6323776/
13. Fridberg et al. The role of thermography in assessment of wounds: a scoping review. Injury 2024. PMID 39226731. https://europepmc.org/article/MED/39226731
14. A comprehensive scoping review on the use of point-of-care infrared thermography devices for assessing various wound types. Int Wound J 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12358192/
15. Convolutional neural net models and image processing methods for predicting surgical site infection (rural Rwanda). MIT DSpace. https://dspace.mit.edu/handle/1721.1/139063
16. Influence of dressing changes on wound temperature. J Wound Care 2004. PMID 15517749. https://europepmc.org/article/MED/15517749
17. Postoperative wound assessment in cattle: how reliable is the back hand palpation? Ir Vet J 2021. https://pmc.ncbi.nlm.nih.gov/articles/PMC8207616/

**Infection diagnosis, general**
18. Reddy M et al. Does this patient have an infection of a chronic wound? JAMA 2012. PMID 22318282. https://europepmc.org/article/MED/22318282
19. Gardner SE et al. The validity of the clinical signs and symptoms used to identify localized chronic wound infection. Wound Repair Regen 2001. PMID 11472613. https://europepmc.org/article/MED/11472613
20. Identifying infection in chronic wounds in a community setting: a systematic review of diagnostic test accuracy studies. J Adv Nurs 2024. PMID 37574778. https://europepmc.org/article/MED/37574778
21. A scoping review of "smart" dressings for diagnosing surgical site infection: a focus on arthroplasty. https://pmc.ncbi.nlm.nih.gov/articles/PMC11505597/
22. IWII Wound Infection in Clinical Practice consensus document, 2022 update (PDF not opened; content seen in search summary only). https://woundsinternational.com/wp-content/uploads/2023/05/IWII-CD-2022-web.pdf

**pH and moisture**
23. The pH of wounds during healing and infection: a descriptive literature review. Wound Practice and Research 25(2). https://journals.cambridgemedia.com.au/wpr/volume-25-number-2/ph-wounds-during-healing-and-infection-descriptive-literature-review
24. Metcalf DG, Haalboom M, Bowler PG et al. Elevated wound fluid pH correlates with increased risk of wound infection. Wound Medicine 2019. https://research.utwente.nl/en/publications/elevated-wound-fluid-ph-correlates-with-increased-risk-of-wound-i/
25. Wound pH and temperature as predictors of healing: an observational study. J Wound Care 2023. PMID 37094930. https://europepmc.org/article/MED/37094930
26. Assessment of the impact of pH of wound fluid on associated microbial distribution in infected diabetic foot ulcer. J Family Med Prim Care 2025. PMID 40547739. https://europepmc.org/article/MED/40547739
27. McArdle C et al. Diabetic foot ulcer wound fluid: the effects of pH on DFU bacteria and infection. J Foot Ankle Res 2015 (abstract). https://pmc.ncbi.nlm.nih.gov/articles/PMC4416157/
28. Advanced wound dressing for real-time pH monitoring. ACS Sensors 2021. https://pmc.ncbi.nlm.nih.gov/articles/PMC8294608/
29. A wearable wound moisture sensor as an indicator for wound dressing change: an observational study of wound moisture and status. Int Wound J 2015. https://pmc.ncbi.nlm.nih.gov/articles/PMC7950073

**Metabolites and biomarkers**
30. Wound fluid lactate concentration: a helpful marker for diagnosing soft-tissue infection in diabetic foot ulcers? Preliminary findings. Diabet Med 2011. PMID 21219425. https://europepmc.org/article/MED/21219425
31. Elevated uric acid correlates with wound severity. Int Wound J 2012. PMID 21973196. https://europepmc.org/article/MED/21973196
32. Trengove et al. Biochemical analysis of wound fluid from nonhealing and healing chronic leg ulcers. https://research-repository.uwa.edu.au/en/publications/biochemical-analysis-of-wound-fluid-from-non-healing-and-healing-/
33. Electrochemical detection of Pseudomonas in wound exudate samples from patients with chronic wounds. Wound Repair Regen 2016. PMID 26815644. https://europepmc.org/article/MED/26815644
34. Differentiation between infected and non-infected wounds using an electronic nose. Clin Microbiol Infect 2019. PMID 30922929. https://europepmc.org/article/MED/30922929
35. A microfluidic wearable device for wound exudate management and analysis in human chronic wounds. Sci Transl Med 2025. PMID 40267213. https://europepmc.org/article/MED/40267213
36. R&D World coverage of [35]. https://www.rdworldonline.com/smart-bandage-clears-new-hurdle-monitors-chronic-wounds-in-human-patients/
37. Defining a new diagnostic assessment parameter for wound care: elevated protease activity. Wound Repair Regen 2016. PMID 27027492. https://europepmc.org/article/MED/27027492
38. Bacterial protease activity: a prognostic biomarker of early wound infection. J Wound Care 2022. PMID 35404695. https://europepmc.org/article/MED/35404695
39. Bacterial protease activity as a biomarker to assess the risk of non-healing in chronic wounds. Wound Repair Regen 2021. PMID 34057796. https://europepmc.org/article/MED/34057796
40. Rapid enzyme analysis as a diagnostic tool for wound infection. Wound Repair Regen 2015. PMID 25816836. https://europepmc.org/article/MED/25816836
41. Increased matrix metalloproteinase-9 predicts poor wound healing in diabetic foot ulcers. Diabetes Care 2009. PMID 18835949. https://europepmc.org/article/MED/18835949
42. Wound infection detection using a rapid biomarker. Adv Skin Wound Care 2023 (repository record). https://scholarsmine.mst.edu/mec_aereng_facwork/6304

**Oxygenation, impedance, offloading**
43. A systematic review and meta-analysis of tests to predict wound healing in diabetic foot. J Vasc Surg 2016. PMID 26804365. https://europepmc.org/article/MED/26804365
44. Evaluation of diabetic foot ulcer healing with hyperspectral imaging of oxyhemoglobin and deoxyhemoglobin. Diabetes Care 2009. PMID 19641161. https://europepmc.org/article/MED/19641161
45. Weingarten MS et al. Diffuse near-infrared spectroscopy prediction of healing in diabetic foot ulcers (Drexel record). https://researchdiscovery.drexel.edu/esploro/outputs/journalArticle/Diffuse-near-infrared-spectroscopy-prediction-of-healing/991019168676304721
46. Correlation between systemic blood pressure and free flap perfusion: a photoplethysmography study. https://series.publisso.de/en/journals/iprs/volume15/iprs000194
47. Measuring subepidermal moisture to detect early pressure ulcer development: a systematic review. J Wound Care 2022. PMID 36001704. https://europepmc.org/article/MED/36001704
48. Subepidermal moisture is associated with early pressure ulcer damage in nursing home residents with dark skin tones: pilot findings. J Wound Ostomy Continence Nurs 2009. PMID 19448508. https://europepmc.org/article/MED/19448508
49. Bioimpedance measurement based evaluation of wound healing. Physiol Meas 2017. PMID 28248191. https://europepmc.org/article/MED/28248191
50. Bioimpedance sensor array for monitoring chronic wounds: validation of method feasibility. Int Wound J 2024. PMID 39099180. https://pmc.ncbi.nlm.nih.gov/articles/PMC11298616
51. Activity patterns of patients with diabetic foot ulceration. Diabetes Care 2003. PMID 12941724. https://europepmc.org/article/MED/12941724
52. Role and determinants of adherence to off-loading in diabetic foot ulcer healing. Diabetes Care 2016. PMID 27271185. https://europepmc.org/article/MED/27271185
53. Innovative intelligent insole system reduces diabetic foot ulcer recurrence at plantar sites. Lancet Digit Health 2019. PMID 33323253. https://europepmc.org/article/MED/33323253

**Fluorescence and 405 nm light**
54. Diagnostic accuracy of point-of-care fluorescence imaging for the detection of bacterial burden in wounds: results from the 350-patient Fluorescence Imaging Assessment and Guidance trial. https://pmc.ncbi.nlm.nih.gov/articles/PMC7876364/
55. Skin pigmentation impacts the clinical diagnosis of wound infection: imaging of bacterial burden to overcome diagnostic limitations. https://pmc.ncbi.nlm.nih.gov/articles/PMC10933203/
56. Rahma S et al. The use of point-of-care bacterial autofluorescence imaging in the management of diabetic foot ulcers: a pilot randomized controlled trial. Diabetes Care 2022. PMID 35796769. https://europepmc.org/article/MED/35796769
57. Rapid diagnosis of Pseudomonas aeruginosa in wounds with point-of-care fluorescence imaging. https://pmc.ncbi.nlm.nih.gov/articles/PMC7917920/
58. The clinical utility of autofluorescence imaging for bacterial detection in wounds: a systematic review. Int Wound J 2025. PMID 40432492. https://europepmc.org/article/MED/40432492
59. Jones LM et al. In vitro detection of porphyrin-producing wound bacteria with real-time fluorescence imaging. Future Microbiol 2020. https://scholars.ttu.edu/en/publications/in-vitro-detection-of-porphyrin-producing-wound-bacteria-with-rea-2
60. Photoinactivation of Moraxella catarrhalis using 405-nm blue light. Photochem Photobiol 2020. PMID 32105346. https://europepmc.org/article/MED/32105346
61. Antimicrobial action of violet-blue light (405 nm) in ex vivo stored plasma. J Blood Transfus 2016. PMID 27774337. https://europepmc.org/article/MED/27774337

**Measurement bias**
62. Sjoding MW et al. Racial bias in pulse oximetry measurement. N Engl J Med 2020. https://doi.org/10.1056/NEJMc2029240 (numbers read at https://rebelem.com/racial-bias-with-pulse-oximetry)
63. Emory University summary of Bhavani et al., JAMA 2022, temporal vs oral thermometers. https://news.emory.edu/stories/2022/09/hs_bhavani_jama_racial_differences_thermometers_detecting_fevers_06-09-2022/story.html

**Military / austere**
64. Death on the battlefield (2001-2011): implications for the future of combat casualty care. J Trauma Acute Care Surg 2012. PMID 23192066. https://europepmc.org/article/MED/23192066
65. Early infections complicating the care of combat casualties from Iraq and Afghanistan. Surg Infect 2018. PMID 29863446. https://europepmc.org/article/MED/29863446
66. After the battlefield: infectious complications among wounded warriors in the Trauma Infectious Disease Outcomes Study. Mil Med 2019. PMID 31778199. https://europepmc.org/article/MED/31778199
67. Impact of operational theater on combat and noncombat trauma-related infections. Mil Med 2016. PMID 27753561. https://europepmc.org/article/MED/27753561
68. Combat trauma-associated invasive fungal wound infections: epidemiology and clinical classification. Epidemiol Infect 2015. PMID 24642013. https://europepmc.org/article/MED/24642013
69. Invasive mold infections following combat-related injuries. Clin Infect Dis 2012. PMID 23042971. https://europepmc.org/article/MED/23042971
70. Joint Trauma System CPG: Invasive Fungal Infection in War Wounds (ID 28, 17 Jul 2023). https://jts.health.mil/assets/docs/cpgs/Invasive_Fungal_Infection_in_War_Wounds_17_Jul_2023_ID28_v1.1.pdf
71. Joint Trauma System CPG: Extremity Compartment Syndrome and Fasciotomy (ID 17). https://jts.health.mil/assets/docs/cpgs/Extremity_Compartment_Syndrome_and_Fasciotomy_ID17_21_May_2026.pdf
72. Joint Trauma System CPG: Prolonged Casualty Care Guidelines (ID 91). https://learning-media.allogy.com/api/v1/pdf/8b28df78-a36a-4529-8d77-89ae3c2d8b9e/contents
73. Joint Trauma System CPG: Sepsis Management in Prolonged Field Care (ID 83). https://learning-media.allogy.com/api/v1/pdf/3ecdadb8-2a3c-4598-a4f3-8de886a0ac47/contents
74. JBJS OrthoBuzz commentary on Schmidt et al., continuous NIRS for acute compartment syndrome (JBJS 2018). https://orthobuzz.jbjs.org/2018/10/09/new-isnt-always-better/
75. Environmental factors related to fungal wound contamination after combat trauma in Afghanistan, 2009-2011. Emerg Infect Dis 2015. https://wwwnc.cdc.gov/eid/article/21/10/14-1759_article

**Low-resource / tropical**
76. GlobalSurg Collaborative. Surgical site infection after gastrointestinal surgery in high-income, middle-income, and low-income countries. Lancet Infect Dis 2018. https://eprints.whiterose.ac.uk/id/eprint/131496/
77. Rigato M et al. Characteristics, prevalence, and outcomes of diabetic foot ulcers in Africa: a systemic review and meta-analysis. Diabetes Res Clin Pract 2018. PMID 29807105. https://europepmc.org/article/MED/29807105
78. Skin wounds in a rural setting of Côte d'Ivoire: population-based assessment of the burden and clinical epidemiology. PLoS Negl Trop Dis 2022. PMID 36227839. https://europepmc.org/article/MED/36227839
79. WHO fact sheet: Buruli ulcer (12 January 2023). https://www.who.int/news-room/fact-sheets/detail/buruli-ulcer-(mycobacterium-ulcerans-infection)
80. WHO fact sheet: Snakebite envenoming. https://www.who.int/news-room/fact-sheets/detail/snakebite-envenoming
81. WHO fact sheet: Burns (13 October 2023). https://www.who.int/news-room/fact-sheets/detail/burns
82. GSMA. The Mobile Economy Sub-Saharan Africa 2023. https://www.gsma.com/mobileeconomy/wp-content/uploads/2023/10/20231017-GSMA-Mobile-Economy-Sub-Saharan-Africa-report.pdf
83. IEA commentary: access to electricity improves slightly in 2023. https://www.iea.org/commentaries/access-to-electricity-improves-slightly-in-2023-but-still-far-from-the-pace-needed-to-meet-sdg7
84. Adriaans B. The aetiology and pathogenesis of tropical ulcer (thesis, University of Cape Town). https://open.uct.ac.za/handle/11427/25758
