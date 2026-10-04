# C. Therapy hardware constraints for PulsePatch (405 nm light + low-frequency ultrasound)

Compiled 2026-10-03. Scope: doses, power, physical size, purchasable parts, safety limits, and energy budget for the therapy side of the patch.

Evidence tags used throughout:

- `[F]` the source page or datasheet was opened and read during this research session.
- `[S]` the number was seen only in a search-engine extract of the source during this session (page blocked by captcha/403 or not opened). Treat as probable, confirm before relying on it.
- `UNVERIFIED` from memory or an engineering assumption; not seen in a source this session.
- Evidence level is marked as in vitro / animal / human.
- Arithmetic done for this document is labelled "calc".

---

## 0. Parameters summary

| Parameter | Value | Evidence level | Source |
|---|---|---|---|
| 405 nm dose, planktonic S. aureus, 5 log | 36 J/cm² | in vitro | [14] `[S]` |
| 405 nm dose, planktonic P. aeruginosa, 4.2 log | 180 J/cm² | in vitro | [14] `[S]` |
| 400 nm dose, 34 wound isolates, ≥5 log in 71% | 54 to 108 J/cm² (15 to 30 min, implies 60 mW/cm², calc) | in vitro | [17] `[S]` |
| 415 nm dose, P. aeruginosa / A. baumannii biofilm, ~3 log | 432 J/cm² | in vitro | [20] `[F]` |
| 415 nm dose, biofilm in mouse burn, 3 log | 360 to 540 J/cm² | animal | [20] `[F]` |
| 405 nm, MRSA wound, >4 log after 2 daily treatments | 250 J/cm² at 40 mW/cm², 104 min/day, active cooling required | animal (pig) | [22] `[F]` |
| 405 nm, chronic wounds, human | 20 / 60 / 100 J/cm² gave 0.65 / 1.55 / 1.82 log, transient, no healing benefit | human, n = 22 | [23] `[F]` |
| Mammalian cell tolerance, 405 nm | osteoblasts unaffected at 18 J/cm² (5 mW/cm² x 1 h), impaired at 54 J/cm² (15 mW/cm² x 1 h) | in vitro | [25] `[F]`, [26] `[S]` |
| Skin contact limit, applied part, contact ≥ 10 min | 43 °C | standard | [28] `[F]` |
| Skin contact limit, 1 to 10 min / < 1 min | 48 °C / 51 °C (metal) | standard | [28] `[F]` |
| Wearable ultrasound precedent (Drexel) | 20 kHz, 55 kPa, 100 mW/cm² ISPTP, 15 min, ~15 V drive | human pilot, n = 20 and n = 8 | [7][9][10][11] `[F]` |
| MIST / UltraMIST | 40 kHz, 0.1 to 0.5 W/cm² nominal (0.1 to 0.8 in payer summaries), 3 to 20 min, non-contact saline mist | human RCTs | [34][38] `[F]`, [37] `[S]` |
| PZT thickness-mode disc at 40 kHz | about 50 mm thick (calc from N_T = 2005 Hz·m) | physics | [44] `[F]` |
| PZT radial-mode disc at 40 kHz | about 50 to 53 mm diameter (calc from N_P = 1980 to 2130 Hz·m); catalogue 50 mm disc resonates at 44 to 45 kHz | physics + part | [44][45][46] `[F]` |
| Flexural unimorph, purchasable | 15 mm x 1.2 mm, 30 kHz ± 2 kHz, $16.50 | part | [47] `[F]` |
| CLENS (light + ultrasound) | 456 kHz, ~280 kPa, ~80 mW/cm² ISATA, 405 nm at 30 mW/cm²; P. acnes only; in vitro only | in vitro | [1] `[F]` |
| Combination evidence at 20 to 40 kHz | none found | none | section 3 |
| FDA diagnostic output ceiling (Track 3) | derated ISPTA ≤ 720 mW/cm², MI ≤ 1.9 (or ISPPA ≤ 190 W/cm²) | guidance | [29] `[F]` |
| 405 nm LED, 3.5 mm class | 910 to 930 mW typ at 500 mA, Vf 3.3 to 3.4 V, wall-plug ~54 to 56 % (calc) | datasheet | [57][58] `[F]` |
| Energy per session, optimistic | about 272 mWh (74 mAh at 3.7 V) | calc | section 5 |
| Energy per session, conservative | about 1684 mWh (455 mAh at 3.7 V) | calc | section 5 |
| Sessions per 100 mAh / 300 mAh LiPo | optimistic 1 / 3; conservative 0 / 0 | calc | section 5 |

---

## 1. 405 nm antimicrobial light

### 1.1 Reported doses and irradiances

**In vitro, planktonic**

- Maclean et al. 2009 (Strathclyde), 405 nm LED array, suspensions: S. aureus 36 J/cm² for 5 log; MRSA 45 J/cm² for 5 log; C. perfringens 45 J/cm² for 4.4 log; A. baumannii 108 J/cm² for 4.2 log; P. aeruginosa 180 J/cm² for 4.2 log. Gram-positive species were generally more susceptible than Gram-negative. Up to 9 log reduction of S. aureus at high density. [14] (abstract `[F]`; dose table `[S]`, PMC table page was captcha-blocked). The array irradiance was not retrieved.
- Halstead et al. 2016, 400 nm, 34 clinical and type isolates (A. baumannii, P. aeruginosa, S. aureus, E. coli, K. pneumoniae and others): 71 % showed ≥ 5 log reduction after 15 to 30 min, 54 to 108 J/cm². Biofilm seeding was significantly reduced for all isolates. [17] `[S]`
- Leanse et al. 2018 (Dai lab), 405 nm at 100 to 150 mW/cm²: P. aeruginosa 5 log at 144 J/cm²; A. baumannii 4.69 log at 270 J/cm²; E. coli 4.29 log at 576 J/cm². No resistance after 20 serial cycles in vitro. [21] `[F]`
- Sinclair et al. 2024 (Strathclyde): irradiances 0.5 to 150 mW/cm², doses up to 288 J/cm². Lower irradiance was more dose-efficient: 22.5 J/cm² at 5 mW/cm² matched 67.5 J/cm² at 150 mW/cm² for low-density liquid suspensions; ≥ 96 % reductions at ≤ 5 mW/cm². [16] `[F]`

**In vitro, biofilm**

- McKenzie et al. 2013: E. coli biofilms on glass and acrylic, about 140 mW/cm² for 5 to 60 min (calc: 42 to 504 J/cm²), up to 5 log (acrylic) and 7 log (glass). Significant inactivation also for S. aureus, P. aeruginosa, L. monocytogenes biofilms. [15] `[F]`
- Wang et al. 2016 (Dai/Hamblin), 415 nm: 432 J/cm² gave 3.02 to 3.12 log in 24 h and 72 h P. aeruginosa biofilms and 3.18 to 3.59 log in A. baumannii biofilms. [20] `[F]`

**Animal**

- Dai et al. 2013, 415 nm, mouse burn infected with P. aeruginosa: single 55.8 J/cm² exposure 30 min after inoculation cut the bioluminescence area-under-curve about 100-fold and raised survival from 18.2 % to 100 %. No significant skin damage on histology/TUNEL. Bacteria were inactivated about 35-fold faster than keratinocytes in vitro. [18] `[F]`. Note the treatment was applied 30 min after inoculation, before a biofilm matured.
- Dai et al. 2013, 415 ± 10 nm, CA-MRSA in mouse skin abrasions: in vitro 4.75 log bacterial inactivation at 170 J/cm² versus 0.29 log loss of HaCaT keratinocytes. [19] (citation `[F]`, numbers `[S]`)
- Wang et al. 2016: established biofilm in mouse burns needed about 360 J/cm² (24 h old) and 540 J/cm² (48 h old) for 3 log. No apoptotic cells by TUNEL at 540 J/cm². [20] `[F]`
- Leanse et al. 2018: mouse abrasions, 108 and 216 J/cm² at 405 nm. [21] `[F]`
- Negri et al. 2025 (MGH), pig full-thickness wounds with MRSA USA300, 405 nm LED dressing (13 x 18 cm PDMS): 40 mW/cm², 250 J/cm², 104 min daily. More than 4 log reduction after two treatments; 4.7 log CFU/g at 96 h. The first prototype caused thermal damage to skin; a recirculating cooling circuit was added to hold skin at about 35 ± 1 °C while the LED heat sink ran at 65 to 70 °C. The paper states no FDA-registered blue-light device exists for wounds. [22] `[F]`

**Human**

- Plum et al. (Wound Repair and Regeneration, DOI 10.1111/wrr.70180; trial NCT05739058): 22 chronic-wound patients, 405 nm LED, 20 J/cm² (n = 7), 60 J/cm² (n = 8), 100 J/cm² (n = 7), six treatments over two weeks. Immediate reductions of 0.65, 1.55 and 1.82 log; counts rebounded by follow-up; no significant effect on wound healing; no advantage above 60 J/cm². [23] `[F]` (abstract-level). Irradiance was not retrieved.
- McGee et al. 2023: continuous low-irradiance 405 nm phototherapy, 24 h/day for 4 weeks, 25 participants; average wound area reduction 29 %; no adverse events. Irradiance not given in the retrieved text. Uncontrolled pilot. [24] `[F]`
- No randomized controlled human trial showing a clinical infection or healing benefit of 405 nm light in wounds was found.

**Reading of the dose evidence.** Published "36 J/cm² kills S. aureus" figures are planktonic, in vitro. Biofilm and Gram-negative targets need roughly 100 to 500 J/cm². The only human wound data show under 2 log at 60 to 100 J/cm², transient.

### 1.2 Safety

- Mammalian cells (in vitro): osteoblasts unaffected by 5 mW/cm² for 1 h (18 J/cm²); function decreased at 15 mW/cm² for 1 h (54 J/cm²) [25] `[F]`. A follow-up reports no significant viability effect up to 36 J/cm² and significant loss at 54 J/cm², mechanism oxidative (H2O2) [26] `[S]`. In the CLENS paper, 3T3 fibroblasts and primary human keratinocytes showed no significant harm up to 58 J/cm² of 405 nm with ultrasound, assessed at 0 and 24 h [1] `[F]`.
- Animal skin tolerated far higher doses than cultured cells: no TUNEL-positive cells at 540 J/cm² (415 nm, mouse) [20] `[F]`; 250 J/cm² daily in pigs with cooling [22] `[F]`.
- Therapeutic window is real but narrow in vitro: the bactericidal dose for biofilm (hundreds of J/cm²) exceeds the dose that impairs cultured osteoblasts (54 J/cm²). Wound-bed cells (fibroblasts, keratinocytes) are the cells the patch is trying to help.
- ICNIRP 2013 (incoherent visible/IR) [27] `[F]`:
  - Skin: only a thermal limit, H = 2.0 x 10^4 x t^0.25 J/m² for t < 10 s, 380 nm to 3 µm. No limit is given for longer exposures; heat-stress guidance applies. Thermal pain begins above about 45 °C skin temperature.
  - No photochemical skin limit in the visible. Photosensitized skin injury is possible; the porphyria action spectrum has a secondary peak near 400 nm.
  - Retina (blue-light hazard): weighting B(405 nm) = 0.200; aphakic/infant weighting A(405 nm) = 1.30. Limits: radiance dose 1 x 10^6 J/m²/sr for t ≤ 10,000 s; radiance 100 W/m²/sr for t > 10,000 s; small-source irradiance 1 W/m² for exposures longer than 100 s. Worst-case viewing distance 200 mm.
  - Rough estimate (calc): a Lambertian 160 mW source gives about 51 mW/sr on axis, 1.27 W/m² at 200 mm, 0.25 W/m² after B weighting (below 1 W/m²) but 1.65 W/m² with the aphakic/infant weighting (above 1 W/m²). Whether the small-source criterion applies depends on the emitter's angular size; treat this as an order-of-magnitude check. An on-skin interlock for the LEDs is therefore a hardware/firmware requirement.
- Heating: the pig study is direct evidence that an on-skin LED dressing at 40 mW/cm² burned skin without active cooling [22] `[F]`.

### 1.3 Power and time for a 2 cm x 2 cm area (calc)

Optical energy at the wound = dose x 4 cm².

| Target dose | Optical energy | Time at 10 mW/cm² (40 mW) | Time at 40 mW/cm² (160 mW) | Time at 100 mW/cm² (400 mW) |
|---|---|---|---|---|
| 36 J/cm² | 144 J | 60 min | 15 min | 6 min |
| 60 J/cm² | 240 J | 100 min | 25 min | 10 min |
| 100 J/cm² | 400 J | 167 min | 41.7 min | 16.7 min |
| 250 J/cm² | 1000 J | 417 min | 104 min | 41.7 min |

Electrical power. Datasheet wall-plug efficiency at 500 mA, 25 °C: Luminus SST-10-UV 930 mW / (3.3 V x 0.5 A) = 56 %; Lite-On LTPL-C034UVH405 910 mW / (3.4 V x 0.5 A) = 54 % [57][58] `[F]`. System efficiency from battery to wound = LED x optical coupling x driver:

- Optimistic: 0.55 x 0.80 x 0.90 = 0.396, about 0.40 (coupling and driver figures are assumptions, `UNVERIFIED`).
- Conservative: 0.45 (hot junction, no heat sink) x 0.60 x 0.85 = 0.23 (`UNVERIFIED` assumptions).

At 40 mW/cm² on 4 cm²: 160 mW optical needs 0.40 W (optimistic) to 0.70 W (conservative) electrical, 109 to 188 mA from a 3.7 V cell. At 10 mW/cm²: 0.10 to 0.17 W.

Thermal reality check (calc, convection coefficient about 10 W/m²K is `UNVERIFIED`): a 3 x 3 cm patch face at 6 K above ambient-side temperature sheds about 54 mW by natural convection. A continuous 0.4 to 0.7 W therefore relies on the body as the heat sink, under a 43 °C contact limit. Practical choices are low irradiance (5 to 10 mW/cm²) for hours, or pulsed delivery with a skin thermistor in the control loop.

Uniformity (calc): a 130° emitter reaches its half-intensity radius of 10 mm at about 4.7 mm standoff. A thin patch needs either several small emitters (for example a 2 x 2 grid at 10 mm pitch with about 2.3 mm standoff) or a diffusing light guide.

### 1.4 Purchasable 405 nm SMD LEDs

| Part | Package | Radiant flux | Vf | Max current | Wall-plug (calc) | Price | Datasheet |
|---|---|---|---|---|---|---|---|
| Luminus SST-10-UV-A130-G405-00 (400 to 410 nm bin) | 3.5 x 3.5 mm ceramic, 130°, 1.4 °C/W | 930 mW typ at 500 mA (bin G ≥ 900 mW), FWHM 10 nm | 3.3 V typ (2.8 to 4.0) at 500 mA | 1.5 A CW | 56 % | $2.68 at 500 pcs (Future) `[S]` | https://download.luminus.com/datasheets/Luminus_SST-10-UV_Datasheet.pdf `[F]` |
| Lite-On LTPL-C034UVH405 | 3.45 x 3.45 x 2.13 mm `[S]`, 130°, Rth j-c 3 °C/W | 910 mW typ at 500 mA | 3.4 V typ at 500 mA | 700 mA | 54 % | $5.54 (1), $4.14 (10), $3.31 (100) DigiKey `[F]` | https://static.chipdip.ru/lib/706/DOC043706619.pdf `[F]` |
| Würth WL-SUMW 15335340AA350 | 3.5 x 3.5 mm (3535), 130°, 8 K/W | 800 to 1300 mW at 500 mA (binned) | 3.5 V typ (3.2 to 4.2) at 500 mA | 800 mA | 46 to 74 % | not retrieved | https://www.we-online.com/components/products/datasheet/15335340AA350.pdf `[F]` |
| Kingbright ATDS3534UV405B | 3.45 x 3.45 mm | 800 mW `[S]` | 3.4 V `[S]` | 700 mA `[S]`, rated 500 mA `[F]` | not computed | $7.91 DigiKey `[F]` | via https://www.digikey.co.nz/en/product-highlight/k/kingbright/uv-smd-leds |
| Kingbright ATS2012UV405 | 2.0 x 1.25 mm (0805), 20 mA class | not retrieved | about 3.3 V `[S]` | 30 mA `[S]` | unknown | not retrieved | same highlight page `[F]` for series |

Notes: all four high-power parts are sold for UV curing; at the 10 to 40 mA per emitter a patch would use, they run far below rating, which helps efficiency and heat. The Würth datasheet states its parts are not designed or intended for medical use without prior notification to the manufacturer [59] `[F]`.

### 1.5 LED drivers

- TI TPS61165: boost constant-current LED driver, 3 to 18 V input, 38 V open-LED protection, 1.2 A switch, 1.2 MHz, up to 90 % efficiency, 2 x 2 x 0.8 mm 6-pin WSON, PWM/one-wire dimming [61] `[S]`. Suits 2 to 4 LEDs in series (6.6 to 13.6 V) from a single LiPo cell.
- A single 3.3 V LED straddles the LiPo range (3.0 to 4.2 V) and needs a buck-boost or a low-dropout current sink; specific parts were not researched (`UNVERIFIED` territory).

---

## 2. Low-frequency ultrasound for wounds and biofilm

### 2.1 Clinical and lab evidence

**MIST / UltraMIST (non-contact, 40 kHz)**

- Device: 40 kHz; maximum 1.25 W/cm² at 65 µm tip displacement; nominal treatment intensity 0.1 to 0.5 W/cm²; held 0.5 to 1.5 cm from the wound; energy carried by saline mist [34] `[F]`. Payer summaries quote 0.1 to 0.8 W/cm² [37] `[S]`. Treatment 3 to 20 min depending on wound size [38] `[F]`. The system is a generator console with fluid pump, a treatment wand and a disposable applicator [38] `[S]`; it is a clinic device, not a wearable.
- Human outcomes: Ennis 2005 RCT (diabetic foot ulcers, n = 55): 40.7 % vs 14.3 % healed at 12 weeks (p = 0.0366). Kavros 2007 (ischemic ulcers, n = 70): 63 % vs 29 % achieved > 50 % volume reduction at 12 weeks (p < 0.001). Driver 2011 meta-analysis (8 studies, 444 patients): 85.2 % area reduction over a mean 7 weeks; 41.7 % healed by 12 weeks [35] `[F]`. A NICE summary of a 133-patient sham-controlled trial reports 18 % vs 14 % healed, not significant [37] `[S]`. Aetna classifies the therapy as experimental/unproven [35] `[F]`.
- Bacteria (Serena et al. 2009) [34] `[F]`: in vitro, one 5-min application left 33 % of P. aeruginosa, 40 % of E. coli, 27 % of E. faecalis dead, but 1 % of MRSA and 0 % of S. aureus. Pig wounds: ultrasound alone 7.2 to 6.7 log CFU/g over 7 days (sham rose to 8.6). Human pressure ulcers (n = 11, 2 weeks): mean bioburden 4 x 10^7 to 2 x 10^7. These are well under 1 log.

**Contact debridement devices (clinic, cavitational)**

- Söring Sonoca UAW 25 kHz [40] `[S]`; Misonix SonicOne 22.5 kHz, piezo stack in handpiece with titanium tip [39] `[F]`; Arobella Qoustic 35 kHz [40] `[S]`. Mechanism is cavitation and acoustic streaming in saline [41] `[F]`. These are Langevin-horn handpieces driven by console generators; intensity values were not retrieved.

**Biofilm studies (Pitt group, BYU)**

- Rediske et al. 1999, rabbits, E. coli biofilm on implants, 28.48 kHz continuous for 24 h: ultrasound alone had no significant effect on viability (p = 0.80); with gentamicin, 300 mW/cm² gave an extra 2.39 log (p = 0.048) but damaged skin (lesion, scar); 100 mW/cm² gave no significant enhancement; skin stayed below 40 °C at 100 mW/cm² [32] `[F]`. Animal.
- Carmen et al. 2005, rabbits, 28.5 kHz, 500 mW/cm² pulsed 1:3, 24 to 48 h with gentamicin: E. coli extra 2.28 log (p = 0.002); P. aeruginosa no enhancement (0.22 log, p = 0.17; -0.11 log, p = 0.588). No skin abnormality with pulsing [33] `[F]`. Animal.

**Reading.** Low-frequency ultrasound at intensities a patch could deliver does not kill or remove biofilm by itself in the available data. Benefit appears with a co-administered antibiotic, at 300 to 500 mW/cm², for 24 to 48 h, and not for P. aeruginosa. Devices that physically disrupt biofilm do it by cavitation at clinic-console power.

### 2.2 Wearable precedent

**Drexel (Lewin, Samuels, Weingarten, Sunny, Bawiec, Ngo)**

- Samuels et al. 2013 (J Acoust Soc Am 134:1541) [7] `[F]`. Human pilot, 20 venous-ulcer subjects, 4 groups of 5 (sham; 20 kHz 15 min; 20 kHz 45 min; 100 kHz 15 min), up to four sessions alongside standard care. Applicator: four flexural piezo elements, about 35 x 35 x 10 mm, under 100 g, battery-operated, tether-free. Output: 55 kPa, 100 mW/cm² ISPTP, measured by hydrophone 2.5 mm from the face. Drive: tone burst, 1 Hz repetition, 500 ms on (50 % duty). Coupling: sterile gel inside Tegaderm. Result: the 20 kHz 15-min group closed significantly faster (p < 0.03) and all five healed by the fourth session; sham wounds grew 3 % per week on average. Skin temperature rise under 1 °C in 45 min. In vitro: fibroblast metabolism +32 %, proliferation +35 to 40 % at 24 h. Authors note the n = 20 limitation.
- Sunny et al. 2012 [10] `[F]` and Bawiec et al. [11] `[F]`: transducer is a flextensional (cymbal-type) element, a PZT-5H disc with shaped brass caps. For 20 kHz: disc radius 6 to 10 mm, thickness 0.5 mm, cap 0.125 mm brass, cavity depth 0.25 to 0.30 mm. For 100 kHz: radius 3 to 5 mm. Arrays: 2 x 2 = 35 x 35 x 8 mm; 3 x 3 = 55 x 55 x 8 mm. Drive about 15 V (10 to 25 V range) for 55 kPa / 100 mW/cm² ISPTP. Li-polymer battery located away from the applicator. Electrical power and efficiency were not stated in the retrieved text.
- Sunny 2015 dissertation: under 10 mm thick, under 100 g, 10 to 15 V battery drive [12] `[F]`.
- Ngo et al. 2019 (IEEE TUFFC 66:572) and Lewin et al. 2018 abstract: 20 kHz, 40 mm diameter disc applicator under 20 g, 55 kPa, 100 mW/cm² ISPTP, described as non-cavitational and non-thermal. Diabetic ulcer pilot, n = 8: 4.7 weeks to closure vs 12 weeks sham [8][9] `[F]`. A search extract attributes "10 to 12 V rechargeable lithium-ion batteries, total weight under 200 g, up to 4 h between charges" to this group's system [S].
- Claimed mechanism is stimulation of healing (fibroblast activity), not biofilm disruption. No bacterial endpoint was reported in the retrieved material.

**ZetrOZ sam (commercial wearable)**

- 3 MHz, continuous, 0.65 W per applicator, 1.3 W with two applicators, 132 mW/cm² per transducer, 4 h per day, 18,720 J per session, gel coupling patch, separate rechargeable power controller [42] `[F]`, [43] `[S]`. Calc: 0.65 W / 0.132 W/cm² = about 4.9 cm² radiating area; 18,720 J = 5.2 Wh acoustic per session, which is why the battery is a separate pack. It is a musculoskeletal device at 3 MHz, not a low-frequency or wound device.

### 2.3 Transducer physics check

Frequency constants, APC International [44] `[F]`:

| Material | N_T thickness (Hz·m) | N_P planar/radial (Hz·m) |
|---|---|---|
| APC 840 (Navy I) | 2005 | 2130 |
| APC 850 (Navy II) | 2040 | 1980 |
| APC 855 (Navy VI) | 2079 | 1920 |
| APC 880 (Navy III) | 2110 | 2120 |

Resulting dimensions (calc, dimension = N / f):

| Mode | 40 kHz | 20 kHz | 456 kHz (CLENS) |
|---|---|---|---|
| Thickness-mode disc, thickness | 50 to 53 mm | 100 to 106 mm | 4.4 to 4.6 mm |
| Radial-mode disc, diameter | 48 to 53 mm | 96 to 107 mm | 4.2 to 4.7 mm |

Catalogue confirmation: Steminc SMD50T30F45R, 50 mm x 3 mm, radial resonance 44 ± 3 kHz, 7200 pF, ≤ 8 Ω, 280 V recommended max, $34.29 per pair [45] `[F]`; SMD50T21F45R, 50 x 2.1 mm, 45 ± 3 kHz, 10,000 pF, $29.01 per pair [46] `[F]`. Small-disc radial resonances from catalogue titles: 10 x 0.2 mm at 212 kHz, 7 x 0.2 mm at 300 kHz; 20 x 8 mm thickness-type at 255 kHz [49] `[S]`.

Conclusion: a "40 kHz PZT disc" in thickness or radial mode is a 50 mm part. It cannot fit a 2 x 2 cm patch.

Conventional 40 kHz power transducers are larger still: Steminc bolt-clamped Langevin SMBLTD45F40H 53.75 x 45 x 35 mm, 70 W, $47.49 [48] `[S]`; "mini" SMBLTF40W25 59 mm x 25.5 mm, 25 W, 3300 pF, $62.04 [48] `[F]`.

Types that do reach 20 to 40 kHz at patch scale:

- Flexural unimorph discs (piezo bonded to a metal plate). Steminc SMUN15K12F30: 15 mm x 1.2 mm, 30 ± 2 kHz, 6230 pF, ≤ 44 Ω, $16.50; SMUN15MT19F22111: 22 kHz, $28.38 per pair; SMUN38T24F11422: 38 mm, 11 kHz, $75.24 [47] `[F]`. These are characterized in air (listed for sounder/repeller use). Loading by gel and tissue adds mass and damping, lowers the resonance and broadens it; output pressure into tissue is not specified by the vendor and must be measured with a hydrophone.
- Cymbal flextensional elements. Class V flextensional; fundamental flexural resonance tunable from about 5 to 150 kHz in water by size, cap stiffness and cavity design; single elements have high Q and low efficiency [51] `[F]`. A common research geometry is 12.7 mm diameter, 1.0 mm PZT, 0.25 mm caps [51] `[S]`. Not found as a catalogue part; the Drexel devices were custom built [10][11].
- Bimorph benders (Steminc catalogue items sit at 2 to 5 kHz) [47] `[S]`: too low.

Air-coupled 40 kHz ranging transducers: Murata MA40S4S, 9.9 mm diameter, 2550 pF, 20 Vpp max, 120 ± 3 dB SPL at 30 cm with 10 Vrms, open structure, not for outdoor use, listed "not for new designs" by distributors [50] `[S]`. 120 dB SPL is 20 Pa rms; in air that is about 0.1 mW/cm² at 30 cm (calc, air impedance about 415 rayl `UNVERIFIED`). The device is a small bender with a cone matched to air; the open housing would fill with gel, and the element is not built to push against a water-like load. It is not usable as a tissue-coupled therapy source. Compare the Drexel target of 55 kPa.

Pressure/intensity relation used (calc, tissue impedance 1.5 MRayl `UNVERIFIED` standard value): I = p² / (2 x 1.5 x 10^6). 55 kPa gives 100.8 mW/cm², consistent with [7][9].

### 2.4 Drive electronics

| Option | Supply | Output | Package | Fit for 20 to 40 kHz therapy drive |
|---|---|---|---|---|
| TI DRV8662 | 3 to 5.5 V | boost to 105 V, 200 Vpp differential | 4 x 4 x 0.9 mm QFN-20 | No. Built for haptics: amplifier bandwidth 5 kHz at 200 Vpp, 20 kHz only at 50 Vpp with no load; "maximum frequency of 500 Hz"; 400 mA average battery current driving 47 nF at 300 Hz [52] `[F]` |
| TI DRV2667 | 3.3 to 5.5 V | 105 V boost, 200 Vpp, I2C, waveform memory | 4 x 4 mm QFN-20 | No, same 300 Hz-class load ratings [53] `[F]` |
| TI DRV2700 | 3.3 to 5.5 V | 105 V boost, 200 Vpp; flyback to 1 kV | 4 x 4 x 0.9 mm QFN-20 | Same amplifier family; bandwidth not stated on the page retrieved [53] `[F]`. The boost stage alone could serve as an HV rail generator |
| PiezoDrive PDu100 | 3 to 5.5 V | +100 V unipolar or ±100 V bipolar, 15 mA average, 100 mA peak | 11.8 x 12.9 mm module, 560 mg | Marginal. About 60 kHz unloaded bandwidth; 25 mA quiescent; linear output stage. Calc: a 6.2 nF unimorph at 30 kHz and 30 Vpp needs 5.6 mA average (within limit); at 100 Vpp it needs 18.7 mA (over limit) [54] `[F]` |
| Microchip MD1213 + TC6320 | MD1213 4.5 to 13 V, logic 1.8 to 5 V | MD1213: 2 A gate driver, 6 ns edges. TC6320: complementary 200 V, 2 A MOSFET pair, 7 to 8 Ω | MD1213 12-lead QFN; TC6320 8-lead SOIC or DFN | Works as a square-wave half bridge but needs a separate HV rail; designed for MHz imaging pulses [55] `[S]` |
| Microchip HV7355 | logic and ±5 V-class level-shift rails | 8 channels, 0 to +150 V, ±1.5 A | 56-pin VQFN | Overkill for one element [55] `[S]` |
| Boost to 10 to 15 V + small H-bridge + series inductor | single LiPo | 20 to 30 Vpp across element, more with resonant step-up | e.g. TI DRV8837: 0 to 11 V bridge supply, 1.8 A, 280 mΩ, 2 x 2 mm WSON [56] `[S]` | Closest match to the Drexel approach (about 15 V drive) [10][11]. Inductor resonated with the piezo capacitance recovers reactive energy and removes the need for a 100 V rail |

Reactive load (calc): hard-switching a 6.2 nF element at 30 Vpp and 30 kHz costs C·V²·f = 0.17 W before any acoustic output. A resonant inductor is therefore not optional at this power scale.

---

## 3. Combined light + ultrasound ("CLENS")

CLENS = "Coincident Light Energy and Non-focused ultraSound", a trademark of Photosonix Medical, Inc. (Fort Washington, PA) [2][3][4] `[F]`.

**Primary paper.** Schafer ME, McNeely T. "Combining Visible Light and Non-Focused Ultrasound Significantly Reduces Propionibacterium acnes Biofilm While Having Limited Effect on Host Cells." Microorganisms 2021;9(5):929. DOI 10.3390/microorganisms9050929 [1] `[F]`.

| Item | Reported value |
|---|---|
| Ultrasound frequency | 456 kHz ("450 kHz" in the 2015 abstracts) |
| Ultrasound pressure | 280 kPa in the parameter table; 250 and 300 kPa in figure captions |
| Ultrasound intensity | about 80 mW/cm² ISATA.0; stated as "less than 100 mW/cm²" |
| Duty cycle | not stated in the retrieved paper text; a patent extract gives 5 % at 250 kPa [5] `[S]`. Consistent by calc: 280 kPa is about 2.6 W/cm² instantaneous |
| Light | 405 nm, 36 LEDs around the transducer, aimed through an acrylic truncated cone; 30 to 100 mW/cm² |
| Doses | 9 to 144 J/cm², 5 to 30 min |
| Target | 4.45 cm² membrane insert, saline-coupled, chamber at 37 °C |
| Organism | P. acnes ATCC 6919 only, stationary planktonic and biofilm on PET membrane |
| Biofilm result | combined: > 1 log after 5 min (9 J/cm²), > 3 log after 30 min (54 J/cm²); both imply 30 mW/cm² |
| Planktonic result | ultrasound alone: no observable killing in 20 min; 405 nm alone bactericidal; combination reported synergistic |
| Durability | biofilm began regrowing at 48 h and nearly returned to starting density by 96 h |
| Host cells | murine 3T3 fibroblasts and primary human keratinocytes; light 12 to 58 J/cm² with ultrasound; viability at 0 and 24 h after exposure not significantly reduced (one extraction flagged p = 0.05 for keratinocytes at 24 h; check the paper) |
| "FDA-cleared levels" | authors' statement that each energy is within levels previously cleared in other devices. The combination device is not cleared |
| Conflicts | both authors were Photosonix employees; NIH SBIR R43AR067650; seven related patents |
| In vivo | none in the paper |

Corrections to the brief: the "58 J/cm² over 24 h" figure means viability measured up to 24 h after a single exposure, not 24 h of exposure.

**Other CLENS material**

- IEEE IUS 2015 proceeding: 405 nm at 30 mW/cm², ultrasound 450 kHz under 100 mW/cm²; organisms listed as S. epidermidis, S. aureus, P. acnes; > 1 log at 5 min, > 3 log at 30 min; a further 2 log over 24 h; regrowth from 48 h [2] `[F]`.
- Ultrasound Med Biol 2015 supplement abstract: same organisms; 20 min produced "significant cell death"; 60 min released the biofilm from the membrane; no log values [3] `[F]`.
- 2015 dermatology conference abstract: 90 % and 99.94 % P. acnes biofilm kill at 5 and 30 min; "efficacy required the simultaneous application of both energies"; "in vivo data has shown over 90 % reduction in skin surface bacteria in as little as 10 minutes" with no subject count or methods [4] `[F]`.
- 2021 paper: activity against S. aureus, S. epidermidis and E. coli biofilms is "manuscript in preparation" [1] `[F]`. No such paper was found.
- Company material describes the device as investigational and not for sale [6] `[S]`.

**Direct answers**

- Combination at 20 to 40 kHz: no evidence found. Two targeted searches returned only the 450 kHz CLENS work and unrelated ultrasound-plus-antibiotic or light-plus-antibiotic studies.
- Combination against wound pathogens: S. aureus and S. epidermidis appear only in 2015 conference abstracts (no full methods, no peer-reviewed data). P. aeruginosa: no evidence found.
- Combination in vivo: one unsupported sentence in a conference abstract about skin-surface bacteria. No animal wound study and no human trial found.
- Sequential delivery (ultrasound first, then light), as the pitch describes: no evidence found. The only group reporting synergy says simultaneity was required [4].

Design note: 456 kHz corresponds to a PZT disc about 4.4 mm thick or 4.7 mm in diameter (section 2.3), which fits a patch. The pitch's 40 kHz does not.

---

## 4. Safety limits that become requirements

**Skin-contact temperature (IEC 60601-1:2005 Tables 23/24, as reproduced in [28] `[F]`)**

| Applied part contact time | Metal and liquids | Glass, porcelain | Plastic, rubber, wood |
|---|---|---|---|
| t < 1 min | 51 °C | 56 °C | 60 °C |
| 1 min ≤ t < 10 min | 48 °C | 48 °C | 48 °C |
| t ≥ 10 min | 43 °C | 43 °C | 43 °C |

Values are for healthy adult skin. The 41 °C threshold (justification and disclosure required above it for parts not intended to supply heat) is `UNVERIFIED`. Wound-bed and diabetic skin are less tolerant; a design ceiling of 41 °C with a hardware over-temperature cut-off independent of firmware is the defensible requirement. Thermal pain starts near 45 °C [27], and neuropathic patients may not feel it.

**Ultrasound**

- FDA diagnostic guidance [29] `[F]`: Track 3 global maxima derated ISPTA ≤ 720 mW/cm² and MI ≤ 1.9 (or derated ISPPA ≤ 190 W/cm²). Track 1 table: peripheral vessel 720 mW/cm², cardiac 430, fetal and other 94, ophthalmic 17 (MI 0.23). These govern diagnostic imaging in the MHz range. They are a reference point, not the legal limit for a therapeutic low-frequency device.
- MI is unreliable below about 500 kHz; a revised index has been proposed for 20 to 100 kHz [30][31] `[F]`. Calc with the standard definition (MI = peak rarefactional MPa / sqrt(f in MHz), `UNVERIFIED` from memory): Drexel 55 kPa at 20 kHz gives 0.39; MIST 0.5 W/cm² at 40 kHz (122 kPa) gives 0.61; MI 1.9 at 40 kHz would be 380 kPa or about 4.8 W/cm²; CLENS 280 kPa at 456 kHz gives 0.41.
- Cavitation: debridement devices at 22 to 40 kHz cavitate by design [41]. The Drexel devices capped output at 55 kPa and are described as non-cavitational [9]. Continuous 300 mW/cm² at 28 kHz for 24 h injured rabbit skin; 100 mW/cm² did not [32]. A wearable should stay at or below about 100 mW/cm² ISPTP with pulsing until measured otherwise.
- Regulatory class: MIST systems are cleared as ultrasound wound cleaners [38] `[S]`. Limits in IEC 60601-2-5 (physiotherapy ultrasound, 3 W/cm²) and 21 CFR 1050.10 are `UNVERIFIED`.
- Firmware/hardware requirements that follow: closed-loop drive amplitude limit, burst timer with hard maximum session time, coupling detection (impedance or current signature) so the element does not run dry, skin thermistor.

**Light**

- ICNIRP numbers in section 1.2 [27]. Requirements: LEDs enabled only with confirmed skin contact; light-tight patch edge; irradiance and dose counters with a hard dose cap; temperature-gated duty cycling; labeling exclusion for porphyria and photosensitizing drugs.
- IEC 62471 risk-group classification and IEC 60601-2-57 applicability are `UNVERIFIED`.

---

## 5. Energy budget

All figures calc. Area 4 cm². Battery nominal energy = capacity x 3.7 V; usable fraction 0.8 (`UNVERIFIED` assumption covering cutoff, converter loss, ageing).

**Light phase**

- Optimistic: 60 J/cm² (the human dose above which no further benefit was seen [23]). Optical 240 J. System efficiency 0.396 (0.55 x 0.80 x 0.90). Electrical 240 / 0.396 = 606 J = 168 mWh.
- Conservative: 250 J/cm² (pig MRSA protocol [22]). Optical 1000 J. System efficiency 0.23. Electrical 1000 / 0.23 = 4348 J = 1208 mWh.

**Ultrasound phase** (Drexel protocol: 20 kHz, 15 min, 50 % duty [7]). Electro-acoustic efficiency of small flexural/cymbal elements was not found in any source; the values below are assumptions and are the dominant uncertainty.

- Optimistic: spatial-average 50 mW/cm² in the burst x 4 cm² = 0.2 W acoustic; x 0.5 duty = 0.1 W average; transducer 30 % x driver 80 % = 0.24; electrical 0.417 W; x 900 s = 375 J = 104 mWh.
- Conservative: spatial-average 100 mW/cm² x 4 cm² = 0.4 W; x 0.5 = 0.2 W; transducer 15 % x driver 70 % = 0.105; electrical 1.905 W; x 900 s = 1714 J = 476 mWh.

**Totals**

| | Ultrasound | Light | Total | mAh at 3.7 V |
|---|---|---|---|---|
| Optimistic | 104 mWh | 168 mWh | 272 mWh | 74 mAh |
| Conservative | 476 mWh | 1208 mWh | 1684 mWh | 455 mAh |
| Mixed (optimistic ultrasound, 100 J/cm² light at 0.30) | 104 mWh | 370 mWh | 474 mWh | 128 mAh |

**Sessions per charge**

| Cell | Nominal | Usable (0.8) | Optimistic | Mixed | Conservative |
|---|---|---|---|---|---|
| 100 mAh | 370 mWh | 296 mWh | 1.09, so 1 session | 0.62, so 0 | 0.18, so 0 |
| 300 mAh | 1110 mWh | 888 mWh | 3.26, so 3 sessions | 1.87, so 1 | 0.53, so 0 |

**Peak current at 3.7 V**

- Light at 40 mW/cm²: 0.40 to 0.70 W, 109 to 188 mA.
- Ultrasound burst, optimistic: 0.2 / 0.24 = 0.83 W, 225 mA (2.25 C on a 100 mAh cell).
- Ultrasound burst, conservative: 0.4 / 0.105 = 3.8 W, 1.03 A (10 C on 100 mAh, 3.4 C on 300 mAh). Not feasible on a 100 mAh cell.

**Ceiling check.** A 100 mAh cell spent entirely on light delivers at most 296 mWh x 3.6 J/mWh x 0.396 / 4 cm² = about 105 J/cm² (optimistic) or 61 J/cm² (conservative efficiency 0.23). Biofilm-level doses of 250 to 500 J/cm² are outside what a 100 mAh cell can deliver even once.

Housekeeping load (MCU, radio, sensors) is a few percent of these totals and is excluded.

---

## 6. Assumptions in the pitch that look shaky

1. "About 40 kHz PZT disc." A PZT disc resonates at 40 kHz only at about 50 mm diameter (radial) or 50 mm thickness [44][45]. Patch-scale 20 to 40 kHz needs a flexural unimorph or a custom cymbal, both low-efficiency, high-Q parts with no vendor data for tissue loading.
2. "Low-frequency ultrasound disrupts biofilm" at wearable power. The wearable precedent (Drexel) is deliberately non-cavitational and targets healing, with no bacterial endpoint [7][9]. Ultrasound alone did not reduce biofilm viability in vivo [32]; MIST at up to 0.5 W/cm² achieved well under 1 log and nothing on S. aureus in vitro [34]. Biofilm removal in clinics uses cavitating horn devices on mains power.
3. "Ultrasound followed by light." The only combination data used simultaneous delivery and reported that simultaneity was required [4]. No data for sequential use.
4. Borrowing CLENS as support. CLENS is 456 kHz, P. acnes, in vitro, one company-affiliated group, with regrowth by 96 h [1]. Nothing at 20 to 40 kHz, nothing peer-reviewed in wound pathogens, nothing in vivo.
5. "405 nm kills bacteria" at a wearable dose. Planktonic S. aureus needs 36 J/cm²; biofilms and Gram-negatives need 100 to 500 J/cm² [14][20]; humans showed under 2 log, transient, and no healing benefit at 60 to 100 J/cm² [23].
6. Heat. A 40 mW/cm² on-skin LED dressing burned pig skin until active cooling was added [22]. A sealed patch over a wound has a 43 °C limit [28] and almost no convective path.
7. Battery. One optimistic session uses about 74 mAh; a conservative one about 455 mAh. A 100 mAh cell supports one optimistic session and cannot supply the conservative ultrasound burst current.
8. Shared aperture. The piezo element and its caps are opaque. Light and ultrasound cannot both sit directly over the same 2 x 2 cm; CLENS used a ring of 36 LEDs around the transducer and a bulky acrylic cone [1].
9. Host-cell margin. Cultured osteoblasts were impaired at 54 J/cm² [25][26], below biofilm-effective doses. Animal skin tolerated more, but wound-bed cell tolerance in humans at effective doses is not established.
10. Off-the-shelf piezo haptic drivers (DRV8662/DRV2667/DRV2700). They top out near 500 Hz at full swing [52] and cannot drive 20 to 40 kHz.

---

## 7. Unverified items

- IEC 60601-1 clause 11.1.2.2, 41 °C disclosure threshold for applied parts not intended to supply heat.
- IEC 60601-2-5 physiotherapy ultrasound limit (3 W/cm²); 21 CFR 1050.10; IEC 60601-2-57; IEC 62471 risk group for a 405 nm patch.
- Mechanical index definition as used in section 4 calculations.
- Tissue acoustic impedance 1.5 MRayl, air 415 rayl, natural convection about 10 W/m²K.
- Electro-acoustic efficiency of flexural/cymbal elements (15 to 30 % assumed), optical coupling efficiency (60 to 80 % assumed), driver efficiencies, LiPo usable fraction 0.8.
- Maclean 2009 array irradiance; Plum et al. irradiance and publication year; McGee et al. irradiance.
- CLENS duty cycle (5 %) and 250 kPa, seen only in a patent search extract; keratinocyte p = 0.05 at 24 h; the size of the ultrasound-exposed zone within the 4.45 cm² target.
- Drexel battery description (10 to 12 V Li-ion, under 200 g, 4 h) seen only in a search extract; electrical power of the Drexel applicators not found.
- MIST 0.1 to 0.8 W/cm² (payer-policy extract; the fetched primary source says 0.1 to 0.5 W/cm² nominal).
- Package dimensions of MD1213 and HV7355; all `[S]` driver and LED rows in the tables; Kingbright ATS2012UV405 radiant flux; Würth and TPS61165 prices.
- Sonoca and Qoustic frequencies (`[S]`); acoustic intensity of contact debridement devices not found.

---

## 8. Sources

1. Schafer ME, McNeely T. Microorganisms 2021;9(5):929. https://pmc.ncbi.nlm.nih.gov/articles/PMC8146519/
2. Schafer ME, McNeely T. Coincident light/ultrasound therapy to treat bacterial biofilms. IEEE IUS 2015. DOI 10.1109/ULTSYM.2015.0244. https://researchdiscovery.drexel.edu/esploro/outputs/conferenceProceeding/Coincident-Lightultrasound-therapy-to-treat-bacterial/991019176794704721
3. Schafer ME, McNeely T. Ultrasound Med Biol 2015;41(4 Suppl):S63-S64. https://researchdiscovery.drexel.edu/esploro/outputs/abstract/Coincident-LightUltrasound-Therapy-to-Treat-Bacterial/991019695311604721
4. Schafer ME. CLENS: a novel coincident light/ultrasound therapy to treat acne (conference abstract, 2015). https://www.longdom.org/proceedings/clens-a-novel-coincident-lightultrasound-therapy-to-treat-acne-5726.html
5. US Patent 9,649,396 (also 10,207,125; 10,792,510). https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9649396
6. Photosonix Medical profile. https://www.sep.benfranklin.org/partner/photosonix-medical/
7. Samuels JA, Weingarten MS, Margolis DJ, et al. J Acoust Soc Am 2013;134(2):1541-1547. https://pmc.ncbi.nlm.nih.gov/articles/PMC3745491
8. Ngo O, Niemann E, Gunasekaran V, et al. IEEE Trans Ultrason Ferroelectr Freq Control 2019;66(3):572-580. https://researchdiscovery.drexel.edu/esploro/outputs/journalArticle/Development-of-Low-Frequency-20-100-kHz/991014877753704721
9. Lewin PA, Ngo O, et al. J Acoust Soc Am 2018;144(3):1698-1699. https://researchdiscovery.drexel.edu/esploro/outputs/abstract/Low-frequency-20-kHz-patch-like-ultrasound/991019186543004721
10. Sunny Y, Bawiec CR, Nguyen AT, et al. Ultrasonics 2012;52(7):943-948. https://researchdiscovery.drexel.edu/esploro/outputs/journalArticle/Optimization-of-un-tethered-low-voltage-20100kHz/991019168425604721
11. Bawiec CR, Sunny Y, Nguyen AT, et al. Finite element static displacement optimization of 20-100 kHz flexural transducers for fully portable ultrasound applicator. Ultrasonics. https://pmc.ncbi.nlm.nih.gov/articles/PMC3568635
12. Sunny Y. PhD dissertation, Drexel University, 2015. https://researchdiscovery.drexel.edu/esploro/outputs/doctoral/Design-and-optimization-of-flexural-piezoelectric/991014632324204721
13. Drexel news, 2016. https://drexel.edu/now/archive/2016/November/Ultrasound-Wound-Healing-Device/
14. Maclean M, MacGregor SJ, Anderson JG, Woolsey G. Appl Environ Microbiol 2009;75(7):1932-1937. https://strathprints.strath.ac.uk/19234/ ; table https://pmc.ncbi.nlm.nih.gov/articles/PMC2663198/table/t2
15. McKenzie K, Maclean M, et al. Photochem Photobiol 2013;89(4):927-935. https://strathprints.strath.ac.uk/44902/
16. Sinclair LG, Anderson JG, MacGregor SJ, Maclean M. Arch Microbiol 2024;206(6):276. https://strathprints.strath.ac.uk/89262
17. Halstead FD, et al. Appl Environ Microbiol 2016;82(13):4006-4016. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4907187/
18. Dai T, Gupta A, Huang YY, et al. Antimicrob Agents Chemother 2013;57(3):1238-1245. https://scholar.usuhs.edu/en/publications/blue-light-rescues-mice-from-potentially-fatal-pseudomonas-aerugi/
19. Dai T, Gupta A, Huang YY, et al. Photomed Laser Surg 2013;31(11):531-538. https://scholar.usuhs.edu/en/publications/blue-light-eliminates-community-acquired-methicillin-resistant-st/
20. Wang Y, Wu X, Chen J, et al. J Infect Dis 2016;213(9):1380-1387. https://scholar.usuhs.edu/en/publications/antimicrobial-blue-light-inactivation-of-gram-negative-pathogens-/
21. Leanse LG, Harrington OD, Fang Y, et al. Front Microbiol 2018;9:2403. https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2018.02403/full
22. Negri LB, Farinelli W, Korupolu S, et al. J Infect Dis 2025;231(3):e545-e552. https://academic.oup.com/jid/article/231/3/e545/7896367
23. Plum F, Rasul A, Burian EA, et al. Wound Repair Regen. DOI 10.1111/wrr.70180. https://www.citedrive.com/en/discovery/blue-scpledscp-light-attenuates-the-bacterial-bioburden-in-chronic-wounds-transiently-but-dosedependently/ ; https://clinicaltrials.gov/study/NCT05739058
24. McGee SA, White AB, McMullan P, Serena T, Rogers G. J Drugs Dermatol 2023;22(11):1111-1117. https://jddonline.com/articles/dermatology/S1545961623P1111X
25. McDonald RS, Gupta S, Maclean M, et al. Eur Cell Mater 2013;25:204-214. https://www.ecmjournal.org/papers/vol025/vol025a15.php
26. Ramakrishnan P, et al. J Biomed Opt 2014;19(10):105001. https://biomedicaloptics.spiedigitallibrary.org/journals/journal-of-biomedical-optics/volume-19/issue-10/105001/Differential-sensitivity-of-osteoblasts-and-bacterial-pathogens-to-405-nm/10.1117/1.JBO.19.10.105001.full
27. ICNIRP. Guidelines on limits of exposure to incoherent visible and infrared radiation. Health Phys 2013;105(1):74-96. https://www.icnirp.org/cms/upload/publications/ICNIRPVisible_Infrared2013.pdf
28. Advanced Energy application note, maximum allowable temperature (reproduces IEC 60601-1:2005 Tables 23 and 24). https://www.advancedenergy.com/getmedia/8544158d-181a-4083-814e-90ffb75cf298/an_maximum_allowable_temperature.pdf
29. FDA. Marketing Clearance of Diagnostic Ultrasound Systems and Transducers (2023). https://www.fda.gov/media/71100/download
30. Ahmadi F, McLoughlin IV, Chauhan S, ter Haar G. Prog Biophys Mol Biol 2012;108(3):119-138. https://researchers.westernsydney.edu.au/en/publications/bio-effects-and-safety-of-low-intensity-low-frequency-ultrasonic-/
31. Ahmadi F, McLoughlin IV. IEEE EMBC 2013:1964-1967. https://researchers.westernsydney.edu.au/en/publications/a-new-mechanical-index-for-gauging-the-human-bio-effects-of-low-f/
32. Rediske AM, Roeder BL, Brown MK, et al. Antimicrob Agents Chemother 1999;43(5):1211-1214. https://pmc.ncbi.nlm.nih.gov/articles/PMC89135
33. Carmen JC, Roeder BL, Nelson JL, et al. Am J Infect Control 2005;33(2):78-82. https://pmc.ncbi.nlm.nih.gov/articles/PMC1361257
34. Serena TE, Lee SK, Lam K, et al. Ostomy Wound Manage 2009. https://www.hmpgloballearningnetwork.com/site/wmp/content/the-impact-noncontact-nonthermal-low-frequency-ultrasound-bacterial-counts-experimental-and-
35. Aetna Clinical Policy Bulletin 0746, Ultrasound Therapy for Wound Healing. https://www.aetna.com/cpb/medical/data/700_799/0746.html
36. Unger P. Low-frequency, noncontact, nonthermal ultrasound therapy: a review of the literature. 2008. https://www.hmpgloballearningnetwork.com/site/wmp/content/low-frequency-noncontact-nonthermal-ultrasound-therapy-a-review-literature-0
37. BCBSRI policy, Non-Contact Non-Thermal Ultrasound Treatment for Wounds. https://www.bcbsri.com/sites/default/files/polices/NonContact_NonThermal_Ultrasound_Treatment_for_Wounds.pdf ; NICE clinical evidence chapter. https://www.nice.org.uk/guidance/HTG267/chapter/3-clinical-evidence
38. Sanuwave UltraMIST. https://sanuwave.com/products/ultramist ; 510(k) K162721 https://510k.innolitics.com/device/K162721
39. Misonix SonicOne 510(k) K112782. https://fda.innolitics.com/device/K112782
40. Söring UAW trial NCT04633642. https://clinicaltrials.gov/study/NCT04633642 ; Arobella Qoustic. https://www.biospace.com/b-arobella-medical-llc-b-launches-qoustic-wound-therapy-system-tm-product
41. Butcher G. J Foot Ankle Res 2011;4(Suppl 1):P7. https://pmc.ncbi.nlm.nih.gov/articles/PMC3103041/
42. Madzia A, Agrawal C, Jarit P, et al. Open Orthop J 2020;14:176-185. https://pmc.ncbi.nlm.nih.gov/articles/PMC7784557
43. ZetrOZ sam 2.0 510(k) K191568. https://510k.innolitics.com/device/K191568
44. APC International. Physical and Piezoelectric Properties of APC Materials, Rev. 08 (2025). https://americanpiezo.com/wp-content/uploads/2025/04/Physical-and-Piezoelectric-Properties-of-APC-Materials-Rev.-08.pdf
45. Steminc SMD50T30F45R. https://www.steminc.com/PZT/en/piezo-electric-disc-50x3mm-r-45-khz
46. Steminc SMD50T21F45R. https://www.steminc.com/PZT/en/piezo-electric-disc-50x21mm-r-45-khz
47. Steminc SMUN15K12F30. https://www.steminc.com/PZT/en/piezoelectric-unimorph-transducer-disc-15mm-30-khz ; unimorph list https://www.steminc.com/PZT/en/piezo-unimorph-transducer ; bimorph list https://www.steminc.com/PZT/en/producttag/14/piezo-bimorph
48. Steminc Langevin SMBLTD45F40H. https://www.steminc.com/PZT/en/bolt-clamped-langevin-tranducer-40-khz ; SMBLTF40W25 https://www.steminc.com/PZT/en/mini-bolt-clamped-langevin-transducer-40-khz
49. Steminc small discs. https://www.steminc.com/PZT/EN/piezo-transducer-disc-10x02mm-s-212-khz ; https://www.steminc.com/PZT/en/piezo-7x-02mm-wire-lead-300-khz ; https://www.steminc.com/PZT/en/piezoelectric-disc-20x8mm-255-khz-r
50. Murata MA40S4S datasheet. https://www.farnell.com/datasheets/3747890.pdf
51. Newnham RE, Dogan A, Markley DC, et al. Size effects in capped ceramic underwater sound projectors. IEEE Oceans 2002;4:2315-2321. https://pure.psu.edu/en/publications/size-effects-in-capped-ceramic-underwater-sound-projectors/
52. TI DRV8662 datasheet. https://www.ti.com/lit/ds/symlink/drv8662.pdf
53. TI DRV2667. https://www.ti.com/product/DRV2667 ; TI DRV2700. https://www.ti.com/product/DRV2700
54. PiezoDrive PDu100. https://www.piezodrive.com/modules/pdu100-micro-piezo-driver/
55. Microchip MD1213. https://www.hqchip.com/ic/MD1213 ; TC6320. https://radiolocman.com/datasheet/data.html?di=428955 ; HV7355. https://www.radiolocman.com/datasheet/data.html?di=465185
56. TI DRV8837. https://www.radiolocman.com/datasheet/data.html?di=292597
57. Luminus SST-10-UV datasheet. https://download.luminus.com/datasheets/Luminus_SST-10-UV_Datasheet.pdf ; price https://futureelectronics.com/p/semiconductors--optoelectronics--leds/sst-10-uv-a130-g405-00-luminus-devices-2177564
58. Lite-On LTPL-C034UVH405 datasheet. https://static.chipdip.ru/lib/706/DOC043706619.pdf ; DigiKey https://www.digikey.com/en/products/detail/liteon/LTPL-C034UVH405/5414489
59. Würth 15335340AA350 datasheet. https://www.we-online.com/components/products/datasheet/15335340AA350.pdf
60. Kingbright UV SMD LEDs (DigiKey). https://www.digikey.co.nz/en/product-highlight/k/kingbright/uv-smd-leds
61. TI TPS61165. https://www.radiolocman.com/datasheet/data.html?di=171985
