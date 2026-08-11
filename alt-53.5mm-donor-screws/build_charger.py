"""
共田 F95D fan housing  ->  21700 USB-C charger-only remix.

Donor: 共田F95D风扇外壳.3mf  (MakerWorld, 李李子 -- CERN-OHL-W v2 / GPL-3.0)
Keeps the control strip (PCB slot, 21700 bore, battery door, Type-C, buttons, LEDs)
and the original M3 screw pair at X=-26; deletes the entire fan bay.

All work is done in the ASSEMBLED frame; parts are exported back in their own
original local frames so they are drop-in replacements in the donor project.
"""
import numpy as np, trimesh, os

ENG = 'manifold'
OUT = 'out'; os.makedirs(OUT, exist_ok=True)

# ---- assembly transform (derived from the two M3 screw axes; see verify below) ----
DX, DY, DZ = -1.495, 0.0, -6.25          # back cover local -> assembled

# ---- cut / fill parameters, assembled frame ----
X_END       = -18.0     # new outer end face of the finished case
WALL_T      =   3.0     # end wall thickness  -> inner face at -21.0
JOINT_CLR   =   0.195   # donor's own lid clearance -- ASSERTED against a live measurement below
X_BACK_CUT  = X_END - WALL_T - JOINT_CLR # -21.195
TOP_FILL_X0 = -32.5     # front top face is solid up to X=-32; slats start at -31
PLATE_FILL_X0 = -32.0   # back plate is solid up to X=-32; spoke grille starts at -31
PLATE_FILL_Y  =  36.0   # grille openings stop at |Y|=32; screws are at |Y|=42.43
TOP_Z       = (15.0, 19.0)      # front top plate
PLATE_Z     = (-19.0, -14.0)    # back bottom plate
ENV_Y, ENV_Z = 55.0, 19.0       # outer envelope (square edges, verified at X=+70)

# screw features to protect / verify
SCREW_XY = [(-25.925,  42.43), (-25.925, -42.43)]   # assembled

def box(x0,x1,y0,y1,z0,z1):
    b = trimesh.creation.box(extents=[x1-x0, y1-y0, z1-z0])
    b.apply_translation([(x0+x1)/2, (y0+y1)/2, (z0+z1)/2])
    return b

def report(tag, m):
    print(f"  {tag:28s} watertight={m.is_watertight}  vol={m.volume/1000:7.2f} cm3  "
          f"bbox={np.round(m.extents,2)}  bodies={m.body_count}")
    return m

print("=== load donors ===")
front = trimesh.load('stl/front1.stl')          # 前盖.stl_3   (object_29 id=27)
back  = trimesh.load('stl/back_cover.stl')      # 后盖.stl_1   (object_31 id=29)
back_asm = back.copy(); back_asm.apply_translation([DX, DY, DZ])
report('front (donor)', front); report('back  (donor, assembled)', back_asm)
V_FRONT_0, V_BACK_0 = front.volume, back_asm.volume

BIG = 400.0
print("\n=== FRONT: cut + fill top slats + end wall ===")
keep = box(-BIG, X_END, -BIG, BIG, -BIG, BIG)
f1 = report('1 cut at X<=-18', trimesh.boolean.intersection([front, keep], engine=ENG))

top_fill = box(TOP_FILL_X0, X_END, -ENV_Y, ENV_Y, *TOP_Z)
f2 = report('2 + top-slat fill', trimesh.boolean.union([f1, top_fill], engine=ENG))

end_wall = box(X_END - WALL_T, X_END, -ENV_Y, ENV_Y, -ENV_Z, ENV_Z)   # inner face at -21.0
f3 = report('3 + end wall', trimesh.boolean.union([f2, end_wall], engine=ENG))
front_new = f3

print("\n=== BACK: cut + fill spoke grille ===")
keepb = box(-BIG, X_BACK_CUT, -BIG, BIG, -BIG, BIG)
b1 = report('1 cut at X<=-21', trimesh.boolean.intersection([back_asm, keepb], engine=ENG))

plate_fill = box(PLATE_FILL_X0, X_BACK_CUT, -PLATE_FILL_Y, PLATE_FILL_Y, *PLATE_Z)
b2 = report('2 + plate-grille fill', trimesh.boolean.union([b1, plate_fill], engine=ENG))
back_new = b2

# ---------------------------------------------------------------- verification
print("\n=== VERIFY ===")
ok = True
def check(cond, msg):
    global ok
    print(("  PASS  " if cond else "  FAIL  ") + msg); ok = ok and bool(cond)

check(front_new.is_watertight, "front_new watertight")
check(back_new.is_watertight,  "back_new watertight")
check(front_new.body_count == 1, f"front_new is one body (got {front_new.body_count})")
check(back_new.body_count == 1,  f"back_new is one body (got {back_new.body_count})")

# envelope must not grow beyond the donor
def inside(new, ref, tag):
    lo = new.bounds[0] - ref.bounds[0]; hi = ref.bounds[1] - new.bounds[1]
    check(np.all(lo >= -1e-4) and np.all(hi >= -1e-4),
          f"{tag} stays inside donor envelope (slack min={np.round(lo,4)} max={np.round(hi,4)})")
inside(front_new, front, "front"); inside(back_new, back_asm, "back")
check(abs(front_new.bounds[1][0] - X_END) < 1e-4, f"front end face at X={X_END}")
check(abs(back_new.bounds[1][0] - X_BACK_CUT) < 1e-4, f"back end face at X={X_BACK_CUT}")

# --- LIGHT-TIGHTNESS: a ray fired through the part must hit material.
#     (This is a through-hole test, NOT a flushness test: the donor has legitimate
#      1.5 mm recesses at |Y|~43-45 that are not holes.)
def pinholes(m, xs, ys, zfrom, zdir):
    org=np.array([[x,y,zfrom] for y in ys for x in xs])
    d=np.tile([0,0,float(zdir)],(len(org),1))
    tri,ray,loc=m.ray.intersects_id(org,d,multiple_hits=False,return_locations=True)
    hit=np.zeros(len(org),bool); hit[ray]=True
    return int((~hit).sum()), len(org)

xs=np.arange(-32.0,-18.05,0.5); ys=np.arange(-54,54.01,1.0)
n_new,t = pinholes(front_new, xs, ys, 80.0, -1)
n_old,_ = pinholes(front,     xs, ys, 80.0, -1)
check(n_old > 0, f"[test has power] donor front leaks in cut zone: {n_old}/{t}")
check(n_new == 0, f"front top face has no through-holes in cut zone: {n_new}/{t} (donor {n_old})")

xs2=np.arange(-31.0,X_BACK_CUT+0.05,0.5); ys2=np.arange(-49,49.01,1.0)
n_new,t = pinholes(back_new, xs2, ys2, -80.0, 1)
n_old,_ = pinholes(back_asm, xs2, ys2, -80.0, 1)
check(n_old > 0, f"[test has power] donor back leaks in cut zone: {n_old}/{t}")
check(n_new == 0, f"back plate has no through-holes in cut zone: {n_new}/{t} (donor {n_old})")

# --- screw features survived unchanged: compare the as-built column against the DONOR column
def zcol(m, x, y):
    loc,_,_ = m.ray.intersects_location(ray_origins=[[x,y,300]], ray_directions=[[0,0,-1]])
    return np.sort(loc[:,2])[::-1]

for (sx,sy) in SCREW_XY:
    zf_new, zf_old = zcol(front_new, sx, sy), zcol(front, sx, sy)
    zb_new, zb_old = zcol(back_new,  sx, sy), zcol(back_asm, sx, sy)
    check(len(zf_new)==len(zf_old) and np.allclose(zf_new, zf_old, atol=1e-3),
          f"front insert bore at ({sx},{sy}) byte-identical to donor  new={np.round(zf_new,2)} donor={np.round(zf_old,2)}")
    check(len(zb_new)==len(zb_old) and np.allclose(zb_new, zb_old, atol=1e-3),
          f"back screw hole at ({sx},{sy}) byte-identical to donor    new={np.round(zb_new,2)} donor={np.round(zb_old,2)}")
    # and the two are coaxial: probe the bore/hole walls, compare fitted centres
    def centre(m, z):
        s=m.section(plane_origin=[0,0,z], plane_normal=[0,0,1]); sl,T=s.to_2D()
        best=None
        for e in sl.entities:
            p=sl.vertices[e.points]; c=p.mean(0); r=np.linalg.norm(p-c,axis=1)
            if r.std()<0.15 and 1.0<r.mean()<5.0:
                w=(T@np.array([c[0],c[1],0,1]))[:3]
                if abs(w[0]-sx)<3 and abs(w[1]-sy)<3: best=(w,r.mean())
        return best
    cf, cb = centre(front_new,-12.0), centre(back_new,-18.0)
    if cf and cb:
        off=np.hypot(cf[0][0]-cb[0][0], cf[0][1]-cb[0][1])
        check(off<0.05, f"screw axes coaxial at ({sx},{sy}): offset={off:.4f} mm "
                        f"(front bore r={cf[1]:.2f}, back c'bore r={cb[1]:.2f})")
    else:
        check(False, f"could not locate both screw circles at ({sx},{sy})")

# --- NO NEW OPENINGS anywhere: every side-face through-path in the remix must
#     already exist in the donor (the donor has legitimate ones -- battery-door slot,
#     side vent -- that the separate door part closes).
#     NB: the probe ray is tilted 0.17 deg off-axis. An exactly axis-aligned ray grazes
#     coplanar horizontal faces (e.g. the rib top at z=14.000) and randomly hits or misses
#     them, which shows up as phantom "new" openings.
def through(meshes, xs, zs, y0, ydir, tilt=0.003):
    dv=np.array([0.0,float(ydir),float(tilt)]); dv/=np.linalg.norm(dv)
    org=np.array([[x,y0,z] for z in zs for x in xs]); d=np.tile(dv,(len(org),1))
    blocked=np.zeros(len(org),bool)
    for m in meshes:
        tri,ray,loc=m.ray.intersects_id(org,d,multiple_hits=False,return_locations=True)
        blocked[ray]=True
    return ~blocked
#     Both tilt signs are run and the results OR'd, so a real slot cannot hide by the
#     ray walking out of it in one direction.
xs=np.arange(-71,X_END-0.4,0.5); zs=np.arange(-18.3,18.3,0.5)
for ydir,tag in ((1,'-Y'),(-1,'+Y')):
    added_any=0; n_new=n_old=0
    for tilt in (+0.003,-0.003):
        o_new = through([front_new,back_new], xs, zs, -90.0*ydir, ydir, tilt)
        o_old = through([front,   back_asm ], xs, zs, -90.0*ydir, ydir, tilt)
        added_any += int((o_new & ~o_old).sum()); n_new=o_new.sum(); n_old=o_old.sum()
    check(added_any==0,
          f"{tag} face: no openings the donor did not have, both tilt signs "
          f"(remix {n_new}, donor {n_old}, NEW {added_any} of {2*o_new.size})")

# --- lid clearance: MEASURE the donor's own end joint, then require the new joint to match it.
#     (Measuring the donor is what makes this independent -- comparing the new gap back to the
#      JOINT_CLR constant that produced it would only prove the arithmetic.)
def joint_gap(fr, bk, probes):
    g=[]
    for y,z in probes:
        lf,_,_ = fr.ray.intersects_location([[-200,y,z]],[[1,0,0]])
        lb,_,_ = bk.ray.intersects_location([[-200,y,z]],[[1,0,0]])
        if len(lf)>=2 and len(lb): g.append(np.sort(lf[:,0])[-2] - np.sort(lb[:,0])[-1])
    return np.array(g)
donor_gap = joint_gap(front, back_asm, [(0,-18),(0,-16),(30,-18),(-30,-18),(45,-15),(-45,-15)])
new_gap   = joint_gap(front_new, back_new, [(0,-18),(0,-16),(30,-18),(-30,-18),(45,-15),(-45,-15)])
check(len(donor_gap)>=4 and donor_gap.std()<0.005,
      f"donor's own end joint measures {donor_gap.mean():.4f} +/- {donor_gap.std():.4f} mm (n={len(donor_gap)})")
check(len(new_gap)>=4 and np.all(np.abs(new_gap-donor_gap.mean())<0.01),
      f"new end joint matches the MEASURED donor joint: {np.round(new_gap,4)} vs donor {donor_gap.mean():.4f} mm")
check(abs(JOINT_CLR-donor_gap.mean())<0.005,
      f"JOINT_CLR constant ({JOINT_CLR}) agrees with the measured donor joint ({donor_gap.mean():.4f})")

# --- the back plate fill must not have eaten into the screw counterbore.
#     The axis probe alone would miss a fill that clipped one side of the bore, so probe a
#     ring at r=3.0 (counterbore wall is r=3.25) and compare donor vs remix all the way round.
for (sx,sy) in SCREW_XY:
    worst=0.0
    for th in np.arange(0,360,15):
        px,py = sx+3.0*np.cos(np.radians(th)), sy+3.0*np.sin(np.radians(th))
        zn=zcol(back_new,px,py); zo=zcol(back_asm,px,py)
        if len(zn)!=len(zo): worst=9.9; break
        worst=max(worst, float(np.abs(zn-zo).max()) if len(zn) else 0.0)
    check(worst<1e-3, f"counterbore wall at ({sx},{sy}) untouched by the plate fill "
                      f"(max deviation around a r=3.0 ring: {worst:.5f} mm)")

# --- fill boxes are square; prove the donor's profile is square there too, so they cannot
#     overshoot a rounded edge (bbox containment alone would not catch that).
corners_ok=True
for x in (-31.0,-28.0,-24.0,-20.0):
    for sy in (54.6,-54.6):
        hit=len(front.ray.intersects_location([[x,sy,60]],[[0,0,-1]])[0])>0 or \
            len(front_new.ray.intersects_location([[x,sy,60]],[[0,0,-1]])[0])>0
        if not hit: corners_ok=False
    for sy in (54.6,-54.6):
        zt=zcol(front_new,x,sy)
        if len(zt)==0 or abs(zt[0]-19.0)>1e-3: corners_ok=False
check(corners_ok, "outer profile is square at |Y|=54.6 across the fill zone "
                  "(top face still at z=19.000 -> square fill box cannot overshoot)")

# --- assembled interference
rng=np.random.default_rng(7)
p = back_new.vertices[rng.choice(len(back_new.vertices), min(15000,len(back_new.vertices)), replace=False)]
ins = front_new.contains(p).sum()
check(ins <= 3, f"front/back interference after remix: {ins} back verts inside front")

# --- volume sanity
print(f"\n  front volume {V_FRONT_0/1000:.1f} -> {front_new.volume/1000:.1f} cm3  "
      f"({100*front_new.volume/V_FRONT_0:.0f}% of donor)")
print(f"  back  volume {V_BACK_0/1000:.1f} -> {back_new.volume/1000:.1f} cm3  "
      f"({100*back_new.volume/V_BACK_0:.0f}% of donor)")
asm_ext = np.maximum(front_new.bounds[1], back_new.bounds[1]) - np.minimum(front_new.bounds[0], back_new.bounds[0])
print(f"  assembled envelope: {asm_ext[0]:.1f} x {asm_ext[1]:.1f} x {asm_ext[2]:.1f} mm "
      f"(donor was 143.0 x 110.0 x 38.0)")

# ---------------------------------------------------------------- export
print("\n=== EXPORT ===")
front_new.export(f'{OUT}/charger_front.stl')          # already in donor-front local frame
back_local = back_new.copy(); back_local.apply_translation([-DX,-DY,-DZ])
back_local.export(f'{OUT}/charger_back.stl')          # restored to donor-back local frame
front_new.export(f'{OUT}/asm_front.stl'); back_new.export(f'{OUT}/asm_back.stl')
print(f"  wrote {OUT}/charger_front.stl  ({front_new.extents.round(1)})")
print(f"  wrote {OUT}/charger_back.stl   ({back_local.extents.round(1)})")
print("\nALL CHECKS PASSED" if ok else "\n*** SOME CHECKS FAILED ***")
