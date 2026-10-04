# PulsePatch pod board: spec v0.1

Approved by Anay on 2026-10-03. The design lives in `hardware/kicad/gen/design.py`; this page explains it.

## What the board does

A reusable electronics pod that sits on a disposable hydrogel pad. It senses temperature, moisture (as impedance) and pH, and can drive 405 nm light and low-frequency ultrasound. No motion sensor.

## Board

- 30 x 40 mm, 4 copper layers, 0.8 mm thick. Outer layers carry signals; inner layer 1 is a ground plane, inner layer 2 carries signals. Ground is also poured on the other three layers and tied together with stitching vias.
- Top side: radio module, power, sensor front ends, therapy drivers. The battery stacks above this side.
- Bottom side (faces the wound): LED ring, piezo disc, two temperature sensors, eight pad contacts.
- Radio module sits in the top-left corner with its antenna on the board edge. No copper on any layer under the antenna.

## Blocks

| Block | Parts | How it works |
|---|---|---|
| Radio and microcontroller | Raytac MDBT42Q-512K (nRF52832) | Runs in LDO mode, internal RC low-frequency clock. I2C on P0.26 (SDA) and P0.27 (SCL). |
| Temperature | 3 x TMP117 | Wound edge (I2C 0x48) and periwound reference (0x49) on the bottom; ambient (0x4A) on top. All three ALERT pins are wired together. |
| Moisture | 47k reference resistor, 1 µF blocking capacitor | The microcontroller drives a 1 kHz square wave (P0.19) through the resistor into two pad electrodes and reads the midpoint on AIN4. This gives impedance in kΩ, the quantity the infection model was trained on. No dedicated chip. |
| pH | AD8603 buffer | Unity-gain buffer on the working electrode. Reference electrode is held at half supply by a divider. The microcontroller reads buffer output and reference as a differential pair (AIN0, AIN3). |
| Power | MCP73831 charger, AP2112K-3.3 regulator | Single LiPo cell on two pads. About 210 mA charge current. Battery voltage is read through a 1M/1M divider on AIN1. |
| Light | TPS61165 boost driver, 6 x 405 nm 3.5 mm LEDs in series | Constant current, 20 mA maximum, dimmed by PWM on P0.11. |
| Ultrasound | TPS61040 boost adjustable from about 5 to 10 V, DRV8837 H-bridge, 4.7 mH series inductor, piezo pads | The inductor resonates with a 15 mm, 30 kHz, 6.2 nF flexing disc. Bridge inputs on P0.12 and P0.13, enable on P0.14. A filtered PWM on P0.20 sets the boost voltage, which sets the strength. |
| Safety cutoff | 2 x 74LVC1G08 AND gates | Light enable and ultrasound enable each pass through an AND gate with the temperature alert line. Any TMP117 alert turns therapy off without firmware. Pull-downs keep therapy off while the microcontroller is in reset. |
| Pad connector | 8 contact pads, bottom edge | pH working, pH reference, moisture electrode, spare analog line, moisture return (ground), pad ID, +3V3, ground. Pad ID has a 100k pull-up so a resistor in the pad identifies it. |
| User interface and debug | Button (P0.16), status LED (P0.17), 5 debug pads | The button is the daily pain and odour prompt. Debug pads carry SWDIO, SWDCLK, reset, +3V3, ground. |

## How it is built

`hardware/kicad/build.sh` regenerates everything from `design.py`:

1. `gen_schematic.py` writes the schematic, exports KiCad's netlist and fails if any pin is on the wrong net.
2. `gen_board.py` places footprints from that netlist, so board and schematic cannot disagree.
3. `route.py` autoroutes with Freerouting and fills the planes.
4. KiCad's electrical rules check, design rules check and renders run last.

Edit `design.py`, not the generated files. Hand edits in the KiCad editor are overwritten by the next build.

## Not verified yet

- **Part values and pinouts** come from KiCad's stock symbols and from memory of the datasheets. Check each block against its datasheet before ordering: the charge resistor, boost feedback dividers, LED current resistor, and the module's LDO-mode pin handling in particular.
- **LED footprint** is the generic 3.45 mm Cree XP pattern. Confirm pad order against the chosen 405 nm LED.
- **TMP117 alert limits** must be written to the sensors' EEPROM once so the cutoff works from power-on.
- **Ultrasound drive** is the least proven block. Resonant frequency shifts when the disc is loaded by gel, so the inductor value will need tuning on the bench.
- **Thermal isolation** of the two skin-facing temperature sensors from the LEDs and converters is not designed yet. They share one rigid board in this version.
- **Routing** is autorouted. The switching converter loops, the piezo drive and anything near the antenna need a manual check.
- **Remaining design-rule findings** after the last build: 4 silkscreen overlaps, and 1 notice that the radio module footprint differs from the library copy (its inner keep-out was relaxed so it stops flagging the module's own pads). All 178 connections are routed.
