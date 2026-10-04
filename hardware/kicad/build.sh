#!/bin/bash
# Regenerate the PulsePatch schematic and board from gen/design.py and run KiCad's own checks.
# Usage: ./build.sh            full build including autorouting (about 6 minutes)
#        ./build.sh --no-route placed but unrouted board (seconds)
set -euo pipefail
cd "$(dirname "$0")"
KICAD=/Applications/KiCad/KiCad.app/Contents
PY="$KICAD/Frameworks/Python.framework/Versions/3.9/bin/python3"
CLI="$KICAD/MacOS/kicad-cli"
P=pulsepatch
JAR=tools/freerouting-2.4.1.jar

python3 gen/gen_schematic.py
"$CLI" sch erc --severity-all -o $P/erc.rpt $P/$P.kicad_sch
"$CLI" sch export pdf -o $P/$P-schematic.pdf $P/$P.kicad_sch
"$PY" gen/gen_board.py
if [ "${1:-}" != "--no-route" ]; then
  mkdir -p tools
  [ -f "$JAR" ] || curl -L -o "$JAR" https://github.com/freerouting/freerouting/releases/download/v2.4.1/freerouting-2.4.1.jar
  "$PY" gen/route.py > $P/route.log 2>&1 || { tail -5 $P/route.log; exit 1; }
  tail -1 $P/route.log
  "$PY" gen/pour.py 2>&1 | grep -v wxApp
fi
"$CLI" pcb drc --schematic-parity --severity-all --refill-zones --save-board -o $P/drc.rpt $P/$P.kicad_pcb
"$CLI" pcb render --side top -w 1000 -h 1300 --zoom 0.9 -o $P/render-top.png $P/$P.kicad_pcb
"$CLI" pcb render --side bottom -w 1000 -h 1300 --zoom 0.9 -o $P/render-bottom.png $P/$P.kicad_pcb
