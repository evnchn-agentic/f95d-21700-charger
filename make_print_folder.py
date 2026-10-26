"""
Build a self-contained print/ folder: exactly the parts to print, nothing else.

Each part is emitted in the DONOR AUTHOR'S OWN print orientation -- taken from that part's
<item> transform on its plate in the source 3MF -- then dropped onto Z=0 and centred in XY.
So: drop into the slicer, no rotation needed.

Parts that the donor prints together with a printed-in support are merged into ONE STL, so
the support cannot get separated from its part by the slicer's auto-arrange.
"""
import numpy as np, trimesh, re, os, shutil, zipfile

# Read the plate transforms straight out of the donor 3MF so this script is self-contained.
SRC = os.environ.get('F95D_3MF') or os.path.expanduser('~/Downloads/共田F95D风扇外壳.3mf')
if not os.path.exists(SRC):
    raise SystemExit("set F95D_3MF to the donor 3MF (default: ~/Downloads/共田F95D风扇外壳.3mf)")
DEST=os.path.join(os.path.dirname(os.path.abspath(__file__)),'print')
if os.path.isdir(DEST): shutil.rmtree(DEST)
os.makedirs(DEST)

raw=zipfile.ZipFile(SRC).read('3D/3dmodel.model').decode('utf-8')
items={m.group(1):[float(v) for v in m.group(2).split()]
       for m in re.finditer(r'<item objectid="(\d+)"[^>]*transform="([^"]+)"', raw)}
def mat(t):
    M=np.eye(4); M[:3,:3]=np.array(t[:9]).reshape(3,3).T; M[:3,3]=t[9:]; return M

H=os.path.join(os.path.dirname(os.path.abspath(__file__)),'source-frames')
# (out name, [(mesh path, item objectid), ...], note)
JOBS=[
 ('01_front_shell.stl',            [(f'{H}/1_charger_front.stl','28')],                       'remixed 前盖'),
 ('02_back_shell.stl',             [(f'{H}/2_charger_back.stl','31')],                       'remixed 后盖'),
 ('03_battery_door.stl',           [(f'{H}/donor-parts-reused-unmodified/battery_door_A.stl','37'), (f'{H}/donor-parts-reused-unmodified/battery_door_B.stl','39')],      '电池仓盖 + its printed-in support'),
]

FLIPCHK=None
def support_area(m):
    n=m.face_normals; c=m.triangles_center; a=m.area_faces
    incl=np.degrees(np.arccos(np.clip(np.abs(n[:,2]),0,1)))
    return a[(n[:,2]<-1e-6)&(c[:,2]>=0.6)&(incl<45.0)].sum()/100

print(f"{'file':32s} {'bodies':>6s} {'bed X x Y':>16s} {'H':>6s} {'vol':>7s} {'support':>8s}  watertight")
manifest=[]
for out,parts,note in JOBS:
    ms=[]
    for path,oid in parts:
        m=trimesh.load(path)
        m.apply_transform(mat(items[oid]))
        ms.append(m)
    # relative placement is preserved because every mesh goes through its own plate transform
    if len(ms)>1:
        pre=[np.round(x.bounds,4) for x in ms]
        comb=trimesh.util.concatenate(ms)
    else:
        comb=ms[0]
    # drop to bed, centre in XY
    comb.apply_translation([-(comb.bounds[0][0]+comb.bounds[1][0])/2,
                            -(comb.bounds[0][1]+comb.bounds[1][1])/2,
                            -comb.bounds[0][2]])
    e=comb.extents
    wt = all(x.is_watertight for x in ms)
    print(f"{out:32s} {len(ms):6d} {e[0]:7.1f} x {e[1]:6.1f} {e[2]:6.1f} "
          f"{sum(x.volume for x in ms)/1000:6.2f}cc {support_area(comb):7.2f}cm2  {wt}")
    comb.export(f'{DEST}/{out}')
    manifest.append((out, note, e, sum(x.volume for x in ms)/1000, support_area(comb), len(ms)))

# ---- sanity: the merged pairs must sit apart, not intersecting, and touch the bed
print("\nmerged-pair checks:")
for out,parts,note in JOBS:
    if len(parts)<2: continue
    a=trimesh.load(parts[0][0]); a.apply_transform(mat(items[parts[0][1]]))
    b=trimesh.load(parts[1][0]); b.apply_transform(mat(items[parts[1][1]]))
    inter=trimesh.boolean.intersection([a,b],engine='manifold')
    v=0.0 if inter.is_empty else inter.volume
    both_on_bed = abs(a.bounds[0][2]-b.bounds[0][2])<0.01 or min(a.bounds[0][2],b.bounds[0][2])>=-0.01
    print(f"  {out:28s} overlap={v:8.4f} mm3   support sits on bed at Z={b.bounds[0][2]:.2f} "
          f"(part Z={a.bounds[0][2]:.2f})")

with open(f'{DEST}/PRINT.md','w') as f:
    f.write("""# Print list — 共田 F95D → 21700 charger

Everything in this folder gets printed. Nothing outside it does.

**Every file is already in the right orientation — drop it on the bed and slice, no rotation.**

| # | file | qty | material | bed | support |
|---|------|-----|----------|-----|---------|
""")
    mats={'01':'white PETG','02':'white PETG','03':'white PETG'}
    sups={'01':'yes — ~1.8 cm², all internal','02':'**yes — 17.8 cm²**, mostly the cell tower','03':'no — support is built in'}
    for out,note,e,vol,sa,n in manifest:
        k=out[:2]
        f.write(f"| {k} | `{out}` | 1 | {mats[k]} | {e[0]:.0f} × {e[1]:.0f} × {e[2]:.0f} mm | {sups[k]} |\n")
    f.write("""
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
""")
print(f"\nwrote {DEST}")
for x in sorted(os.listdir(DEST)): print("   ",x)
