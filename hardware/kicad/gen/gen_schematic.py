#!/usr/bin/env python3
"""Write pulsepatch.kicad_sch from design.py, then ask KiCad to read it back and confirm every connection.

Pins are joined by net labels placed on the pin ends (no drawn wires). After writing the file the script
exports KiCad's own netlist and fails if any pin is on a different net than design.py says.

Usage: python3 gen_schematic.py
"""
import copy
import subprocess
import sys
import uuid
from pathlib import Path

import design
import kilib
from kilib import Q, child, children

PROJECT = "pulsepatch"
OUT = Path(__file__).resolve().parent.parent / PROJECT
CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
GRID = 1.27


def uid(key):
    """Stable ids, so regenerating the schematic keeps the board's footprints linked to their symbols."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "pulsepatch/" + key))


ROOT = uid("root")


def snap(v):
    return round(round(v / GRID) * GRID, 4)


def pin_matches(pin, key):
    return key == pin["number"] or key == pin["name"] or key in pin["name"].split("/")


def pin_point(x, y, rot, pin):
    """Schematic position and outward label angle of a pin end, for a symbol at (x, y) rotated 0 or 90."""
    if rot == 0:
        px, py, ang = x + pin["x"], y - pin["y"], pin["angle"]
    else:
        px, py, ang = x - pin["y"], y - pin["x"], (pin["angle"] + 90) % 360
    return round(px, 4), round(py, 4), (ang + 180) % 360


def text_effects(size=1.27, hide=False, justify=None):
    eff = ["effects", ["font", ["size", size, size]]]
    if justify:
        eff.append(["justify"] + justify)
    if hide:
        eff.append(["hide", "yes"])
    return eff


def prop(name, value, x, y, hide=False, size=1.27, justify=None):
    return ["property", Q(name), Q(value), ["at", round(x, 4), round(y, 4), 0], text_effects(size, hide, justify)]


def label(net, x, y, angle):
    return ["label", Q(net), ["at", x, y, angle], text_effects(1.27, justify=["left" if angle in (0, 90) else "right", "bottom"]),
            ["uuid", Q(uid("label/%s/%s/%s" % (net, x, y)))]]


def build():
    lib_symbols, items, expected = ["lib_symbols"], [], {}
    cursor = {}      # block -> [next IC y, next list-row y]

    def embed(lib, name):
        sym = kilib.load_symbol(lib, name)
        if not any(str(s[1]) == lib + ":" + name for s in lib_symbols[1:]):
            emb = copy.deepcopy(sym)
            emb[1] = Q(lib + ":" + name)
            lib_symbols.append(emb)
        return sym

    def place(ref, lib, name, value, footprint, x, y, rot, pins_to_nets, in_bom=True):
        sym = embed(lib, name)
        pins = kilib.symbol_pins(sym)
        for key in pins_to_nets:
            if not any(pin_matches(p, key) for p in pins):
                sys.exit("%s: no pin '%s' on %s:%s" % (ref, key, lib, name))
        xs, ys = [p["x"] for p in pins], [p["y"] for p in pins]
        small = len(pins) <= 2
        if small:
            ref_at, val_at, size = (x, y - 2.2), (x, y + 3.4), 1.0
        else:
            ref_at, val_at, size = (x + 2.54, y - max(ys) - 6.0), (x + 2.54, y - max(ys) - 3.8), 1.27
        inst = ["symbol", ["lib_id", Q(lib + ":" + name)], ["at", x, y, rot], ["unit", 1], ["exclude_from_sim", "no"],
                ["in_bom", "yes" if in_bom else "no"], ["on_board", "yes" if footprint else "no"], ["dnp", "no"],
                ["uuid", Q(uid("sym/" + ref))],
                prop("Reference", ref, ref_at[0], ref_at[1], hide=ref.startswith("#"), size=size, justify=None if small else ["left"]),
                prop("Value", value, val_at[0], val_at[1], hide=ref.startswith("#"), size=size, justify=None if small else ["left"]),
                prop("Footprint", footprint, x, y, hide=True), prop("Datasheet", kilib.symbol_property(sym, "Datasheet") or "~", x, y, hide=True),
                prop("Description", kilib.symbol_property(sym, "Description"), x, y, hide=True)]
        inst += [["pin", Q(p["number"]), ["uuid", Q(uid("pin/%s/%s" % (ref, p["number"])))]] for p in pins]
        inst.append(["instances", ["project", Q(PROJECT), ["path", Q("/" + ROOT), ["reference", Q(ref)], ["unit", 1]]]])
        items.append(inst)
        for p in pins:
            net = next((n for key, n in pins_to_nets.items() if pin_matches(p, key)), None)
            px, py, ang = pin_point(x, y, rot, p)
            if net is not None:
                items.append(label(net, px, py, ang))
                expected[(ref, p["number"])] = net
            elif p["etype"] != "no_connect":
                items.append(["no_connect", ["at", px, py], ["uuid", Q(uid("nc/%s/%s" % (ref, p["number"])))]])
                expected[(ref, p["number"])] = None

    for block, (ox, oy) in design.SCH_CELLS.items():
        items.append(["text", Q(block), ["exclude_from_sim", "no"], ["at", ox, oy - 6, 0],
                      ["effects", ["font", ["size", 3.0, 3.0], ["bold", "yes"]], ["justify", "left", "bottom"]],
                      ["uuid", Q(uid("title/" + block))]])
        cursor[block] = [oy + 8.0, oy + 6.0]

    for part in design.PARTS:
        ox, oy = design.SCH_CELLS[part["block"]]
        pins = kilib.symbol_pins(kilib.load_symbol(part["lib"], part["sym"]))
        cur = cursor[part["block"]]
        in_bom = not part["fp"].startswith("TestPoint:")
        if len(pins) > 2:
            top, bottom = max(p["y"] for p in pins), min(p["y"] for p in pins)
            y = snap(cur[0] + top + 14.0)
            cur[0] = y - bottom + 14.0
            place(part["ref"], part["lib"], part["sym"], part["value"], part["fp"], snap(ox + 52.0), y, 0, part["pins"], in_bom=in_bom)
        else:
            vertical = all(abs(p["y"]) >= abs(p["x"]) for p in pins)
            y = snap(cur[1])
            cur[1] = y + 7.62
            place(part["ref"], part["lib"], part["sym"], part["value"], part["fp"], snap(ox + 114.0), y, 90 if vertical else 0, part["pins"], in_bom=in_bom)

    for k, net in enumerate(design.POWER_FLAGS):
        place("#FLG%02d" % (k + 1), "power", "PWR_FLAG", "PWR_FLAG", "", snap(560.0), snap(330.0 + 12.7 * k), 90, {"1": net}, in_bom=False)

    sch = ["kicad_sch", ["version", 20250114], ["generator", Q("eeschema")], ["generator_version", Q("9.0")],
           ["uuid", Q(ROOT)], ["paper", Q("A2")],
           ["title_block", ["title", Q("PulsePatch pod")], ["rev", Q("0.1")], ["comment", 1, Q("Generated by hardware/kicad/gen. Edit design.py, not this file.")]],
           lib_symbols] + items + [["sheet_instances", ["path", Q("/"), ["page", Q("1")]]], ["embedded_fonts", "no"]]
    return sch, expected


def read_back(sch_path):
    """Return {(ref, pin): net name} from KiCad's own netlist export."""
    net_path = sch_path.with_suffix(".net")
    subprocess.run([CLI, "sch", "export", "netlist", "-o", str(net_path), str(sch_path)], check=True, capture_output=True)
    tree = kilib.parse(net_path.read_text())
    found = {}
    for net in children(child(tree, "nets"), "net"):
        for node in children(net, "node"):
            found[(str(child(node, "ref")[1]), str(child(node, "pin")[1]))] = str(child(net, "name")[1])
    return found


def main():
    OUT.mkdir(exist_ok=True)
    sch, expected = build()
    sch_path = OUT / (PROJECT + ".kicad_sch")
    sch_path.write_text(kilib.dump(sch) + "\n")
    found = read_back(sch_path)
    wrong = []
    for key, net in expected.items():
        if key[0].startswith("#"):      # power flags are not in a netlist
            continue
        got = found.get(key)
        if net is None:
            if got is not None and not got.startswith("unconnected-"):
                wrong.append("%s pin %s should be unconnected, KiCad has %s" % (key[0], key[1], got))
        elif got != "/" + net:
            wrong.append("%s pin %s should be %s, KiCad has %s" % (key[0], key[1], net, got))
    nets = sorted({n for n in expected.values() if n})
    print("%d parts, %d nets, %d pins checked against KiCad's netlist: %s" % (
        len(design.PARTS), len(nets), len(expected), "ALL MATCH" if not wrong else "%d MISMATCHES" % len(wrong)))
    for line in wrong[:40]:
        print("  " + line)
    single = [n for n in nets if list(expected.values()).count(n) == 1]
    if single:
        print("nets with only one pin:", ", ".join(single))
    sys.exit(1 if wrong else 0)


if __name__ == "__main__":
    main()
