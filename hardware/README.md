# PulsePatch hardware

Hardware for PulsePatch, a wearable wound patch that senses temperature, moisture and pH and can drive 405 nm light and low-frequency ultrasound. Owner: Anay. Lives on the `KiCAD` branch until it is ready for `main`.

## Layout

| Folder | What is in it |
|---|---|
| `context/` | The team synopsis (`Wolfhacks.pdf`) and the note on light plus ultrasound evidence |
| `research/raw/` | Literature reviews: `A-clinical-signals.md` (which wound signals are worth sensing) and `C-therapy-hardware.md` (light and ultrasound doses, parts, safety limits) |
| `experiments/` | Scripts and results: KiCad library scan, board packing, power and heat budget |
| `docs/board-spec.md` | The approved board spec and the list of things not verified yet |
| `kicad/gen/` | The generator. `design.py` is the single source of truth for parts, connections and placement |
| `kicad/pulsepatch/` | Generated KiCad project: schematic, board, check reports, renders |

## Build the board

Needs KiCad 10 at `/Applications/KiCad` and Java (for the autorouter).

```
cd hardware/kicad
./build.sh              # full build with autorouting, about 6 minutes
./build.sh --no-route   # placed, unrouted board in seconds
```

Then open `kicad/pulsepatch/pulsepatch.kicad_pro` in KiCad.

The build writes `erc.rpt` (schematic check), `drc.rpt` (board check), `pulsepatch-schematic.pdf`, and `render-top.png` / `render-bottom.png` into `kicad/pulsepatch/`.

## Changing the design

Edit `kicad/gen/design.py` and rebuild. The schematic and board are regenerated from it every time, so edits made by hand in the KiCad editor are lost on the next build. Once the design settles and hand routing starts, stop running the build and treat the KiCad files as the source.

## Status

See `docs/board-spec.md` for what is and is not verified. The board is autorouted and has not been reviewed by a person or fabricated.
