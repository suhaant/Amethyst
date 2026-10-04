"""Ground pours and stitching vias. Run with KiCad's bundled Python after route.py.

The autorouter runs some signals across the inner ground layer, which can cut the plane into islands.
This pours ground on the other three layers and drops a grid of ground vias wherever all four layers
are free, so the islands are tied back together.
"""
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

import design
from gen_board import OUT, PROJECT, add_zone, board_box, write_project

PCB = OUT / (PROJECT + ".kicad_pcb")
LAYERS = (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu)
STITCH_PITCH = 2.0                      # mm between candidate via positions
VIA_D, VIA_DRILL, ROOM = 0.45, 0.2, 0.35    # mm; ROOM = via radius plus a margin that must be ground on every layer
HOLE_GAP = 0.8                          # mm, minimum centre distance to a via that is already there
RING = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (0.7, 0.7), (-0.7, 0.7), (0.7, -0.7), (-0.7, -0.7))


def main():
    board = pcbnew.LoadBoard(str(PCB))
    gnd = board.FindNet("/GND")
    for layer, name in ((pcbnew.F_Cu, "GND pour top"), (pcbnew.In2_Cu, "GND pour inner 2"), (pcbnew.B_Cu, "GND pour bottom")):
        add_zone(board, layer, board_box(), gnd).SetZoneName(name)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    fills = {z.GetLayer(): z.GetFilledPolysList(z.GetLayer()) for z in board.Zones() if not z.GetIsRuleArea()}

    holes = [(ToMM(t.GetPosition().x), ToMM(t.GetPosition().y)) for t in board.GetTracks() if t.GetClass() == "PCB_VIA"]

    def near_hole(x, y):
        return any((hx - x) ** 2 + (hy - y) ** 2 < HOLE_GAP ** 2 for hx, hy in holes)

    def all_ground(x, y):
        return all(fills[layer].Contains(VECTOR2I(FromMM(x + ROOM * dx), FromMM(y + ROOM * dy)))
                   for layer in LAYERS for dx, dy in RING)

    count, y = 0, 1.0
    while y < design.BOARD_H - 0.9:
        x = 1.0
        while x < design.BOARD_W - 0.9:
            if all_ground(x, y) and not near_hole(x, y):
                via = pcbnew.PCB_VIA(board)
                via.SetPosition(VECTOR2I(FromMM(x), FromMM(y)))
                via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                try:
                    via.SetWidth(pcbnew.F_Cu, FromMM(VIA_D))
                except TypeError:
                    via.SetWidth(FromMM(VIA_D))
                via.SetDrill(FromMM(VIA_DRILL))
                via.SetNet(gnd)
                board.Add(via)
                count += 1
            x += STITCH_PITCH
        y += STITCH_PITCH
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(str(PCB), board)
    write_project()
    print("ground pours on three more layers, %d stitching vias" % count)


if __name__ == "__main__":
    main()
