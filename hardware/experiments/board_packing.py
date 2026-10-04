#!/usr/bin/env python3
"""Board-space experiment for the PulsePatch pod.

Question: for a patch-sized two-sided board, which sensor sets physically fit,
and how many spare small sensor chips are left over?

Method: every functional block is an IC plus its support passives, each drawn
as a courtyard rectangle. Blocks are placed on a 0.25 mm occupancy grid for the
top side (electronics) and bottom side (wound-facing therapy and optics), with
keep-outs for the board edge, the antenna, and the piezo disc. A routing gap is
added around every part: wider for 2-layer boards, narrower for 4-layer.

Packing success is a geometric check, not proof of routability. The utilisation
column (courtyard area / usable area) is the number to compare against the usual
rule of thumb: about 35% is comfortable on 2 layers, about 50% on 4 layers.

Usage: python3 board_packing.py
Outputs: out/packing_results.md, out/layout_*.svg
"""
import math
from pathlib import Path

OUT = Path(__file__).parent / "out"
GRID = 0.25          # mm per cell
EDGE = 0.5           # mm copper/part pull-back from board edge
COURTYARD = 0.25     # mm added to each side of an IC body
ROUTE_GAP = {"2-layer": 0.8, "4-layer": 0.4}   # mm between neighbouring courtyards
COMFORT = {"2-layer": 0.35, "4-layer": 0.50}   # utilisation rule of thumb
LIMIT = {"2-layer": 0.50, "4-layer": 0.65}

# Passive / small-part courtyards (mm), already including courtyard margin.
SMALL = {
    "0402": (1.9, 1.0), "0603": (3.0, 1.5), "0805": (3.4, 1.9),
    "L2016": (2.6, 2.2), "L3030": (3.6, 3.6), "L6060": (6.6, 6.6),
    "X2016": (2.6, 2.2), "X32K": (2.6, 1.8), "SOD323": (3.2, 1.8),
    "TP": (1.5, 1.5), "CONTACT": (2.5, 2.5),
}

# name -> (side, label, IC body (L, W) in mm or None, [(small part, count)], placement preference)
# Body sizes are package dimensions from datasheets; see research/02-parts-and-kicad.md.
BLOCKS = {
    # --- always present
    "ble_module":   ("top", "nRF52832 module MDBT42Q 16x10", (16.0, 10.0), [("0402", 2), ("X32K", 1), ("0402", 2)], "edge"),
    "ble_small":    ("top", "nRF52832 module BC832 7.8x8.8", (8.8, 7.8), [("0402", 2), ("X32K", 1), ("0402", 2)], "edge"),
    "pmic":         ("top", "nPM1100 charger+buck QFN 4x4", (4.0, 4.0), [("L2016", 1), ("0402", 5), ("0603", 2)], "corner"),
    "swd_charge":   ("top", "SWD pads + charge pads", None, [("TP", 4), ("CONTACT", 2)], "corner"),
    "pad_contacts": ("bottom", "8 spring contacts to disposable pad", None, [("CONTACT", 8)], "corner"),
    # --- sensing
    "temp_wound":   ("bottom", "TMP117 wound-edge temp 2x2", (2.0, 2.0), [("0402", 1)], "center"),
    "temp_ref":     ("bottom", "TMP117 periwound reference 2x2", (2.0, 2.0), [("0402", 1)], "corner"),
    "temp_ambient": ("top", "TMP117 ambient temp 2x2", (2.0, 2.0), [("0402", 1)], "corner"),
    "ph_buffer":    ("top", "pH buffer op-amp SOT-23-5", (2.9, 2.8), [("0402", 5)], "corner"),
    "moisture_cdc": ("top", "FDC1004 cap-to-digital 3x4.9", (3.0, 4.9), [("0402", 2)], "corner"),
    "imu":          ("top", "accelerometer LGA 2x2", (2.0, 2.0), [("0402", 2)], "corner"),
    "ui":           ("top", "pain/odour button + status LED", (3.0, 2.6), [("0603", 1), ("0402", 3)], "corner"),
    "afe_ad5941":   ("top", "AD5941 impedance + pH AFE 7x7", (7.0, 7.0), [("0402", 14), ("0603", 2), ("X2016", 1)], "corner"),
    "spectral":     ("bottom", "AS7341 spectral sensor 3.1x2", (3.1, 2.0), [("0402", 3)], "center"),
    "ppg":          ("bottom", "MAX30102 heart rate 5.6x3.3", (5.6, 3.3), [("0402", 4), ("0603", 1)], "corner"),
    # --- therapy (see research/raw/C-therapy-hardware.md)
    "led_array":    ("bottom", "6x 405 nm LED 3.5x3.5", None, [], "center"),   # LEDs added in code
    "led_driver":   ("top", "LED boost driver 2x2 + L", (2.0, 2.0), [("L3030", 1), ("SOD323", 1), ("0603", 2), ("0402", 3)], "corner"),
    "us_boost":     ("top", "12 V boost for ultrasound SOT-23", (2.9, 2.8), [("L3030", 1), ("SOD323", 1), ("0603", 3), ("0402", 3)], "corner"),
    "us_bridge":    ("top", "H-bridge 2x2 + resonant inductor", (2.0, 2.0), [("L6060", 1), ("0402", 2)], "corner"),
}
LED_SIZE = (4.0, 4.0)      # 3.5 x 3.5 mm LED with courtyard
N_LEDS = 6
PIEZO_D = 16.0             # mm, 15 mm flexural unimorph plus clearance, centre of wound-facing side
ANTENNA_KEEPOUT = {"ble_module": (10.5, 5.0), "ble_small": (8.3, 4.0)}   # mm, copper-free zone mirrored onto the other side under the antenna
SPARE = ("spare 2x2 I2C sensor", (2.0, 2.0), [("0402", 2)])

BASE = ["pmic", "swd_charge", "pad_contacts"]
SENSING = {
    "A pitch baseline (pH, moisture, wound + reference temp)":
        ["temp_wound", "temp_ref", "ph_buffer", "moisture_cdc"],
    "B recommended (A + ambient temp + accelerometer + button/LED)":
        ["temp_wound", "temp_ref", "temp_ambient", "ph_buffer", "moisture_cdc", "imu", "ui"],
    "C stretch (B with one AFE for pH/impedance + heart rate + spectral)":
        ["temp_wound", "temp_ref", "temp_ambient", "afe_ad5941", "imu", "ui", "ppg", "spectral"],
}
THERAPY = ["led_array", "led_driver", "us_boost", "us_bridge"]
BOARDS = {
    "25x25 mm": ("rect", 25.0, 25.0),
    "D32 mm (AirTag size)": ("circle", 32.0, 32.0),
    "D35 mm (Libre 2 size)": ("circle", 35.0, 35.0),
    "30x40 mm": ("rect", 30.0, 40.0),
    "40x40 mm": ("rect", 40.0, 40.0),
}


class Side:
    """Occupancy grid for one side of the board."""

    def __init__(self, board):
        self.shape, self.w, self.h = board
        self.nx, self.ny = int(round(self.w / GRID)), int(round(self.h / GRID))
        self.occ = [bytearray(self.nx) for _ in range(self.ny)]
        self.placed = []      # (x, y, w, h, block, label, is_ic)
        self.keepouts = []    # (kind, ...) for drawing
        self.usable = 0
        cx, cy, r = self.w / 2, self.h / 2, self.w / 2 - EDGE
        for j in range(self.ny):
            for i in range(self.nx):
                x, y = (i + 0.5) * GRID, (j + 0.5) * GRID
                if self.shape == "circle":
                    inside = (x - cx) ** 2 + (y - cy) ** 2 <= r * r
                else:
                    inside = EDGE <= x <= self.w - EDGE and EDGE <= y <= self.h - EDGE
                if inside:
                    self.usable += 1
                else:
                    self.occ[j][i] = 1
        self.usable_mm2 = self.usable * GRID * GRID
        self.sat = None

    def block_circle(self, d):
        cx, cy, r = self.w / 2, self.h / 2, d / 2
        n = 0
        for j in range(self.ny):
            for i in range(self.nx):
                if not self.occ[j][i] and ((i + 0.5) * GRID - cx) ** 2 + ((j + 0.5) * GRID - cy) ** 2 <= r * r:
                    self.occ[j][i] = 1
                    n += 1
        self.keepouts.append(("circle", cx, cy, r))
        return n * GRID * GRID

    def block_rect(self, x, y, w, h):
        for j in range(max(0, int(y / GRID)), min(self.ny, int(math.ceil((y + h) / GRID)))):
            for i in range(max(0, int(x / GRID)), min(self.nx, int(math.ceil((x + w) / GRID)))):
                self.occ[j][i] = 1
        self.keepouts.append(("rect", x, y, w, h))

    def build_sat(self):
        sat = [[0] * (self.nx + 1) for _ in range(self.ny + 1)]
        for j in range(self.ny):
            row, above, cur, run = self.occ[j], sat[j], sat[j + 1], 0
            for i in range(self.nx):
                run += row[i]
                cur[i + 1] = above[i + 1] + run
        self.sat = sat

    def free(self, i, j, cw, ch):
        if i < 0 or j < 0 or i + cw > self.nx or j + ch > self.ny:
            return False
        s = self.sat
        return s[j + ch][i + cw] - s[j][i + cw] - s[j + ch][i] + s[j][i] == 0

    def place(self, size, gap, prefer, anchor, block, label, is_ic, near=None, orient=None):
        """Place one rectangle. Returns its centre, or None if it does not fit."""
        self.build_sat()
        best = None
        options = {size, size[::-1]}
        if orient == "tall":
            options = {(min(size), max(size))}
        for w, h in options:
            cw, ch = int(math.ceil((w + gap) / GRID)), int(math.ceil((h + gap) / GRID))
            if anchor is not None:
                ai, aj = int(anchor[0] / GRID), int(anchor[1] / GRID)
                reach = int(14 / GRID)
                irange = range(max(0, ai - reach), min(self.nx, ai + reach))
                jrange = range(max(0, aj - reach), min(self.ny, aj + reach))
            else:
                irange, jrange = range(self.nx), range(self.ny)
            for j in jrange:
                for i in irange:
                    if not self.free(i, j, cw, ch):
                        continue
                    cx, cy = (i + cw / 2) * GRID, (j + ch / 2) * GRID
                    target = anchor or near
                    if target is not None:
                        score = (cx - target[0]) ** 2 + (cy - target[1]) ** 2
                    elif prefer == "center":
                        score = (cx - self.w / 2) ** 2 + (cy - self.h / 2) ** 2
                    elif prefer == "edge":
                        score = j * 1000 + abs(cx - self.w / 2)
                    else:
                        score = j * 1000 + i
                    if best is None or score < best[0]:
                        best = (score, i, j, cw, ch, w, h)
        if best is None:
            return self.place(size, gap, prefer, None, block, label, is_ic, near=anchor) if anchor is not None else None
        _, i, j, cw, ch, w, h = best
        for jj in range(j, j + ch):
            self.occ[jj][i:i + cw] = b"\x01" * cw
        x, y = i * GRID + gap / 2, j * GRID + gap / 2
        self.placed.append((x, y, w, h, block, label, is_ic))
        return (x + w / 2, y + h / 2)


def block_rects(name):
    side, label, body, extras, prefer = BLOCKS[name]
    rects = []
    if body:
        rects.append(((body[0] + 2 * COURTYARD, body[1] + 2 * COURTYARD), label, True))
    if name == "led_array":
        rects += [(LED_SIZE, "LED", False)] * N_LEDS
    for kind, count in extras:
        rects += [(SMALL[kind], kind, False)] * count
    return side, prefer, rects


def run(board_name, sensing, therapy, stackup, ble="ble_module"):
    board = BOARDS[board_name]
    gap = ROUTE_GAP[stackup]
    sides = {"top": Side(board), "bottom": Side(board)}
    area = {"top": 0.0, "bottom": 0.0}
    names = BASE + SENSING[sensing] + (THERAPY if therapy else [])
    if therapy:
        sides["bottom"].usable_mm2 -= sides["bottom"].block_circle(PIEZO_D)
    order = [ble] + sorted(names, key=lambda n: -sum(r[0][0] * r[0][1] for r in block_rects(n)[2]))
    failed = []
    for name in order:
        side_name, prefer, rects = block_rects(name)
        side, anchor = sides[side_name], None
        for k, (size, label, is_ic) in enumerate(rects):
            use_anchor = anchor if (k > 0 and name != "led_array") else None
            pos = side.place(size, gap, prefer, use_anchor, name, label, is_ic, orient="tall" if name == ble else None)
            if pos is None:
                failed.append(name)
                break
            area[side_name] += size[0] * size[1]
            if k == 0:
                anchor = pos
                if name == ble:
                    x, y = side.placed[-1][:2]
                    kw, kh = ANTENNA_KEEPOUT[ble]
                    sides["bottom"].block_rect(x, y, kw, kh)
                    sides["bottom"].usable_mm2 -= kw * kh
    base_util = {s: area[s] / sides[s].usable_mm2 for s in sides}
    spares = {"comfortable": 0, "max": 0}
    if not failed:
        label, body, extras = SPARE
        size = (body[0] + 2 * COURTYARD, body[1] + 2 * COURTYARD)
        slot = size[0] * size[1] + sum(SMALL[k][0] * SMALL[k][1] * c for k, c in extras)
        side, n = sides["top"], 0
        while (area["top"] + slot) / side.usable_mm2 <= LIMIT[stackup]:
            pos = side.place(size, gap, "corner", None, "spare", label, True)
            if pos is None or not all(side.place(SMALL[k], gap, "corner", pos, "spare", k, False) for k, c in extras for _ in range(c)):
                break
            area["top"] += slot
            n += 1
            if area["top"] / side.usable_mm2 <= COMFORT[stackup]:
                spares["comfortable"] = n
        spares["max"] = n
    return dict(board=board_name, sensing=sensing, therapy=therapy, stackup=stackup, ble=ble, sides=sides,
                failed=failed, util=base_util, spares=spares)


def verdict(r):
    if r["failed"]:
        return "does not fit (" + ", ".join(sorted(set(r["failed"]))) + ")"
    worst = max(r["util"].values())
    if worst <= COMFORT[r["stackup"]]:
        return "fits, comfortable"
    if worst <= LIMIT[r["stackup"]]:
        return "fits, tight"
    return "packs but too dense to route"


PALETTE = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377", "#BBBBBB", "#EE7733",
           "#009988", "#882255", "#999933", "#332288", "#DDCC77", "#117733", "#CC6677", "#44AA99"]


def svg(r, path):
    s = 9.0  # px per mm
    board = BOARDS[r["board"]]
    w, h = board[1], board[2]
    pad, title_h = 12, 46
    blocks = []
    for side in r["sides"].values():
        for item in side.placed:
            if item[6] and (item[4], item[5]) not in blocks:
                blocks.append((item[4], item[5]))
    blocks += [(b, BLOCKS[b][1]) for b in ("led_array", "pad_contacts", "swd_charge") if any(i[4] == b for sd in r["sides"].values() for i in sd.placed)]
    legend_h = 16 * ((len(blocks) + 1) // 2) + 10
    width, height = max(int(2 * w * s + 3 * pad), 640), int(h * s + title_h + 3 * pad + legend_h)
    colors, out = {}, []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" font-family="Helvetica, Arial, sans-serif">')
    out.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')
    out.append(f'<text x="{pad}" y="18" font-size="13" fill="#111">{r["board"]} | {r["stackup"]} | {"with therapy" if r["therapy"] else "sensing only"} | {verdict(r)}</text>')
    out.append(f'<text x="{pad}" y="34" font-size="11" fill="#444">sensor set {r["sensing"].split(" ")[0]} | radio {"MDBT42Q" if r["ble"] == "ble_module" else "BC832"} | both sides drawn as seen from the top | spare 2x2 sensor slots: {r["spares"]["comfortable"]} comfortable, {r["spares"]["max"]} max</text>')
    for k, name in enumerate(("top", "bottom")):
        side = r["sides"][name]
        ox, oy = pad + k * (w * s + pad), title_h + pad
        if board[0] == "circle":
            out.append(f'<circle cx="{ox + w * s / 2}" cy="{oy + h * s / 2}" r="{w * s / 2}" fill="#f3f1ea" stroke="#333"/>')
        else:
            out.append(f'<rect x="{ox}" y="{oy}" width="{w * s}" height="{h * s}" rx="6" fill="#f3f1ea" stroke="#333"/>')
        for ko in side.keepouts:
            if ko[0] == "circle":
                out.append(f'<circle cx="{ox + ko[1] * s}" cy="{oy + ko[2] * s}" r="{ko[3] * s}" fill="#d9d2c0" stroke="#8a7f66" stroke-dasharray="4 3"/>')
                out.append(f'<text x="{ox + ko[1] * s}" y="{oy + ko[2] * s + 4}" font-size="10" text-anchor="middle" fill="#5c5340">piezo disc</text>')
            else:
                out.append(f'<rect x="{ox + ko[1] * s}" y="{oy + ko[2] * s}" width="{ko[3] * s}" height="{ko[4] * s}" fill="none" stroke="#8a7f66" stroke-dasharray="4 3"/>')
                out.append(f'<text x="{ox + (ko[1] + ko[3] / 2) * s}" y="{oy + (ko[2] + ko[4] / 2) * s + 3}" font-size="8" text-anchor="middle" fill="#5c5340">antenna keep-out</text>')
        for x, y, rw, rh, block, label, is_ic in side.placed:
            c = colors.setdefault(block, PALETTE[len(colors) % len(PALETTE)])
            out.append(f'<rect x="{ox + x * s:.1f}" y="{oy + y * s:.1f}" width="{rw * s:.1f}" height="{rh * s:.1f}" fill="{c}" fill-opacity="{0.9 if is_ic else 0.45}" stroke="#222" stroke-width="0.5"><title>{label}</title></rect>')
        out.append(f'<text x="{ox + w * s / 2}" y="{oy - 3}" font-size="11" text-anchor="middle" fill="#111">{name} side: {r["util"][name] * 100:.0f}% used</text>')
    ly = title_h + pad + h * s + pad + 8
    for n, (block, label) in enumerate(blocks):
        lx = pad + (n % 2) * (width // 2)
        yy = ly + 16 * (n // 2)
        c = colors.get(block, "#888")
        out.append(f'<rect x="{lx}" y="{yy - 9}" width="10" height="10" fill="{c}" stroke="#222" stroke-width="0.5"/>')
        out.append(f'<text x="{lx + 15}" y="{yy}" font-size="10" fill="#222">{label}</text>')
    out.append("</svg>")
    path.write_text("\n".join(out))


HIGHLIGHT = set()   # (sensing letter, board prefix, stackup, therapy, ble) combos to draw; empty = draw every config that fits


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "layouts").mkdir(exist_ok=True)
    rows = ["# Board packing results", "",
            f"Grid {GRID} mm, edge pull-back {EDGE} mm, routing gap {ROUTE_GAP}, piezo keep-out D{PIEZO_D:.0f} mm, {N_LEDS} LEDs.",
            "Utilisation = courtyard area / usable area per side, before spares.",
            "Spare slots = extra 2x2 mm I2C sensors (each with 2 caps) that still fit on the top side: first number keeps the board comfortable, second is the hard maximum.", ""]
    for therapy in (False, True):
        for ble in ("ble_module", "ble_small"):
            rows += [f"## {'With therapy (LEDs + piezo + drivers)' if therapy else 'Sensing only'}, radio = {BLOCKS[ble][1]}", "",
                     "| Sensor set | Board | Stackup | Top used | Bottom used | Verdict | Spare slots |", "|---|---|---|---|---|---|---|"]
            for sensing in SENSING:
                for board_name in BOARDS:
                    for stackup in ROUTE_GAP:
                        r = run(board_name, sensing, therapy, stackup, ble)
                        sp = f"{r['spares']['comfortable']} / {r['spares']['max']}" if not r["failed"] else "-"
                        rows.append(f"| {sensing.split(' ')[0]} | {board_name} | {stackup} | {r['util']['top'] * 100:.0f}% | {r['util']['bottom'] * 100:.0f}% | {verdict(r)} | {sp} |")
                        key = (sensing.split(" ")[0], board_name.split(" ")[0], stackup, therapy, ble)
                        if (not HIGHLIGHT and not r["failed"]) or key in HIGHLIGHT:
                            tag = f"{key[0]}_{key[1]}_{stackup[0]}L_{'therapy' if therapy else 'sense'}_{'MDBT42Q' if ble == 'ble_module' else 'BC832'}"
                            svg(r, OUT / "layouts" / f"layout_{tag}.svg")
                print(f"done: {sensing.split(' ')[0]} therapy={therapy} {ble}", flush=True)
            rows.append("")
    (OUT / "packing_results.md").write_text("\n".join(rows))
    print("\n".join(rows))


if __name__ == "__main__":
    main()
