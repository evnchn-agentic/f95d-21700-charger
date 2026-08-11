# Print list — 共田 F95D → 21700 charger

Everything in this folder gets printed. Nothing outside it does.

**Every file is already in the right orientation — drop it on the bed and slice, no rotation.**

| # | file | qty | material | bed | support |
|---|------|-----|----------|-----|---------|
| 01 | `01_front_shell.stl` | 1 | white PETG | 110 × 45 × 38 mm | yes — ~1.8 cm², all internal |
| 02 | `02_back_shell.stl` | 1 | white PETG | 42 × 100 × 26 mm | **yes — 17.8 cm²**, mostly the cell tower |
| 03 | `03_battery_door.stl` | 1 | white PETG | 12 × 96 × 22 mm | no — support is built in |

## Notes

* **White PETG throughout.** Not PLA — this is a lithium-cell enclosure and the donor's own
  safety notice rules PLA out.
* **Turn slicer supports ON.** `02` needs about 17.8 cm² of it, nearly all under the battery
  tower; `01` needs about 1.8 cm², all internal where you will not see it.
* `03` contains **two bodies**: the door plus the donor's printed-in support pad, already
  positioned. Load it as a single object — do not let the slicer split or re-arrange it.
  Snap the pad off with pliers after printing.
* The donor also ships a printed-in support tab for the back shell. It is **not** used here:
  it would sit on top of the relocated screw counterbore, and it saves no support anyway.
  It is kept in `../alt-53.5mm-donor-screws/` where the original screw position leaves it clear.
* After printing, pierce the two sacrificial membranes in the screw holes of `02` with a
  screwdriver — they are 0.22 mm skins that let the holes bridge.
* **The panel is sealed.** The donor's button and light-pipe parts are not printed. All seven
  panel apertures — 5 × Ø4.00 LED holes and 2 × 19.15 × 11.20 button ovals — are capped with a
  **1.0 mm skin flush with the outer face**, leaving 2 mm of the 3 mm panel as a light well
  behind each. White PETG diffuses the LEDs through that skin.
* Because the shell prints outer-face-down, those caps are laid straight onto the bed in the
  first five layers — no bridging, and they come out with bed-quality finish.
* **Trade-off, by design:** the OFF switch is no longer reachable. The charger has no exposed
  controls; plug in to charge, unplug when done.

## Hardware (not printed)

* 2 × M3×5×5 heat-set brass insert — into `01`
* 2 × M3×8 torx flat-head screw — through `02`
