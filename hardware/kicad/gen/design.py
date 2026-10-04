"""PulsePatch board: every part, what it connects to, and where it sits.

This file is the single source of truth. gen_schematic.py and gen_board.py both read it.
Pin keys are a pin name, a pin number, or one half of a slash name ("P0.02" matches "AIN0/P0.02").
Pins not listed are left unconnected on purpose.
"""
import math

BOARD_W, BOARD_H = 30.0, 40.0
PIEZO_CENTRE, PIEZO_D = (15.0, 24.0), 16.0      # 15 mm flexing disc plus clearance, wound-facing side
PIEZO_DISC_D = 15.0                              # the disc itself; drawn on the bottom silkscreen
LED_RING_R = 10.6

R0402 = "Resistor_SMD:R_0402_1005Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
SOT23_5 = "Package_TO_SOT_SMD:SOT-23-5"
WSON6 = "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm"
PAD_2MM = "TestPoint:TestPoint_Pad_2.0x2.0mm"
PAD_1MM5 = "TestPoint:TestPoint_Pad_1.5x1.5mm"
L_3MM = "Inductor_SMD:L_Taiyo-Yuden_NR-30xx"
L_6MM = "Inductor_SMD:L_6.3x6.3_H3"
SOD123 = "Diode_SMD:D_SOD-123"
LED_3535 = "LED_SMD:LED_Cree-XP"

PARTS = []
_count = {}


def add(prefix, symbol, value, footprint, block, pins, at=None):
    """at = (x, y, rotation, side) for a hand-placed part; None lets gen_board flow it into the block's region."""
    _count[prefix] = _count.get(prefix, 0) + 1
    ref = "%s%d" % (prefix, _count[prefix])
    lib, name = symbol.split(":")
    PARTS.append(dict(ref=ref, lib=lib, sym=name, value=value, fp=footprint, block=block, pins=pins, at=at))
    return ref


def res(value, a, b, block, at=None):
    return add("R", "Device:R", value, R0402, block, {"1": a, "2": b}, at)


def cap(value, a, b, block, fp=C0402, at=None):
    return add("C", "Device:C", value, fp, block, {"1": a, "2": b}, at)


def pad(net, block, fp=PAD_2MM, at=None):
    return add("TP", "Connector:TestPoint", net, fp, block, {"1": net}, at)


def tmp117(addr_net, block, at=None, cap_at=None):
    add("U", "Sensor_Temperature:TMP117xxDRV", "TMP117", WSON6, block,
        {"V+": "+3V3", "GND": "GND", "SCL": "SCL", "SDA": "SDA", "ALERT": "TEMP_ALERT_N", "ADD0": addr_net}, at)
    cap("100n", "+3V3", "GND", block, at=cap_at)


# ---- POWER: charge pads -> charger -> cell -> 3.3 V rail, plus battery voltage sense
pad("VCHG", "POWER", PAD_1MM5)
pad("GND", "POWER", PAD_1MM5)
add("U", "Battery_Management:MCP73831-2-OT", "MCP73831", SOT23_5, "POWER",
    {"4": "VCHG", "2": "GND", "3": "VBAT", "5": "CHG_PROG", "1": "CHG_STAT"})
cap("4.7u", "VCHG", "GND", "POWER", C0603)
res("4.7k", "CHG_PROG", "GND", "POWER")                 # about 210 mA charge current
cap("4.7u", "VBAT", "GND", "POWER", C0603)
pad("VBAT", "POWER", PAD_1MM5)
pad("GND", "POWER", PAD_1MM5)
add("U", "Regulator_Linear:AP2112K-3.3", "AP2112K-3.3", SOT23_5, "POWER",
    {"VIN": "VBAT", "GND": "GND", "EN": "VBAT", "VOUT": "+3V3"})
cap("1u", "VBAT", "GND", "POWER")
cap("1u", "+3V3", "GND", "POWER")
res("1M", "VBAT", "BAT_SENSE", "POWER")
res("1M", "BAT_SENSE", "GND", "POWER")
cap("100n", "BAT_SENSE", "GND", "POWER")

# ---- MCU: Raytac nRF52832 module in the top-left corner, antenna end on the board edge
add("U", "RF_Module:MDBT42Q-512K", "MDBT42Q-512K", "RF_Module:Raytac_MDBT42Q", "MCU", {
    "VDD": "+3V3", "GND": "GND", "P0.26": "SDA", "P0.27": "SCL",
    "P0.02": "PH_OUT", "P0.03": "BAT_SENSE", "P0.04": "PAD_ID", "P0.05": "PH_REF",
    "P0.11": "LED_PWM", "P0.12": "US_IN1", "P0.13": "US_IN2", "P0.14": "US_EN",
    "P0.15": "TEMP_ALERT_N", "P0.16": "BUTTON", "P0.17": "STATUS_LED", "P0.18": "CHG_STAT",
    "P0.19": "MOIST_DRV", "P0.20": "US_LEVEL", "P0.28": "MOIST_SENSE", "P0.29": "PAD_AUX",
    "SWDIO": "SWDIO", "SWDCLK": "SWDCLK", "P0.21": "RESET_N"}, at=(6.3, None, 0, "F"))
cap("10u", "+3V3", "GND", "MCU", C0603)
cap("100n", "+3V3", "GND", "MCU")
res("4.7k", "+3V3", "SDA", "MCU")
res("4.7k", "+3V3", "SCL", "MCU")

# ---- TEMPERATURE: wound edge and periwound reference face the skin, ambient sits on top away from heat
tmp117("GND", "TEMPERATURE", at=(25.0, 24.0, 0, "B"), cap_at=(27.4, 24.0, 90, "B"))       # 0x48 wound edge
tmp117("+3V3", "TEMPERATURE", at=(27.4, 33.9, 0, "B"), cap_at=(27.4, 36.0, 0, "B"))       # 0x49 periwound reference
tmp117("SDA", "UI")                                                                          # 0x4A ambient
res("10k", "+3V3", "TEMP_ALERT_N", "SAFETY")

# ---- MOISTURE: impedance between two pad electrodes at 1 kHz, the quantity the infection model was trained on.
# The microcontroller drives a 1 kHz square wave through a 47k reference resistor; the electrode pair is the
# bottom of that divider (other electrode on ground) and the midpoint is read on AIN4.
res("47k 1%", "MOIST_DRV", "MOIST_SENSE", "MOISTURE")
cap("1u", "MOIST_SENSE", "MOIST_1", "MOISTURE")         # blocks DC so no steady current flows through the wound

# ---- PH: unity-gain buffer on the working electrode, reference electrode held at mid-supply
add("U", "Amplifier_Operational:AD8603", "AD8603", "Package_TO_SOT_SMD:TSOT-23-5", "PH",
    {"5": "+3V3", "2": "GND", "3": "PH_IN", "4": "PH_BUF", "1": "PH_BUF"})
cap("100n", "+3V3", "GND", "PH")
res("10k", "PH_WE", "PH_IN", "PH")
cap("100p", "PH_IN", "GND", "PH")
res("100k", "+3V3", "PH_REF", "PH")
res("100k", "PH_REF", "GND", "PH")
cap("1u", "PH_REF", "GND", "PH")
res("10k", "PH_BUF", "PH_OUT", "PH")
cap("100n", "PH_OUT", "GND", "PH")

# ---- SAFETY: any TMP117 alert pulls TEMP_ALERT_N low and forces both therapy enables off in hardware
add("U", "74xGxx:74LVC1G08", "74LVC1G08", SOT23_5, "SAFETY",
    {"1": "LED_PWM", "2": "TEMP_ALERT_N", "4": "LED_CTRL", "5": "+3V3", "3": "GND"})
cap("100n", "+3V3", "GND", "SAFETY")
res("100k", "LED_PWM", "GND", "SAFETY")                 # therapy stays off while the MCU is in reset
add("U", "74xGxx:74LVC1G08", "74LVC1G08", SOT23_5, "SAFETY",
    {"1": "US_EN", "2": "TEMP_ALERT_N", "4": "US_EN_SAFE", "5": "+3V3", "3": "GND"})
cap("100n", "+3V3", "GND", "SAFETY")
res("100k", "US_EN", "GND", "SAFETY")

# ---- LIGHT: boost constant-current driver feeding six 405 nm LEDs in series (20 mA max, PWM dimmed)
add("U", "Driver_LED:TPS61165DRV", "TPS61165", WSON6, "LIGHT",
    {"VIN": "VBAT", "GND": "GND", "SW": "LED_SW", "FB": "LED_FB", "COMP": "LED_COMP", "CTRL": "LED_CTRL"})
cap("4.7u", "VBAT", "GND", "LIGHT", C0603)
add("L", "Device:L", "10u", L_3MM, "LIGHT", {"1": "VBAT", "2": "LED_SW"})
add("D", "Device:D_Schottky", "MBR0540", SOD123, "LIGHT", {"A": "LED_SW", "K": "LED_ANODE"})
cap("1u 50V", "LED_ANODE", "GND", "LIGHT", C0805)
cap("220n", "LED_COMP", "GND", "LIGHT")
res("10R", "LED_FB", "GND", "LIGHT")
_string = ["LED_ANODE", "LED_S1", "LED_S2", "LED_S3", "LED_S4", "LED_S5", "LED_FB"]
for _k, _deg in enumerate((270, 330, 30, 90, 150, 210)):
    _x = PIEZO_CENTRE[0] + LED_RING_R * math.cos(math.radians(_deg))
    _y = PIEZO_CENTRE[1] + LED_RING_R * math.sin(math.radians(_deg))
    add("D", "Device:LED", "405nm", LED_3535, "LIGHT", {"A": _string[_k], "K": _string[_k + 1]},
        at=(round(_x, 2), round(_y, 2), 0, "B"))

# ---- ULTRASOUND: adjustable 5..10 V boost, H-bridge, series inductor resonating with the piezo disc
add("U", "Regulator_Switching:TPS61040DBV", "TPS61040", SOT23_5, "ULTRASOUND",
    {"VIN": "VBAT", "GND": "GND", "EN": "US_EN_SAFE", "SW": "US_SW", "FB": "US_FB"})
cap("4.7u", "VBAT", "GND", "ULTRASOUND", C0603)
add("L", "Device:L", "10u", L_3MM, "ULTRASOUND", {"1": "VBAT", "2": "US_SW"})
add("D", "Device:D_Schottky", "MBR0540", SOD123, "ULTRASOUND", {"A": "US_SW", "K": "+10V"})
cap("4.7u 25V", "+10V", "GND", "ULTRASOUND", C0805)
res("1M", "+10V", "US_FB", "ULTRASOUND")
res("180k", "US_FB", "GND", "ULTRASOUND")
cap("22p", "+10V", "US_FB", "ULTRASOUND")
# Strength control: a filtered PWM voltage (0..3.3 V) pulls the boost output from about 10 V down to about 5 V.
res("100k", "US_LEVEL", "US_CTL", "ULTRASOUND")
cap("1u", "US_CTL", "GND", "ULTRASOUND")
res("560k", "US_CTL", "US_FB", "ULTRASOUND")
add("U", "Driver_Motor:DRV8837", "DRV8837", "Package_SON:WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm", "ULTRASOUND",
    {"VM": "+10V", "VCC": "+3V3", "GND": "GND", "IN1": "US_IN1", "IN2": "US_IN2", "7": "US_EN_SAFE",
     "OUT1": "US_OUT1", "OUT2": "US_OUT2"}, at=(24.0, 36.2, 0, "F"))
cap("100n 25V", "+10V", "GND", "ULTRASOUND", at=(27.6, 35.6, 0, "F"))
cap("100n", "+3V3", "GND", "ULTRASOUND", at=(27.6, 36.8, 0, "F"))
add("L", "Device:L", "4.7m", L_6MM, "ULTRASOUND", {"1": "US_OUT1", "2": "PIEZO_A"}, at=(25.5, 31.1, 0, "F"))
pad("PIEZO_A", "ULTRASOUND", PAD_1MM5, at=(28.3, 26.6, 0, "B"))
pad("US_OUT2", "ULTRASOUND", PAD_1MM5, at=(28.3, 29.3, 0, "B"))

# ---- UI and debug
add("SW", "Switch:SW_Push", "PTS810", "Button_Switch_SMD:SW_SPST_PTS810", "UI", {"1": "BUTTON", "2": "GND"})
add("D", "Device:LED", "status", "LED_SMD:LED_0603_1608Metric", "UI", {"A": "STATUS_LED_A", "K": "GND"})
res("1k", "STATUS_LED", "STATUS_LED_A", "UI")
# Debug pads sit on the bottom so a pogo jig can reach them when the disposable pad is off.
for _k, _net in enumerate(("SWDIO", "SWDCLK", "RESET_N", "+3V3", "GND")):
    pad(_net, "UI", PAD_1MM5, at=(16.0 + 3.0 * _k, 8.5, 0, "B"))

# ---- PAD: eight spring-contact targets for the disposable pad, in a row along the bottom edge
res("100k", "+3V3", "PAD_ID", "PAD")
# The second moisture electrode is the ground contact next to PAD_AUX; PAD_AUX is a spare analog line.
for _k, _net in enumerate(("PH_WE", "PH_REF", "MOIST_1", "PAD_AUX", "GND", "PAD_ID", "+3V3", "GND")):
    pad(_net, "PAD", at=(3.4 + 3.3 * _k, 38.3, 0, "B"))

# Nets that need a PWR_FLAG so the electrical rules check knows they are powered from outside the schematic.
POWER_FLAGS = ["VCHG", "GND", "+10V"]

# Nets that carry converter or battery current: routed 0.4 mm wide instead of 0.2 mm.
# The H-bridge outputs stay at 0.2 mm: they leave neighbouring 0.5 mm-pitch pins, where two 0.4 mm tracks cannot fit.
POWER_NETS = ["VBAT", "VCHG", "+10V", "LED_SW", "US_SW", "LED_ANODE", "PIEZO_A"]

# Top-side regions (x0, y0, x1, y1) that gen_board flows un-placed parts into, by block.
REGIONS = {"SIDE": (13.4, 0.7, 29.3, 17.15), "CORE": (0.7, 17.5, 29.3, 27.2), "DRIVE": (0.7, 27.6, 21.4, 39.3)}
BLOCK_REGION = {"POWER": "SIDE", "UI": "SIDE", "MCU": "CORE", "TEMPERATURE": "CORE", "MOISTURE": "CORE", "PH": "CORE",
                "SAFETY": "CORE", "PAD": "CORE", "LIGHT": "DRIVE", "ULTRASOUND": "DRIVE"}

# Schematic sheet (A2): top-left corner of each block.
SCH_CELLS = {"POWER": (12, 25), "MCU": (157, 25), "TEMPERATURE": (302, 25), "MOISTURE": (447, 25),
             "PH": (12, 165), "SAFETY": (302, 165), "UI": (447, 150),
             "LIGHT": (12, 285), "ULTRASOUND": (157, 285), "PAD": (447, 290)}
