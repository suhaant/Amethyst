"""Build Wound_Patch_ML_Dataset.xlsx from research findings + synthetic data."""

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.chart import LineChart, Reference
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill

from generate_data import P

OUT = "Wound_Patch_ML_Dataset.xlsx"
df = pd.read_csv("data/wound_timeseries.csv")

wb = Workbook(write_only=True)
wb._fonts[0] = Font(name="Arial", size=10)  # default font for all cells

HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(name="Arial", size=10, bold=True, color="FFFFFF")
TITLE_FONT = Font(name="Arial", size=14, bold=True)
BOLD = Font(name="Arial", size=10, bold=True)
BLUE = Font(name="Arial", size=10, color="0000FF")
EV_FILL = {"H": "E2EFDA", "A": "FFF2CC", "V": "DDEBF7", "Model": "FCE4D6"}


def hdr(ws, names):
    ws.append([_c(ws, n, HDR_FONT, HDR_FILL) for n in names])


def _c(ws, v, font=None, fill=None, wrap=False):
    c = WriteOnlyCell(ws, value=v)
    if font:
        c.font = font
    if fill:
        c.fill = fill
    if wrap:
        c.alignment = Alignment(wrap_text=True, vertical="top")
    return c


def widths(ws, ws_widths):
    for col, w in ws_widths.items():
        ws.column_dimensions[col].width = w


# ---------------------------------------------------------------------------
# 1. README
# ---------------------------------------------------------------------------
ws = wb.create_sheet("README")
widths(ws, {"A": 24, "B": 110})
ws.append([_c(ws, "Smart Wound Patch - ML Training Dataset", TITLE_FONT)])
ws.append(["Purpose", "Literature-based reference values + a synthetic, labeled time-series dataset for training a bacterial-infection detector (pH, temperature, moisture)."])
ws.append(["Important", "The time-series data is SIMULATED from published ranges. No public dataset of continuous wound pH/temp/moisture with infection labels exists. Use for proof-of-concept; retrain on real patch/lab data later."])
ws.append([])
ws.append([_c(ws, "Sheet", BOLD), _c(ws, "What it contains", BOLD)])
for s, d in [
    ("Literature_Data", "Every number extracted from published studies: sensor, value, condition, evidence type (Human / Animal / In vitro) and source link."),
    ("Thresholds", "Quick reference: normal vs warning vs infection ranges per sensor, with sources."),
    ("Model_Parameters", "Exact settings the simulator uses and where each came from (source or ASSUMPTION)."),
    ("Cohort_Summary", "Averages by outcome group (live formulas over Wound_Summary)."),
    ("Wound_Summary", "One row per simulated wound (600): type, outcome, infection onset, baseline vs peak sensor values."),
    ("Daily_Trends", "One row per wound per day (8,400): daily mean pH, temperature, impedance, and that day's label."),
    ("Example_Wounds", "Three wounds side by side (healing / stalled / infected) with trend charts."),
    ("Glucose_Participants", "The 16 real people whose Dexcom glucose traces were used (BIG IDEAs Lab, PhysioNet)."),
    ("How_Training_Works", "How labels work, why different patients are OK, and how to collect real labeled data."),
    ("Model_Results", "Random forest results, leave-people-out cross-validation, with vs without glucose."),
    ("Full_Data", "All 403,200 readings (600 wounds x 14 days x every 30 min). This is the training table."),
]:
    ws.append([s, s and d])
ws.append([])
ws.append([_c(ws, "Full_Data column", BOLD), _c(ws, "Meaning", BOLD)])
for s, d in [
    ("wound_id", "Simulated wound / patient ID (0-599). Keep all rows of one wound in the same train or test fold (GroupKFold)."),
    ("hour", "Hours since patch applied (0-335.5, every 0.5 h)."),
    ("ph", "Wound-bed pH reading (includes sensor noise and drift)."),
    ("temp_c", "Skin temperature under the patch, deg C (includes day/night cycle, showers, noise)."),
    ("impedance_kohm", "Moisture signal: electrical impedance at 1 kHz in kOhm. LOWER = wetter / more exudate. Rises as wound heals, drops with infection."),
    ("wound_type", "acute (e.g. surgical) or chronic (e.g. diabetic ulcer)."),
    ("outcome", "healing / stalled (non-healing, no infection) / infected."),
    ("infection_onset_h", "Hour bacteria established (blank if never infected)."),
    ("artifact", "1 if reading is affected by a shower, dressing change, or patch peeling off."),
    ("blood_glucose_mgdl", "REAL Dexcom G6 glucose (mg/dL) from one BIG IDEAs participant, rebuilt from their real days; infection adds a small rise."),
    ("wound_glucose_mM", "Simulated wound-fluid glucose (mM): lags blood ~4 h, lower than blood, and DROPS when bacteria consume it."),
    ("participant_id", "Which real person's glucose trace this wound uses (1-16). Group by this for cross-validation."),
    ("hba1c", "That person's HbA1c (%)."),
    ("label", "Target: normal / warning (first 24 h after onset) / infection (>24 h after onset). Set from the true hidden state, not from sensor values."),
]:
    ws.append([s, d])
ws.append([])
ws.append([_c(ws, "Evidence colors", BOLD)])
for k, d in [("H", "Human clinical study"), ("A", "Animal study"), ("V", "In vitro / bench / device test")]:
    ws.append([_c(ws, k, fill=PatternFill("solid", fgColor=EV_FILL[k])), d])

# ---------------------------------------------------------------------------
# 2. Literature_Data
# ---------------------------------------------------------------------------
LIT = [
    # sensor, measurement, value, units, condition, evidence, study, url
    ("pH", "Intact skin", "5.67 +/- 0.53", "pH", "Healthy", "H", "Multicenter cohort, n=117 (Sci Rep 2026)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("pH", "Acute wound", "6.59 +/- 0.62", "pH", "Normal", "H", "Sci Rep 2026", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("pH", "Chronic wound", "7.11 +/- 0.66", "pH", "Normal", "H", "Sci Rep 2026", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("pH", "Healing wound", "6.82 +/- 0.81", "pH", "Normal", "H", "Sci Rep 2026", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("pH", "Non-healing wound", "7.04 +/- 0.69", "pH", "Normal", "H", "Sci Rep 2026", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("pH", "Non-infected wound", "6.90 +/- 0.88", "pH", "Normal", "H", "Sci Rep 2026", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("pH", "Colonised wound", "7.05 +/- 0.64", "pH", "Warning", "H", "Sci Rep 2026 (not sig. different from non-infected)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("pH", "Infected wound (centre)", "7.53 +/- 0.59", "pH", "Infection", "H", "Sci Rep 2026, n=21 measurements", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("pH", "Infected wound (edge)", "7.57 +/- 0.46", "pH", "Infection", "H", "Sci Rep 2026", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("pH", "Healing trend", "-0.088", "pH / week", "Normal", "H", "Sci Rep 2026 (non-healing -0.03/wk)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("pH", "Phase: inflammation / granulation / epithelialisation", "7.05 / 6.90 / 6.56", "pH", "Normal", "H", "Sci Rep 2026", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("pH", "Spatial: centre / edge / surrounding skin", "7.03 / 7.07 / 6.66", "pH", "Normal", "H", "Sci Rep 2026", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("pH", "DFU healed: bed / edge", "6.28 / 6.47", "pH", "Normal", "H", "DFU cohort n=187", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13097620/"),
    ("pH", "DFU not healed: bed / edge", "7.10 / 7.48", "pH", "Warning", "H", "DFU cohort n=187", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13097620/"),
    ("pH", "DFU healing cutoff", "bed < 6.7 (AUC 0.78)", "pH", "Threshold", "H", "DFU cohort n=187", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13097620/"),
    ("pH", "Infected (no necrosis) vs non-infected", "7.2 vs 6.5", "pH", "Infection", "H", "Metcalf 2019 (cited)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13097620/"),
    ("pH", "Necrotic tissue (lowers pH)", "6.1 +/- 0.6", "pH", "Confounder", "H", "Schneider 2007 (cited)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13097620/"),
    ("pH", "Leg ulcer / critically colonised", "8.9 / 9.25", "pH", "Infection", "H", "Romanelli, Strohal (cited in review)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9493238/"),
    ("pH", "Burns: pH rose before clinical infection signs", "qualitative", "-", "Infection", "H", "Burn exudate study", "https://pubmed.ncbi.nlm.nih.gov/25468471/"),
    ("pH", "Growth outcome", "<=7.6: 30% shrink in 2 wk; >=8.0: wound grew", "pH", "Threshold", "H", "Gethin, n=20", "https://wounds-uk.com/wp-content/uploads/2023/02/content_9150.pdf"),
    ("pH", "Rat S. aureus infection time course", "~7.0 -> 8.0; up by 6 h, rising 4 days", "pH", "Infection", "A", "Su 2024", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11216007/"),
    ("pH", "Diabetic rat MRSA + P. aeruginosa", "rises daily, peaks day 3-4 (figure only)", "-", "Infection", "A", "Gao lab, Sci Adv 2023", "https://www.science.org/doi/10.1126/sciadv.adf7388"),
    ("pH", "Rat burns day 1 / 2 / 3", "7.5 / 8.0-8.2 / 7.8", "pH", "Infection", "A", "Colorimetric dressing", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10275586"),
    ("pH", "Horse inoculation effect", "none (p=0.75)", "-", "Confounder", "A", "Equine wound model", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6709944/"),
    ("pH", "P. aeruginosa culture", "6.5 -> 9.0 over 18 h (unverified)", "pH", "Infection", "V", "Review (paywalled)", "https://www.tandfonline.com/doi/full/10.1080/05704928.2018.1558232"),
    ("pH", "S. aureus culture", "dips to 6.0 at 8 h, ~7.0 at 18 h (unverified)", "pH", "Infection", "V", "Review (paywalled)", "https://www.tandfonline.com/doi/full/10.1080/05704928.2018.1558232"),
    ("pH", "Classifier ranges", "normal 4-6 / warning 6-7.5 / infection 7.5-9", "pH", "Threshold", "V", "Nano-Micro Lett 2025 (restated, not validated)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12222607/"),
    ("pH", "Sensor drift", "< 0.04", "pH / h", "Sensor", "V", "Su 2024", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11216007/"),
    ("pH", "Sensor sensitivity (PANI)", "59.7 (drops to ~20 above pH 8)", "mV / pH", "Sensor", "V", "Gao 2023; M-PANI study", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11647034/"),
    ("pH", "Clinical meter accuracy", "+/- 0.1 to 0.2", "pH", "Sensor", "H", "Sci Rep 2026; DFU study", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("Temperature", "Wound centre non-infected vs colonised", "28.66 vs 29.04", "deg C", "Normal", "H", "Sci Rep 2026 (no sig. difference)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("Temperature", "Healing trend", "-0.19 (healing), -0.09 (all)", "deg C / week", "Normal", "H", "Sci Rep 2026", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13035947/"),
    ("Temperature", "Healthy left-right difference", "0.3 - 0.4", "deg C", "Normal", "H", "Thermography norms (secondary)", "https://www.researchgate.net/publication/216015612"),
    ("Temperature", "Non-infected wound vs healthy skin", "+1.1 to 1.2", "deg C", "Normal", "H", "Chanmugam 2017, n=6", "https://pubmed.ncbi.nlm.nih.gov/28817451/"),
    ("Temperature", "Inflammation vs healthy skin", "+1.5 to 2.2", "deg C", "Warning", "H", "Chanmugam 2017", "https://pubmed.ncbi.nlm.nih.gov/28817451/"),
    ("Temperature", "Infection vs healthy skin", "+4 to 5", "deg C", "Infection", "H", "Chanmugam 2017", "https://pubmed.ncbi.nlm.nih.gov/28817451/"),
    ("Temperature", "Periwound vs other limb, infection cutoff", "> 1.1 (2 deg F)", "deg C", "Threshold", "H", "Fierheller & Sibbald 2010", "https://dx.doi.org/10.1097/01.ASW.0000383197.28192.98"),
    ("Temperature", "Deep infection sign (STONEES)", ">= 1.7 (3 deg F)", "deg C", "Threshold", "H", "Sibbald 2015", "https://doi.org/10.1097/01.ASW.0000458991.58947.6b"),
    ("Temperature", "Diabetic foot infection cutoff", "2.15 (sens 88.9%, spec 61.5%, AUC 0.85)", "deg C", "Threshold", "H", "n=97", "https://pubmed.ncbi.nlm.nih.gov/32812820/"),
    ("Temperature", "Foot complication cutoff", "2.2 (sens 76%, spec 40%)", "deg C", "Threshold", "H", "van Netten 2014", "https://pubmed.ncbi.nlm.nih.gov/25098361/"),
    ("Temperature", "Infected foot vs other foot", "~1.6 (very high variance)", "deg C", "Infection", "H", "SIDESTEP trial, n=332", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7951616/"),
    ("Temperature", "Per extra bacterial species", "+0.95", "deg C", "Infection", "H", "Venous ulcers n=57 (secondary)", "https://onlinelibrary.wiley.com/doi/abs/10.1111/wrr.12781"),
    ("Temperature", "Temp vs clinician infection rating", "r = 0.32", "-", "Confounder", "H", "Collins 2025, 268 wounds", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12315627/"),
    ("Temperature", "C-section wound gradient SSI vs no SSI (day 7)", "1.92 vs 1.09", "deg C", "Infection", "H", "n=50; signal 11-16 days before diagnosis", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6323776/"),
    ("Temperature", "Early post-op infected wounds", "COOLER on days 1-2", "-", "Confounder", "H", "Stoma closure n=60", "https://pubmed.ncbi.nlm.nih.gov/30791157/"),
    ("Temperature", "Normal post-op peak (hip/knee)", "+3.1 to 4.4 at day 3; 0 by day 90", "deg C", "Normal", "H", "Arthroplasty", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3102809/"),
    ("Temperature", "Pig infection time course", "~40 within 48 h of inoculation", "deg C", "Infection", "A", "Pang 2020", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7080536/"),
    ("Temperature", "Rabbit infected vs control", "38.5 (S. aureus) vs 37; peak day 4-6", "deg C", "Infection", "A", "Rabbit model", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8313280/"),
    ("Temperature", "Rabbit implant infection", "+0.8 to 1.5; peak day 4", "deg C", "Infection", "A", "Rabbit spinal implant", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8820007/"),
    ("Temperature", "Rat S. aureus", "32.5 -> 33.7", "deg C", "Infection", "A", "Su 2024", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11216007/"),
    ("Temperature", "Day/night cycle (wrist)", "1.16 - 1.44 peak-to-peak", "deg C", "Confounder", "H", "iButton study", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11353769/"),
    ("Temperature", "Water on skin (shower)", "~ -3.5, recovers ~30 min", "deg C", "Confounder", "H", "Sensor demo (secondary)", "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4476093/"),
    ("Temperature", "Sensor accuracy (MAX30205)", "+/- 0.1", "deg C", "Sensor", "V", "Datasheet", "https://www.analog.com/media/en/technical-documentation/data-sheets/MAX30205.pdf"),
    ("Glucose", "Normal CGM, non-diabetic (Dexcom G6)", "mean 99 +/- 7; CV 17%; 96% time 70-140", "mg/dL", "Healthy", "H", "Shah 2019, n=153", "https://academic.oup.com/jcem/article/104/10/4356/5479355"),
    ("Glucose", "Non-diabetic inpatients with infection", "mean ~103; CV 18%; 33% had a spike >180", "mg/dL", "Infection", "H", "CGM study, n=90", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12952634/"),
    ("Glucose", "Type 1 diabetes before vs during infection", "160 -> 175.5 (+15); CV 37.3 -> 39.6%", "mg/dL", "Infection", "H", "COVID, n=32 adults", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8418789/"),
    ("Glucose", "Children T1D around infection", "159 -> 179 during -> back in 2 wk", "mg/dL", "Infection", "H", "n=18", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11917402"),
    ("Glucose", "Infection risk vs post-op glucose", "OR 1.07 per +10 mg/dL; >180 OR 2.0", "-", "Risk factor", "H", "SCOAP (via Lee 2014 review)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4242425"),
    ("Glucose", "SSI risk by glucose band (vs <=110)", "111-140 OR 3.6; 141-180 OR 6.3; >220 OR 12.1", "-", "Risk factor", "H", "Ata 2010", "https://jamanetwork.com/journals/jamasurgery/fullarticle/406267"),
    ("Glucose", "Infection risk per 40 mg/dL", "+30% (OR 1.3)", "-", "Risk factor", "H", "Ramos 2008", "https://pubmed.ncbi.nlm.nih.gov/18936571/"),
    ("Glucose", "High glucose variability after surgery", "SSI OR 3.22", "-", "Risk factor", "H", "Spinal fusion", "https://www.ovid.com/jnls/spinejournal/abstract/10.1097/brs.0000000000004214"),
    ("Glucose", "Wound-fluid glucose after infection", "drops > 35%", "%", "Infection", "A", "Gao lab, Sci Adv 2023 (diabetic mice)", "https://www.science.org/doi/10.1126/sciadv.adf7388"),
    ("Glucose", "Wound fluid lags blood glucose", "~4 h", "hours", "Sensor", "A", "Gao lab, Sci Adv 2023", "https://www.science.org/doi/10.1126/sciadv.adf7388"),
    ("Glucose", "Pig S. aureus wounds", "wound glucose undetectable (bacteria consume it)", "-", "Infection", "A", "Hirsch 2008", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2276479/"),
    ("Glucose", "Human wound fluid vs serum", "wound glucose LOWER than blood", "-", "Normal", "H", "Trengove 1996, 8 ulcers", "https://onlinelibrary.wiley.com/doi/10.1046/j.1524-475X.1996.40211.x"),
    ("Glucose", "Wound lactate (bacteria byproduct)", "median 21 mM; higher if infected", "mM", "Infection", "H", "Loffler 2011, DFU", "https://pubmed.ncbi.nlm.nih.gov/21219425"),
    ("Moisture", "Leg ulcer exudate", "0.17-0.21 (Dealey); 0.43-0.63 (Thomas)", "g/cm2/24h", "Normal", "H", "WUWHS 2019 consensus", "https://woundsinternational.com/wp-content/uploads/2023/02/836aed9753c3d8e3d8694bcaee336395.pdf"),
    ("Moisture", "Granulating wound exudate", "0.51", "g/cm2/24h", "Normal", "H", "WUWHS 2019", "https://woundsinternational.com/wp-content/uploads/2023/02/836aed9753c3d8e3d8694bcaee336395.pdf"),
    ("Moisture", "Open wound evaporation", "214 +/- 8.4", "g/m2/h", "Normal", "H", "Lamke 1977", "https://www.sciencedirect.com/science/article/abs/pii/0305417977900043"),
    ("Moisture", "Intact skin water loss (TEWL)", "11 - 14", "g/m2/h", "Healthy", "H", "Review", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12359141/"),
    ("Moisture", "Fresh wound water loss", "96.9 -> 14.6 by day 14", "g/m2/h", "Normal", "H", "Review", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11464781/"),
    ("Moisture", "Mouse exudate rate", "~2", "uL/cm2/h", "Normal", "A", "iCares", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12173118/"),
    ("Moisture", "Humidity under dressing", "95 - 100 (any wound)", "% RH", "Confounder", "V", "Patent measurement", "https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8438940"),
    ("Moisture", "WoundSense readings", "44.9% optimal / 26% wet / 29.1% dry", "% of readings", "Normal", "H", "Milne 2016, 30 pts", "https://strathprints.strath.ac.uk/55516/1/Milne_etal_IWJ_2015_A_wearable_wound_moisture_sensor_as_an_indicator_for_wound_dressing_change_an_observational_study.pdf"),
    ("Moisture", "Impedance intact skin @ 1 kHz", "58.6", "kOhm", "Healthy", "H", "Kekonen 2019", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6603574/"),
    ("Moisture", "Impedance fresh wound @ 1 kHz", "6.3 (recovers over ~142 h)", "kOhm", "Normal", "H", "Kekonen 2019", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6603574/"),
    ("Moisture", "Impedance change with healing", "R +11%, X +90%, phase +50%", "%", "Normal", "H", "Lukaski & Moore 2012 (review)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12162137/"),
    ("Moisture", "Impedance with infection", "DECREASES (size not published)", "-", "Infection", "H", "Lukaski & Moore 2012; Stanford bandage", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12162137/"),
    ("Moisture", "Extra day of drainage after joint surgery", "+42% (hip) / +29% (knee) infection risk", "% per day", "Infection", "H", "Patel 2007", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6728765"),
    ("Moisture", "Sudden exudate increase", "infection sign (qualitative)", "-", "Infection", "H", "IWII 2022 consensus", "https://woundsinternational.com/wp-content/uploads/2023/05/IWII-CD-2022-web.pdf"),
    ("Moisture", "Infected burns", "more exudate (qualitative)", "-", "Infection", "A", "Rat P. aeruginosa", "https://www.nature.com/articles/s41598-019-50003-8"),
    ("Moisture", "S. aureus detectable by impedance", ">= 10^8 CFU/mL", "CFU/mL", "Sensor", "V", "Farrow 2012", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4263571/"),
    ("Moisture", "Capacitive sensor pressure / bending error", "~13% / up to 20%", "%", "Sensor", "V", "Farooqui 2016", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4926082/"),
]
ws = wb.create_sheet("Literature_Data")
widths(ws, {"A": 6, "B": 13, "C": 44, "D": 38, "E": 14, "F": 12, "G": 10, "H": 44, "I": 70})
ws.freeze_panes = "A2"
hdr(ws, ["#", "Sensor", "Measurement", "Value", "Units", "Condition", "Evidence", "Study / context", "Source URL"])
for i, r in enumerate(LIT, 1):
    fill = PatternFill("solid", fgColor=EV_FILL[r[5]])
    ws.append([i, r[0], r[1], r[2], r[3], r[4], _c(ws, r[5], fill=fill), r[6], r[7]])

# ---------------------------------------------------------------------------
# 3. Thresholds
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Thresholds")
widths(ws, {"A": 26, "B": 26, "C": 26, "D": 26, "E": 70})
ws.append([_c(ws, "Quick reference - what the numbers mean", TITLE_FONT)])
ws.append([])
hdr(ws, ["Sensor", "Normal / healing", "Warning", "Infection", "Basis"])
for r in [
    ("pH (wound bed)", "6.3 - 6.9, slowly falling", "7.0 - 7.4 or rising", ">= 7.5, or +0.5 above own baseline", "Sci Rep 2026 cohort (infected 7.53 vs non-infected 6.90); DFU cutoff 6.7"),
    ("Temperature rise vs baseline", "< +0.5 deg C", "+0.5 to +1.1 deg C", ">= +1.1 deg C sustained (>= 2.2 = strong)", "Fierheller 2 deg F; diabetic foot 2.15 deg C cutoff; Chanmugam +4-5 severe"),
    ("Impedance (moisture) vs baseline", "Rising slowly (drying / healing)", "Flat or -10 to -20%", "Falling >= 20-30% (wetter)", "Direction from Lukaski 2012 / Stanford; size is an ASSUMPTION"),
    ("Timing", "-", "First 6-24 h after bacteria arrive", "Peaks 2-4 days after onset", "Rat/pig/rabbit models (Gao 2023, Pang 2020, Su 2024)"),
]:
    ws.append(list(r))
ws.append([])
ws.append([_c(ws, "Rule: no single sensor is reliable alone (temperature specificity 36-62% in humans; pH of colonised and clean wounds overlaps). Combine all three and judge vs each patient's own day-1 baseline.", BOLD)])

# ---------------------------------------------------------------------------
# 4. Model_Parameters
# ---------------------------------------------------------------------------
BASIS = {
    "ph_base": "Sci Rep 2026: acute 6.59, chronic 7.11 (SD narrowed to 0.45)",
    "ph_slope_per_day": "Sci Rep 2026: -0.088/wk healing, -0.03/wk non-healing",
    "ph_infection_rise": "Sci Rep 2026: infected 7.53 vs non-infected 6.90",
    "ph_nonresponder_frac": "ASSUMPTION (horse study: no pH change; necrosis lowers pH)",
    "ph_staph_dip": "In vitro S. aureus early acidification (unverified)",
    "ph_noise": "ASSUMPTION (meters +/-0.1-0.2)",
    "ph_drift_per_h": "ASSUMPTION (bench drift up to 0.04/h)",
    "temp_base": "Covered skin ~33-35 deg C",
    "temp_slope_per_day": "Sci Rep 2026: -0.19/wk healing, -0.09/wk all",
    "temp_infection_rise": "Fierheller 1.1, SIDESTEP 1.6, foot cutoff 2.15 deg C",
    "temp_circadian_half_amp": "Wrist 1.2-1.4 deg C peak-to-peak; damped under dressing (ASSUMPTION)",
    "temp_circadian_peak_hour": "Distal skin peaks at night",
    "temp_noise": "MAX30205 +/-0.1 deg C",
    "shower_temp_drop": "Water on skin ~-3.5 deg C",
    "shower_prob_per_day": "ASSUMPTION",
    "z_base": "Kekonen 2019: fresh wound 6.3 kOhm @1 kHz",
    "z_log_growth_per_day": "ASSUMPTION (direction: impedance rises with healing)",
    "z_infection_drop": "ASSUMPTION (direction: impedance drops with infection)",
    "z_noise_frac": "ASSUMPTION",
    "z_shower_frac": "ASSUMPTION",
    "lag_h": "Rat: pH up by 6 h; signals within 24 h (iCares)",
    "time_to_peak_h": "Animal models: peak day 2-4",
    "dressing_change_h": "Milne 2016: DFU ~every 3 days",
    "detach_prob_per_wound": "ASSUMPTION",
    "detach_duration_h": "ASSUMPTION",
    "ambient_temp": "Room temperature",
    "frac_chronic": "Design choice",
    "frac_infected": "Design choice",
    "frac_stalled_of_uninfected": "Design choice",
    "staph_frac_of_infected": "Sci Rep 2026: S. aureus in 6/11 cultures",
    "glucose_or_per_10": "SCOAP: OR 1.07 per +10 mg/dL",
    "glucose_ref_mgdl": "Reference level for the odds ratio",
    "blood_glucose_rise": "+4 (non-diabetic) to +15-20 mg/dL (T1D) during infection",
    "glucose_spike_amplify": "CV 37.3 -> 39.6% during infection (T1D)",
    "wound_glucose_lag_h": "Gao 2023: wound fluid lags blood ~4 h",
    "wound_serum_ratio": "ASSUMPTION (direction: wound < serum, Trengove 1996)",
    "wound_glucose_drop": "Gao 2023: >35% drop after infection",
    "wound_glucose_noise_frac": "ASSUMPTION",
}
ws = wb.create_sheet("Model_Parameters")
widths(ws, {"A": 30, "B": 40, "C": 80})
ws.append([_c(ws, "Simulator settings (generate_data.py). Blue = input you can change in the script.", BOLD)])
hdr(ws, ["Parameter", "Value", "Basis / source"])
for k, v in P.items():
    b = BASIS.get(k, "")
    ws.append([k, _c(ws, str(v), BLUE), _c(ws, b, Font(name="Arial", size=10, color="C00000") if "ASSUMPTION" in b else None)])

# ---------------------------------------------------------------------------
# Per-wound and daily aggregates
# ---------------------------------------------------------------------------
clean = df[~df["artifact"]].copy()
clean["day"] = (clean["hour"] // 24).astype(int) + 1
daily = (clean.groupby(["wound_id", "day"])
         .agg(ph=("ph", "mean"), temp_c=("temp_c", "mean"), impedance_kohm=("impedance_kohm", "mean"),
              blood_glucose_mgdl=("blood_glucose_mgdl", "mean"), wound_glucose_mM=("wound_glucose_mM", "mean"),
              outcome=("outcome", "first"), wound_type=("wound_type", "first"),
              label=("label", lambda s: s.value_counts().idxmax()))
         .reset_index())
art = df.assign(day=(df["hour"] // 24).astype(int) + 1).groupby(["wound_id", "day"])["artifact"].sum()
daily = daily.merge(art.rename("artifact_readings").reset_index(), on=["wound_id", "day"], how="left")

first = df.groupby("wound_id").first()
gmean = df.groupby("wound_id")["blood_glucose_mgdl"].mean()
d1 = daily[daily.day == 1].set_index("wound_id")
later = daily[daily.day >= 2].groupby("wound_id")

# ---------------------------------------------------------------------------
# 5. Cohort_Summary (formulas over Wound_Summary)
# ---------------------------------------------------------------------------
N = len(first)
last = N + 1
ws = wb.create_sheet("Cohort_Summary")
widths(ws, {"A": 34, "B": 14, "C": 14, "D": 14, "E": 14})
ws.append([_c(ws, "Cohort summary - averages by outcome (live formulas)", TITLE_FONT)])
ws.append([])
hdr(ws, ["Metric", "healing", "stalled", "infected", "All"])
rng = lambda col: f"Wound_Summary!${col}$2:${col}${last}"
out = rng("C")
ws.append(["Number of wounds"] + [f'=COUNTIFS({out},"{g}")' for g in ["healing", "stalled", "infected"]] + [f"=COUNTA({out})"])
for name, col in [("Day-1 pH", "F"), ("Peak daily pH", "G"), ("pH rise (peak - day 1)", "H"),
                  ("Day-1 temperature (deg C)", "I"), ("Peak daily temperature (deg C)", "J"),
                  ("Temperature rise (deg C)", "K"), ("Day-1 impedance (kOhm)", "L"),
                  ("Lowest daily impedance (kOhm)", "M"), ("Impedance change, lowest vs day 1", "N"),
                  ("Final-day impedance (kOhm)", "O"),
                  ("Mean blood glucose (mg/dL, real CGM)", "S"),
                  ("Day-1 wound glucose (mM)", "T"), ("Lowest daily wound glucose (mM)", "U"),
                  ("Wound glucose change, lowest vs day 1", "V")]:
    ws.append([name] + [f'=AVERAGEIFS({rng(col)},{out},"{g}")' for g in ["healing", "stalled", "infected"]]
              + [f"=AVERAGE({rng(col)})"])
ws.append([])
ws.append([_c(ws, "Read across the 'infected' column: pH and temperature rise more and impedance drops, while healing wounds stay flat or improve.", BOLD)])

# ---------------------------------------------------------------------------
# 6. Wound_Summary
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Wound_Summary")
widths(ws, {c: 15 for c in "ABCDEFGHIJKLMNOPQRSTUV"})
ws.freeze_panes = "A2"
hdr(ws, ["wound_id", "wound_type", "outcome", "infection_onset_h", "onset_day", "day1_ph", "peak_daily_ph",
         "ph_rise", "day1_temp_c", "peak_daily_temp_c", "temp_rise_c", "day1_impedance_kohm",
         "min_daily_impedance_kohm", "impedance_change_pct", "final_impedance_kohm", "artifact_readings",
         "participant_id", "hba1c", "mean_blood_glucose_mgdl", "day1_wound_glucose_mM",
         "min_daily_wound_glucose_mM", "wound_glucose_change_pct"])
for i, wid in enumerate(first.index, start=2):
    g = later.get_group(wid)
    onset = first.loc[wid, "infection_onset_h"]
    ws.append([
        int(wid), first.loc[wid, "wound_type"], first.loc[wid, "outcome"],
        None if pd.isna(onset) else float(onset),
        f'=IF(D{i}="","",ROUNDDOWN(D{i}/24,0)+1)',
        round(d1.loc[wid, "ph"], 3), round(g["ph"].max(), 3), f"=G{i}-F{i}",
        round(d1.loc[wid, "temp_c"], 2), round(g["temp_c"].max(), 2), f"=J{i}-I{i}",
        round(d1.loc[wid, "impedance_kohm"], 2), round(g["impedance_kohm"].min(), 2), f"=M{i}/L{i}-1",
        round(g["impedance_kohm"].iloc[-1], 2), int(df.loc[df.wound_id == wid, "artifact"].sum()),
        int(first.loc[wid, "participant_id"]), float(first.loc[wid, "hba1c"]),
        round(gmean.loc[wid], 1), round(d1.loc[wid, "wound_glucose_mM"], 2),
        round(g["wound_glucose_mM"].min(), 2), f"=U{i}/T{i}-1",
    ])

# ---------------------------------------------------------------------------
# 7. Daily_Trends
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Daily_Trends")
widths(ws, {c: 16 for c in "ABCDEFGHIJK"})
ws.freeze_panes = "A2"
cols = ["wound_id", "day", "wound_type", "outcome", "label", "ph", "temp_c", "impedance_kohm",
        "blood_glucose_mgdl", "wound_glucose_mM", "artifact_readings"]
hdr(ws, ["wound_id", "day", "wound_type", "outcome", "label (most of day)", "mean_ph", "mean_temp_c",
         "mean_impedance_kohm", "mean_blood_glucose_mgdl", "mean_wound_glucose_mM", "artifact_readings"])
for r in daily[cols].round({"ph": 3, "temp_c": 2, "impedance_kohm": 2, "blood_glucose_mgdl": 1, "wound_glucose_mM": 2}).itertuples(index=False):
    ws.append(list(r))

# ---------------------------------------------------------------------------
# 8. Example_Wounds (hourly, with charts)
# ---------------------------------------------------------------------------
w_heal = first[(first.outcome == "healing") & (first.wound_type == "chronic")].index[0]
w_stall = first[(first.outcome == "stalled") & (first.wound_type == "chronic")].index[0]
inf = first[(first.outcome == "infected") & (first.wound_type == "chronic")]
w_inf = (inf["infection_onset_h"] - 120).abs().idxmin()      # onset near day 5
ex_ids = [w_heal, w_stall, w_inf]
ex = {w: df[(df.wound_id == w) & (df.hour % 1 == 0)].reset_index(drop=True) for w in ex_ids}

ws = wb.create_sheet("Example_Wounds")
widths(ws, {c: 13 for c in "ABCDEFGHIJKLMNOPQ"})
ws.freeze_panes = "B4"
onset_h = first.loc[w_inf, "infection_onset_h"]
ws.append([_c(ws, f"Hourly readings: healing wound #{w_heal}, stalled wound #{w_stall}, infected wound #{w_inf} "
                  f"(bacteria established at hour {onset_h:.0f} = day {onset_h / 24:.1f}). Spikes = showers / dressing changes.", BOLD)])
ws.append([None, "pH", None, None, "Temperature (deg C)", None, None, "Impedance (kOhm)", None, None, "Infected label", "Blood glucose (mg/dL)", None, None, "Wound glucose (mM)"])
hdr(ws, ["hour", "healing", "stalled", "infected", "healing", "stalled", "infected",
         "healing", "stalled", "infected", "label", "healing", "stalled", "infected",
         "healing", "stalled", "infected"])
n_ex = len(ex[w_heal])
for j in range(n_ex):
    ws.append([float(ex[w_heal].hour[j])]
              + [float(ex[w].ph[j]) for w in ex_ids]
              + [float(ex[w].temp_c[j]) for w in ex_ids]
              + [float(ex[w].impedance_kohm[j]) for w in ex_ids]
              + [ex[w_inf].label[j]]
              + [float(ex[w].blood_glucose_mgdl[j]) for w in ex_ids]
              + [float(ex[w].wound_glucose_mM[j]) for w in ex_ids])
x = Reference(ws, min_col=1, min_row=4, max_row=3 + n_ex)
for k, (title, ytitle, c0, anchor) in enumerate([("pH over 14 days", "pH", 2, "S2"),
                                                  ("Temperature over 14 days", "deg C", 5, "S20"),
                                                  ("Impedance (moisture) over 14 days", "kOhm", 8, "S38"),
                                                  ("Blood glucose (real CGM) over 14 days", "mg/dL", 12, "S56"),
                                                  ("Wound-fluid glucose over 14 days", "mM", 15, "S74")]):
    ch = LineChart()
    ch.title, ch.y_axis.title, ch.x_axis.title = title, ytitle, "hour"
    ch.height, ch.width = 8.5, 22
    ch.add_data(Reference(ws, min_col=c0, max_col=c0 + 2, min_row=3, max_row=3 + n_ex), titles_from_data=True)
    ch.set_categories(x)
    ch.x_axis.tickLblSkip = 24
    for s in ch.series:
        s.smooth = False
        s.graphicalProperties.line.width = 12000
    ws.add_chart(ch, anchor)

# ---------------------------------------------------------------------------
# 9. Glucose_Participants
# ---------------------------------------------------------------------------
from glucose_data import load_participants
ppl = load_participants(30)
ws = wb.create_sheet("Glucose_Participants")
widths(ws, {c: 18 for c in "ABCDEFG"})
ws.append([_c(ws, "Real CGM data: BIG IDEAs Lab Glycemic Variability and Wearable Device Data v1.1.3 (PhysioNet, ODC-By 1.0)", BOLD)])
ws.append(["Source", "https://physionet.org/content/big-ideas-glycemic-wearable/1.1.3/"])
ws.append(["Who", "16 adults aged 35-65, HbA1c 5.2-6.4% (normal to prediabetic), Dexcom G6 every 5 min for ~8-10 days. No wounds - used as each simulated patient's real glucose background."])
ws.append([])
hdr(ws, ["participant_id", "hba1c_pct", "complete_days", "mean_glucose_mgdl", "sd_mgdl", "cv_pct", "wounds_using_this_person"])
wc = first.groupby("participant_id").size()
for pid, pp in ppl.items():
    g_all = np.concatenate(pp["days"])
    ws.append([pid, pp["hba1c"], len(pp["days"]), round(g_all.mean(), 1), round(g_all.std(), 1),
               round(g_all.std() / g_all.mean(), 3), int(wc.get(pid, 0))])

# ---------------------------------------------------------------------------
# 10. How_Training_Works
# ---------------------------------------------------------------------------
ws = wb.create_sheet("How_Training_Works")
widths(ws, {"A": 34, "B": 120})
ws.append([_c(ws, "How the model learns 'infected or not' when every patient is different", TITLE_FONT)])
ws.append([])
for k, v in [
    ("1. Where labels come from", "A model learns from examples that already have the right answer. In THIS dataset the simulator knows exactly when bacteria arrived, so every reading is labeled. In real life the label must come from a clinician: wound swab culture, or a doctor's diagnosis using IWII criteria, recorded with date and time."),
    ("2. Different patients", "Patients differ in baseline pH, skin temperature, wound wetness and glucose. So the model does NOT judge raw numbers. Its strongest features are each sensor's CHANGE from that patient's own day-1 baseline (the *_vs_base features) and recent trends (_d6h, _d24h). A rise of +0.5 pH means the same thing whether someone starts at 6.4 or 7.0."),
    ("3. Proving it works on new people", "Leave-people-out cross-validation: the 16 real glucose participants are split into 4 groups. Train on 12 people's wounds, test on the 4 the model has never seen, rotate 4 times. If scores hold up, the model generalizes across people instead of memorizing them."),
    ("4. Never split one patient", "If readings from one wound were in both train and test, the model could 'recognize' the patient and scores would look falsely high. GroupKFold prevents this."),
    ("5. Combining data sources", "Each source teaches a different piece: literature = how big the infection changes are; BIG IDEAs = real everyday glucose swings (meals, nights) the model must learn to ignore; your lab tests = how YOUR sensors read and drift; future patient data = the real thing."),
    ("6. Collecting real labeled data", "Per patient: wear patch continuously, log every reading with timestamp + patient ID; at each dressing change record clinician assessment (infected yes/no), swab result if taken, shower/dressing events. One CSV row per reading with the same columns as Full_Data."),
    ("7. Training on real data later", "Step 1 pre-train on this synthetic set. Step 2 fine-tune / retrain on real patch data. Step 3 always evaluate with leave-patients-out. Report sensitivity (infections caught), false alarm rate, and how many hours before diagnosis the alarm fired."),
    ("8. Honest limits", "Synthetic scores are optimistic: the model is tested on data from the same simulator it learned from. Glucose effects are small in non-diabetic people, so blood glucose adds little; wound-fluid glucose (bacteria consume it) is more useful but is a simulated channel based on animal data."),
]:
    ws.append([_c(ws, k, BOLD, wrap=True), _c(ws, v, wrap=True)])

# ---------------------------------------------------------------------------
# 11. Model_Results
# ---------------------------------------------------------------------------
cmp_ = pd.read_csv("data/model_comparison.csv")
imp = pd.read_csv("data/feature_importance.csv", index_col=0)["importance"]
ws = wb.create_sheet("Model_Results")
widths(ws, {"A": 40, "B": 16, "C": 16, "D": 16, "E": 16, "F": 16, "G": 18, "H": 18, "I": 18})
ws.append([_c(ws, "Random forest, leave-people-out 4-fold CV (GroupKFold by participant). Source: data/model_results.txt", TITLE_FONT)])
ws.append([])
hdr(ws, ["Sensors used", "warning recall", "infection recall", "infection precision", "macro F1",
         "wounds detected", "median h onset->alarm", "alarm before onset", "false alarm (clean wounds)"])
for r in cmp_.itertuples(index=False):
    ws.append([r.sensors, round(r.warning_recall, 3), round(r.infection_recall, 3), round(r.infection_precision, 3),
               round(r.macro_f1, 3), round(r.detected, 3), round(r.median_h_to_alarm, 1),
               round(r.alarm_before_onset, 3), round(r.false_alarm_clean, 3)])
ws.append([])
ws.append([_c(ws, "patch = pH + temperature + impedance; cgm = blood glucose (real Dexcom); wound = wound-fluid glucose (simulated).", BOLD)])
ws.append([])
hdr(ws, ["Top features (all sensors)", "importance", None, None, None, None, None, None, None])
for k, v in imp.head(12).items():
    ws.append([k, round(float(v), 3)])
ws.append([])
ws.append([_c(ws, "Caveat: scores are optimistic because the model is tested on data from the same simulator it was trained on. Real-world accuracy will be lower.", BOLD)])


# ---------------------------------------------------------------------------
# 12. Full_Data
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Full_Data")
widths(ws, {c: 16 for c in "ABCDEFGHIJ"})
ws.freeze_panes = "A2"
hdr(ws, list(df.columns))
for r in df.itertuples(index=False):
    ws.append([None if (isinstance(v, float) and np.isnan(v)) else int(v) if isinstance(v, (bool, np.bool_)) else v for v in r])

wb.save(OUT)
print("saved", OUT)
