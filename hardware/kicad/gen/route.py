"""Autoroute pulsepatch.kicad_pcb with Freerouting. pour.py adds the ground pours afterwards.

Run with KiCad's bundled Python after gen_board.py:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 route.py

Needs Java and tools/freerouting-2.4.1.jar (see build.sh). The result is a starting point: check the
radio, the switching converters and the piezo drive by eye in the KiCad editor before fabricating.
"""
import subprocess
import sys
from pathlib import Path

import pcbnew

from gen_board import write_project

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "pulsepatch"
JAR = HERE.parent / "tools" / "freerouting-2.4.1.jar"
PCB = OUT / "pulsepatch.kicad_pcb"
MAX_PASSES = "40"


def main():
    dsn, ses = OUT / "pulsepatch.dsn", OUT / "pulsepatch.ses"
    board = pcbnew.LoadBoard(str(PCB))
    if not pcbnew.ExportSpecctraDSN(board, str(dsn)):
        sys.exit("could not export " + dsn.name)
    if "(class Power" not in dsn.read_text():
        print("warning: Power net class did not reach the router; all tracks will be 0.2 mm")
    if ses.exists():
        ses.unlink()
    subprocess.run(["java", "-Djava.awt.headless=true", "-jar", str(JAR), "-de", str(dsn), "-do", str(ses),
                    "-mp", MAX_PASSES, "--gui.enabled=false"], check=False)
    if not ses.exists():
        sys.exit("Freerouting did not write " + ses.name)
    board = pcbnew.LoadBoard(str(PCB))
    if not pcbnew.ImportSpecctraSES(board, str(ses)):
        sys.exit("could not import " + ses.name)
    pcbnew.SaveBoard(str(PCB), board)
    write_project()
    tracks = [t for t in board.GetTracks()]
    vias = sum(1 for t in tracks if t.GetClass() == "PCB_VIA")
    print("routed: %d track segments, %d vias" % (len(tracks) - vias, vias))


if __name__ == "__main__":
    main()
