"""Build pulsepatch.kicad_pcb from design.py and the netlist KiCad exported from the generated schematic.

Run with KiCad's bundled Python (it provides the pcbnew module):
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 gen_board.py

Nets and symbol links come from the netlist, so the board always matches what KiCad reads from the schematic.
Hand-placed parts use the coordinates in design.py; the rest are flowed into their block's region on the top side.
The output is placed but unrouted. route.py does the routing.
"""
import json
import math
import sys
from pathlib import Path

import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

import design
import kilib
from kilib import child, children

PROJECT = "pulsepatch"
OUT = Path(__file__).resolve().parent.parent / PROJECT
GAP = 0.35            # mm between neighbouring courtyards when flowing parts
ROW_TARGET = 3.55     # mm, small parts stack in a column up to this height
BOARD_THICKNESS = 0.8


def pt(x, y):
    return VECTOR2I(FromMM(x), FromMM(y))


def read_netlist():
    tree = kilib.parse((OUT / (PROJECT + ".net")).read_text())
    comps = {str(child(c, "ref")[1]): str(child(c, "tstamps")[1]) for c in children(child(tree, "components"), "comp")}
    fields = {str(child(c, "ref")[1]): (str((child(c, "datasheet") or [0, ""])[1]), str((child(c, "description") or [0, ""])[1]))
              for c in children(child(tree, "components"), "comp")}
    pads = {}
    for net in children(child(tree, "nets"), "net"):
        for node in children(net, "node"):
            pads[(str(child(node, "ref")[1]), str(child(node, "pin")[1]))] = str(child(net, "name")[1])
    return comps, pads, fields


def courtyard_box(fp):
    """Courtyard extents (x0, y0, x1, y1) in mm relative to the footprint's current position."""
    boxes = [g.GetBoundingBox() for g in fp.GraphicalItems() if g.GetLayer() in (pcbnew.F_CrtYd, pcbnew.B_CrtYd)]
    if not boxes:
        boxes = [p.GetBoundingBox() for p in fp.Pads()]
    pos = fp.GetPosition()
    return (ToMM(min(b.GetLeft() for b in boxes) - pos.x), ToMM(min(b.GetTop() for b in boxes) - pos.y),
            ToMM(max(b.GetRight() for b in boxes) - pos.x), ToMM(max(b.GetBottom() for b in boxes) - pos.y))


def circle_points(cx, cy, r, n=48):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def board_box(margin=0.3):
    w, h = design.BOARD_W, design.BOARD_H
    return [(margin, margin), (w - margin, margin), (w - margin, h - margin), (margin, h - margin)]


def add_zone(board, layer, points, net=None):
    zone = pcbnew.ZONE(board)
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in points:
        outline.Append(FromMM(x), FromMM(y))
    if net is not None:
        zone.SetLayer(layer)
        zone.SetNet(net)
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        zone.SetMinThickness(FromMM(0.2))
        zone.SetLocalClearance(FromMM(0.2))
    board.Add(zone)
    return zone


DEFAULT_CLASS = {"name": "Default", "clearance": 0.2, "track_width": 0.2, "via_diameter": 0.6, "via_drill": 0.3,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
                 "diff_pair_via_gap": 0.25, "bus_width": 12, "wire_width": 6, "line_style": 0, "priority": 2147483647,
                 "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)", "tuning_profile": ""}


def write_project():
    """Board rules that live in the project file. Call after saving the board: saving resets this file.

    0.1 mm minimum track (the router necks down at fine-pitch pads), 0.45/0.2 mm vias, 0.15 mm clearance,
    and a Power class routed 0.4 mm wide.
    """
    path = OUT / (PROJECT + ".kicad_pro")
    pro = json.loads(path.read_text()) if path.exists() else {"meta": {"filename": path.name, "version": 3}}
    rules = pro.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rules", {})
    rules.update(min_track_width=0.1, min_via_diameter=0.4, min_through_hole_diameter=0.2)
    net_settings = pro.setdefault("net_settings", {})
    default = next((c for c in net_settings.get("classes", []) if c.get("name") == "Default"), DEFAULT_CLASS)
    default.update(clearance=0.15, via_diameter=0.45, via_drill=0.2)
    net_settings["classes"] = [default, dict(default, name="Power", track_width=0.4, priority=0)]
    net_settings["netclass_patterns"] = [{"netclass": "Power", "pattern": "/" + n} for n in design.POWER_NETS]
    path.write_text(json.dumps(pro, indent=2) + "\n")


def main():
    comps, pad_net, fields = read_netlist()
    board = pcbnew.CreateEmptyBoard()
    board.SetCopperLayerCount(4)
    board.GetDesignSettings().SetBoardThickness(FromMM(BOARD_THICKNESS))

    nets = {}
    for name in sorted(set(pad_net.values())):
        nets[name] = pcbnew.NETINFO_ITEM(board, name)
        board.Add(nets[name])

    edge = pcbnew.PCB_SHAPE(board)
    edge.SetShape(pcbnew.SHAPE_T_RECT)
    edge.SetStart(pt(0, 0))
    edge.SetEnd(pt(design.BOARD_W, design.BOARD_H))
    edge.SetLayer(pcbnew.Edge_Cuts)
    edge.SetWidth(FromMM(0.1))
    board.Add(edge)

    cursor = {name: dict(x=box[0], row_y=box[1], row_h=0.0, col_x=0.0, col_w=0.0, col_used=0.0) for name, box in design.REGIONS.items()}
    problems = []
    for part in design.PARTS:
        ref = part["ref"]
        lib, name = part["fp"].split(":")
        fp = pcbnew.FootprintLoad(str(kilib.SHARE / "footprints" / (lib + ".pretty")), name)
        if fp is None:
            sys.exit("footprint %s not found for %s" % (part["fp"], ref))
        fp.SetReference(ref)
        fp.SetValue(part["value"])
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetPath(pcbnew.KIID_PATH("/" + comps[ref]))
        fp.SetSheetname("/")
        fp.SetSheetfile(PROJECT + ".kicad_sch")
        fp.SetField("Datasheet", fields[ref][0])
        fp.SetField("Description", fields[ref][1])
        fp.Reference().SetVisible(False)        # board is too dense for designators on the silkscreen
        for zone in fp.Zones():                 # the module's inner keep-out covers two of its own pads
            if zone.GetIsRuleArea() and not zone.GetLayerSet().Contains(pcbnew.B_Cu):
                zone.SetDoNotAllowPads(False)
                zone.SetDoNotAllowFootprints(False)
        fp.SetPosition(pt(0, 0))
        board.Add(fp)

        if part["at"] is not None:
            x, y, rot, side = part["at"]
            fp.SetOrientationDegrees(rot)
            if y is None:                      # radio module: antenna end flush with the top board edge
                y = -courtyard_box(fp)[1]
                print("module %s courtyard spans y 0.0 to %.2f mm" % (ref, y + courtyard_box(fp)[3]))
            fp.SetPosition(pt(x, y))
            if side == "B":
                fp.SetLayerAndFlip(pcbnew.B_Cu)
        else:
            region = design.BLOCK_REGION[part["block"]]
            x0, y0, x1, y1 = design.REGIONS[region]
            bx0, by0, bx1, by1 = courtyard_box(fp)
            w, h = bx1 - bx0, by1 - by0
            cur = cursor[region]
            if cur["col_w"] and w <= cur["col_w"] + 0.1 and cur["col_used"] + GAP + h <= max(cur["row_h"], ROW_TARGET):
                x, y = cur["col_x"], cur["row_y"] + cur["col_used"] + GAP      # stack under the previous part
                cur["col_used"] += GAP + h
                cur["row_h"] = max(cur["row_h"], cur["col_used"])
            else:
                if cur["x"] + w > x1:                                           # start a new row
                    cur["x"], cur["row_y"], cur["row_h"] = x0, cur["row_y"] + cur["row_h"] + GAP, 0.0
                x, y = cur["x"], cur["row_y"]
                cur.update(col_x=x, col_w=w, col_used=h, x=x + w + GAP, row_h=max(cur["row_h"], h))
            if y + h > y1:
                problems.append("%s does not fit in region %s" % (ref, region))
            fp.SetPosition(pt(x - bx0, y - by0))

        for p in fp.Pads():
            net = pad_net.get((ref, p.GetNumber()))
            if net is not None:
                p.SetNet(nets[net])

    # Piezo disc: outline on the bottom silkscreen, and no bottom-layer tracks or copper under it.
    cx, cy = design.PIEZO_CENTRE
    ring = pcbnew.PCB_SHAPE(board)
    ring.SetShape(pcbnew.SHAPE_T_CIRCLE)
    ring.SetCenter(pt(cx, cy))
    ring.SetEnd(pt(cx + design.PIEZO_DISC_D / 2, cy))
    ring.SetLayer(pcbnew.B_SilkS)
    ring.SetWidth(FromMM(0.15))
    board.Add(ring)
    keepout = add_zone(board, pcbnew.B_Cu, circle_points(cx, cy, design.PIEZO_D / 2))
    keepout.SetIsRuleArea(True)
    layers = pcbnew.LSET()
    layers.AddLayer(pcbnew.B_Cu)
    keepout.SetLayerSet(layers)
    keepout.SetDoNotAllowTracks(True)
    keepout.SetDoNotAllowVias(False)
    keepout.SetDoNotAllowPads(False)
    keepout.SetDoNotAllowFootprints(False)
    (getattr(keepout, "SetDoNotAllowZoneFills", None) or keepout.SetDoNotAllowCopperPour)(True)
    keepout.SetZoneName("piezo disc")

    # Ground plane on inner layer 1. route.py adds ground pours on the other three layers after routing.
    add_zone(board, pcbnew.In1_Cu, board_box(), nets["/GND"]).SetZoneName("GND plane")

    pcbnew.SaveBoard(str(OUT / (PROJECT + ".kicad_pcb")), board)
    write_project()
    print("placed %d footprints, %d nets" % (len(design.PARTS), len(nets)))
    for line in problems:
        print("PROBLEM: " + line)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
