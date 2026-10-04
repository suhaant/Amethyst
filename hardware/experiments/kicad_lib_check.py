#!/usr/bin/env python3
"""Check which candidate PulsePatch parts ship in the stock KiCad libraries.

Scans the symbol libraries bundled with the local KiCad install, looks up each
candidate part, and confirms the footprint it points at exists on disk.
Also dumps every symbol in the Sensor_* libraries so the full menu is searchable.

Usage: python3 kicad_lib_check.py
Outputs: out/kicad_availability.md, out/kicad_sensor_inventory.csv
"""
import csv
import re
import sys
from pathlib import Path

KICAD = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport")
SYM_DIR = KICAD / "symbols"
FP_DIR = KICAD / "footprints"
OUT = Path(__file__).parent / "out"

# category -> list of (label, regex matched against symbol names)
CANDIDATES = {
    "BLE SoC / module": [
        ("nRF52832", r"^nRF52832"), ("nRF52840", r"^nRF52840"),
        ("nRF52805", r"^nRF52805"), ("nRF52810/811", r"^nRF5281[01]"),
        ("nRF52820/833", r"^nRF528(20|33)"), ("nRF5340", r"^nRF5340"),
        ("nRF54L15", r"^nRF54L"), ("Raytac MDBT42Q", r"MDBT42"),
        ("Raytac MDBT50Q", r"MDBT50"), ("Fanstel BC832/BM832", r"^B[CM]832"),
        ("Insight SiP ISP1807", r"ISP1807"), ("u-blox ANNA-B112", r"ANNA-B1"),
        ("u-blox NINA-B1", r"NINA-B1"), ("u-blox BMD-3xx", r"^BMD-3"),
        ("Ebyte E73", r"^E73"), ("Laird BL652/BL654", r"^BL65[24]"),
        ("Renesas DA14531", r"DA1453"), ("Microchip RN4871", r"RN487"),
        ("ESP32-C3 (fallback)", r"^ESP32-C3"), ("STM32WB", r"^STM32WB"),
        ("Seeed XIAO", r"XIAO"),
    ],
    "NFC / batteryless": [
        ("NXP NHS3152", r"NHS3152"), ("NXP NHS3100 (NFC temp logger)", r"NHS3100"), ("TI RF430FRL152H", r"RF430FRL"),
        ("SIC4341", r"SIC434"), ("ST25DV", r"ST25DV"), ("NXP NTAG I2C", r"^NT3H"),
    ],
    "Temperature": [
        ("TI TMP117", r"^TMP117"), ("TI TMP116", r"^TMP116"), ("TI TMP119", r"^TMP119"), ("TI TMP114 (0.15 mm tall)", r"^TMP114"),
        ("ADI MAX30208", r"MAX30208"), ("ADI MAX30205", r"MAX30205"),
        ("ams AS6221", r"AS6221"), ("ams AS6212", r"AS6212"),
        ("ST STTS22H", r"STTS22"), ("Silabs Si7051", r"Si705"),
        ("TI TMP102/112", r"^TMP1[01]2"), ("Microchip MCP9808", r"MCP9808"),
        ("TI LMT70", r"LMT70"), ("Melexis MLX90632 (IR)", r"MLX9063"),
        ("Melexis MLX90614 (IR)", r"MLX90614"),
    ],
    "pH / electrochemical front end": [
        ("TI LMP91200", r"LMP91200"), ("ADI AD5940", r"AD5940"),
        ("ADI AD5941", r"AD5941"), ("TI LMP91000", r"LMP91000"),
        ("TI LMP7721", r"LMP7721"), ("ADI ADA4530", r"ADA4530"),
        ("TI LPV821", r"LPV821"), ("TI LMC6001", r"LMC6001"),
        ("TI OPA333", r"^OPA333"), ("TI LMP7701/2", r"LMP770"),
        ("ADI AD8603", r"AD8603"), ("ADI MAX4003x", r"MAX4002"),
        ("TI LMC6482", r"LMC6482"), ("TI OPA2333", r"^OPA2333"),
        ("TI TLV9062 (generic RRIO)", r"TLV906"),
    ],
    "Moisture / capacitance / impedance": [
        ("TI FDC1004", r"FDC1004"), ("TI FDC2112/2214", r"FDC2[12]1"),
        ("ADI AD7746/7745", r"AD774[56]"), ("ADI AD7150/7151", r"AD715[01]"), ("ADI AD5933/5934", r"AD593[34]"),
        ("ADI MAX30009", r"MAX30009"), ("ADI MAX30001/2/3", r"MAX3000[123]"),
        ("TI AFE4500", r"AFE4500"), ("ADI AD8232", r"AD8232"),
        ("ADI ADuCM355", r"ADuCM35"),
    ],
    "Humidity (dressing headspace)": [
        ("Sensirion SHT40/41/4x", r"^SHT4"), ("Sensirion SHT3x", r"^SHT3"),
        ("Sensirion SHTC3", r"SHTC3"), ("TI HDC2010/2080", r"HDC20"),
        ("TI HDC3020", r"HDC302"), ("ScioSense ENS210", r"ENS210"), ("Bosch BME280", r"^BME280"),
    ],
    "Optical (PPG, spectral, color)": [
        ("MAX30101", r"MAX30101"), ("MAX30102", r"MAX30102"),
        ("MAX30105", r"MAX30105"), ("MAX86141", r"MAX8614"),
        ("MAX86150", r"MAX86150"), ("MAXM86161", r"MAXM8616"),
        ("TI AFE4404", r"AFE44"), ("ams AS7341", r"AS7341"),
        ("ams AS7343", r"AS7343"), ("ams AS726x", r"AS726"),
        ("OSRAM SFH7072/7050", r"SFH70[57]"), ("Vishay VEML6040", r"VEML6040"),
        ("ams TCS3472x", r"TCS3472"), ("Broadcom APDS-9960", r"APDS-99"),
        ("TI OPT3001", r"OPT3001"), ("Vishay VEML7700", r"VEML7700"),
        ("LiteOn LTR-390", r"LTR-?390"),
    ],
    "Gas / VOC": [
        ("Bosch BME688", r"BME688"), ("Bosch BME680", r"BME680"),
        ("ScioSense ENS160", r"ENS160"), ("Sensirion SGP40/41", r"SGP4"),
        ("Sensirion SGP30", r"SGP30"), ("Sensirion SCD40/41 (CO2)", r"SCD4"), ("ams CCS811", r"CCS811"),
    ],
    "Pressure / force": [
        ("Bosch BMP390/388", r"BMP3[89]"), ("ST LPS22HB", r"LPS22"),
        ("Bosch BMP280", r"^BMP280"), ("TE MS5837", r"MS5837"),
    ],
    "Motion": [
        ("ST LIS2DH12", r"LIS2DH12"), ("ST LIS2DH / LIS2DE12", r"LIS2D[HE]"), ("ST LIS3DH", r"^LIS3DH"),
        ("Bosch BMA400", r"BMA400"), ("ST LSM6DSO", r"LSM6DSO"),
        ("TDK ICM-42670", r"ICM-?4267"), ("Bosch BMI270", r"BMI270"),
        ("ADI ADXL362/363", r"ADXL36[23]"), ("Bosch BMI160", r"BMI160"), ("ST LSM6DSL/DS3", r"LSM6DS[L3M]"), ("Kionix KXTJ3", r"KXTJ3"),
    ],
    "Power": [
        ("Nordic nPM1100", r"nPM1100"), ("Nordic nPM1300", r"nPM1300"),
        ("TI BQ25120", r"BQ2512"), ("TI BQ25100", r"BQ25100"),
        ("TI BQ24074", r"BQ2407"), ("Microchip MCP73831", r"MCP73831"),
        ("TI TPS62840", r"TPS62840"), ("TI TPS62740", r"TPS6274"),
        ("TI TPS63001 buck-boost", r"TPS6300"), ("ADI MAX77734", r"MAX77734"),
        ("TI BQ25150", r"BQ2515"), ("TP4056", r"TP4056"),
        ("TI BQ5100x Qi receiver", r"BQ5100"), ("TI TPS61099x boost", r"TPS61099"),
        ("Diodes AP2112 LDO", r"AP2112"), ("Torex XC6206 LDO", r"XC6206"),
        ("TI TPS7A02 LDO", r"TPS7A02"), ("TI TPS2291x load switch", r"TPS2291"),
    ],
    "LED driver": [
        ("TI TPS61165", r"TPS61165"), ("TI TPS61169", r"TPS61169"),
        ("TI LM3410", r"LM3410"), ("Diodes AP3019", r"AP3019"),
        ("Diodes AL8860", r"AL8860"), ("onsemi CAT4104", r"CAT410"),
        ("ADI LT3465", r"LT3465"), ("TI LP5562", r"LP556"),
        ("TI TPS61040/41 boost", r"TPS6104"), ("TI LM3671", r"LM3671"),
        ("TI TLC59108", r"TLC5910"), ("Lumissil IS31FL319x", r"IS31FL319"),
    ],
    "Piezo / ultrasound driver": [
        ("TI DRV8662", r"DRV8662"), ("TI DRV2667", r"DRV2667"),
        ("TI DRV2700", r"DRV2700"), ("TI DRV2605", r"DRV2605"),
        ("Boreas BOS1901/1921", r"BOS19"), ("Microchip MD1213", r"MD1213"),
        ("Microchip HV7355", r"HV73"), ("Microchip TC6320", r"TC6320"),
        ("TI DRV8837/8838 H-bridge", r"DRV883[78]"), ("TI DRV8833", r"DRV8833"),
        ("Microchip TC4427 gate driver", r"TC442[678]"),
        ("Microchip MIC4427", r"MIC442[678]"), ("ADI LT3482 HV boost", r"LT3482"),
        ("TI TPS61391 HV boost", r"TPS6139"), ("ADI MAX14808 pulser", r"MAX1480[89]"),
    ],
}

# Parts with no stock symbol: the package they ship in and a glob for a matching stock footprint.
# If the footprint exists, only the symbol has to be drawn (or pulled from the vendor / SnapMagic / Ultra Librarian).
# None = chip-scale or LGA land pattern that is specific to the part, so a look-alike stock footprint is not trusted.
GENERIC_FP = {
    "ADI AD5941": ("LFCSP-48 7x7 mm", "Package_CSP.pretty/LFCSP-48-1EP_7x7mm_P0.5mm*"),
    "ADI AD5940": ("WLCSP-56 3.6x4.2 mm", None),
    "TI LMP91200": ("TSSOP-16", "Package_SO.pretty/TSSOP-16_4.4x5mm_P0.65mm*"),
    "TI LMP91000": ("WSON-14 4x4 mm", "Package_SON.pretty/WSON-14-1EP_4x4mm_P0.5mm*"),
    "ADI MAX30208": ("thin LGA-10 2x2 mm", None),
    "ams AS6221": ("WLCSP-6 1.5x1.0 mm", None),
    "ST STTS22H": ("UDFN-6 2x2 mm", "Package_DFN_QFN.pretty/*DFN-6*2x2mm*"),
    "Bosch BME688": ("LGA-8 3x3 mm (same as BME680)", "Package_LGA.pretty/Bosch_LGA-8_3x3mm*"),
    "ScioSense ENS160": ("LGA-9 3x3 mm", "Package_LGA.pretty/*LGA-9_3x3mm*"),
    "Sensirion SGP40/41": ("DFN-6 2.44x2.44 mm", "Sensor*.pretty/*SGP4*"),
    "Bosch BMA400": ("LGA-12 2x2 mm", "Package_LGA.pretty/Bosch_LGA-12_2x2mm*"),
    "ST LIS2DH12": ("LGA-12 2x2 mm", "Package_LGA.pretty/LGA-12_2x2mm*"),
    "Nordic nPM1100": ("QFN-24 4x4 mm", "Package_DFN_QFN.pretty/QFN-24-1EP_4x4mm_P0.5mm*"),
    "Nordic nPM1300": ("QFN-32 5x5 mm", "Package_DFN_QFN.pretty/QFN-32-1EP_5x5mm_P0.5mm*"),
    "TI BQ25120": ("DSBGA-25 2.5x2.5 mm", "Package_BGA.pretty/Texas_DSBGA-25*"),
    "TI TPS62840": ("SON-8 1.5x2 mm or HVSSOP-8", "Package_SON.pretty/*SON-8*1.5x2*"),
    "TI DRV2667": ("QFN-20 4x4 mm", "Package_DFN_QFN.pretty/*QFN-20-1EP_4x4mm_P0.5mm*"),
    "TI DRV2700": ("QFN-20 4x4 mm", "Package_DFN_QFN.pretty/*QFN-20-1EP_4x4mm_P0.5mm*"),
    "ADI MAX30009": ("WLCSP-25 2x2 mm", None),
    "MAX30101": ("OLGA-14 3.3x5.6 mm (same as MAX30102)", "OptoDevice.pretty/Maxim_OLGA-14_3.3x5.6mm*"),
    "MAX86141": ("WLCSP-20 2.05x1.85 mm", None),
    "Melexis MLX90632 (IR)": ("SFN-5 3x3 mm", "*.pretty/*MLX90632*"),
    "Fanstel BC832/BM832": ("custom LGA module 7.8x8.8 mm", "RF_Module.pretty/*BC832*"),
    "Insight SiP ISP1807": ("custom LGA module 8x8 mm", "RF_Module.pretty/*ISP1807*"),
    "u-blox ANNA-B112": ("custom LGA module 6.5x6.5 mm", "RF_Module.pretty/*ANNA-B1*"),
    "nRF52805": ("WLCSP-28 2.5x2.5 mm", "Package_CSP.pretty/*WLCSP-28*"),
}

SYM_RE = re.compile(r'^\t\(symbol "([^"]+)"')
PROP_RE = re.compile(r'^\t\t\(property "(Footprint|Description|Datasheet)" "([^"]*)"')
EXT_RE = re.compile(r'^\t\t\(extends "([^"]+)"\)')


def load_symbols():
    """Return {(lib, name): {footprint, description, datasheet, extends}}."""
    symbols = {}
    for path in sorted(SYM_DIR.glob("*.kicad_sym")):
        lib = path.stem
        cur = None
        with path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = SYM_RE.match(line)
                if m:
                    cur = symbols[(lib, m.group(1))] = {
                        "footprint": "", "description": "", "datasheet": "", "extends": ""}
                    continue
                if cur is None:
                    continue
                m = PROP_RE.match(line)
                if m:
                    cur[m.group(1).lower()] = m.group(2)
                    continue
                m = EXT_RE.match(line)
                if m:
                    cur["extends"] = m.group(1)
    for (lib, _name), sym in symbols.items():
        parent = symbols.get((lib, sym["extends"])) if sym["extends"] else None
        if parent:
            for key in ("footprint", "description", "datasheet"):
                sym[key] = sym[key] or parent[key]
    return symbols


def footprint_exists(ref):
    if ":" not in ref:
        return False
    lib, name = ref.split(":", 1)
    return (FP_DIR / f"{lib}.pretty" / f"{name}.kicad_mod").exists()


def main():
    if not SYM_DIR.is_dir():
        sys.exit(f"KiCad symbol directory not found: {SYM_DIR}")
    OUT.mkdir(exist_ok=True)
    symbols = load_symbols()
    n_libs = len({lib for lib, _ in symbols})
    print(f"Indexed {len(symbols)} symbols across {n_libs} libraries")

    lines = ["# KiCad stock-library availability for PulsePatch candidate parts", "",
             f"Scanned {len(symbols)} symbols in {n_libs} libraries from `{SYM_DIR}`.", "",
             "`FP ok` means the footprint the symbol points to exists in the stock footprint libraries.", ""]
    totals = {"found": 0, "missing": 0}
    for cat, parts in CANDIDATES.items():
        lines += [f"## {cat}", "", "| Part | In KiCad? | Library:Symbol | Footprint | FP ok |", "|---|---|---|---|---|"]
        for label, pattern in parts:
            rx = re.compile(pattern, re.IGNORECASE)
            hits = sorted((lib, name) for (lib, name) in symbols if rx.search(name))
            if not hits:
                totals["missing"] += 1
                lines.append(f"| {label} | NO | | | |")
                continue
            totals["found"] += 1
            for i, (lib, name) in enumerate(hits[:4]):
                fp = symbols[(lib, name)]["footprint"]
                ok = "yes" if footprint_exists(fp) else ("none assigned" if not fp else "MISSING")
                lines.append(f"| {label if i == 0 else ''} | {'yes' if i == 0 else ''} | {lib}:{name} | {fp} | {ok} |")
            if len(hits) > 4:
                lines.append(f"| | | (+{len(hits) - 4} more variants) | | |")
        lines.append("")
    lines.insert(4, f"**{totals['found']} of {totals['found'] + totals['missing']} candidates have a stock symbol.**\n")
    (OUT / "kicad_availability.md").write_text("\n".join(lines))

    lines += ["## Parts with no stock symbol: is there at least a stock footprint?", "",
              "Package names here are the expected package; confirm against the datasheet before layout.", "",
              "| Part | Package | Stock footprint | Work needed |", "|---|---|---|---|"]
    for part, (package, pattern) in GENERIC_FP.items():
        hits = sorted(FP_DIR.glob(pattern)) if pattern else []
        if hits:
            fp = f"{hits[0].parent.stem}:{hits[0].stem}" + (f" (+{len(hits) - 1})" if len(hits) > 1 else "")
            lines.append(f"| {part} | {package} | {fp} | draw or import symbol only |")
        else:
            lines.append(f"| {part} | {package} | none | import symbol + footprint from vendor |")
    lines.append("")
    (OUT / "kicad_availability.md").write_text("\n".join(lines))

    with (OUT / "kicad_sensor_inventory.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["library", "symbol", "footprint", "footprint_in_stock_libs", "description"])
        counts = {}
        for (lib, name), sym in sorted(symbols.items()):
            if lib.startswith("Sensor"):
                counts[lib] = counts.get(lib, 0) + 1
                w.writerow([lib, name, sym["footprint"], footprint_exists(sym["footprint"]), sym["description"]])
    print(f"Candidates found: {totals['found']}  missing: {totals['missing']}")
    print("Sensor library sizes:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"Wrote {OUT / 'kicad_availability.md'} and {OUT / 'kicad_sensor_inventory.csv'}")


if __name__ == "__main__":
    main()
