"""
共田 F95D fan housing -> 21700 USB-C charger, SHORT variant.

Same method as build_charger.py, but the M3 screw pair is relocated 7.8 mm further -X,
into the -X end of the donor's own boss lobe, which lets the case end 8.1 mm sooner.

Length: 53.5 mm (keep-donor-screws)  ->  45.4 mm.

The limit on going shorter is the battery bay's own end wall at X = -40.0..-38.49: a boss
must clear it, so BOSS_X >= -33.8 for a Phi8 boss. The donor's lobe only has 6 mm of solid
on the -X side of its existing bore, which is not enough for a second Phi7.6 envelope, so
the boss is extended 2.75 mm further -X with new material welded onto the lobe.
"""
import numpy as np, trimesh, os

ENG='manifold'; OUT='out_short'; os.makedirs(OUT, exist_ok=True)
DX,DY,DZ = -1.495, 0.0, -6.25

# --- screw geometry, all measured off the donor -------------------------------
BOSS_Y      =  42.43
BOSS_R      =   4.0     # new boss outer radius (1.7 mm wall round the insert bore)
BORE_R      =   2.30    # donor's M3x5x5 insert bore
BORE_Z      = (-14.0, -7.0)   # open at the bottom, blind at -7 (donor: identical)
HOLE_R      =   1.95    # donor's back through-hole
CB_R        =   3.25    # donor's counterbore
CB_Z        = (-19.0, -17.5)  # 1.5 mm deep
MEMBRANE_Z  = (-17.5, -17.28) # donor's 0.22 mm sacrificial layer, replicated
PLATE_Z     = (-19.0, -14.0)

BOSS_X      = -33.75    # -X limit set by the bay end wall at -38.49 (0.74 mm clearance)
PLATE_MARGIN=   1.25    # plate left beyond the counterbore
JOINT_CLR   =   0.195   # donor's own lid clearance (asserted against measurement below)
WALL_T      =   3.0

BACK_END = BOSS_X + CB_R + PLATE_MARGIN          # -29.25
X_END    = BACK_END + JOINT_CLR + WALL_T         # -26.055
TOP_FILL_X0, PLATE_FILL_X0, PLATE_FILL_Y = -32.5, -32.0, 36.0
TOP_Z = (15.0,19.0); ENV_Y, ENV_Z = 55.0, 19.0
OLD_SCREW_X = -25.925                            # donor's, removed by the shorter cut

def box(x0,x1,y0,y1,z0,z1):
    b=trimesh.creation.box(extents=[x1-x0,y1-y0,z1-z0])
    b.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]); return b
def cyl(x,y,z0,z1,r,sections=256):
    c=trimesh.creation.cylinder(radius=r, height=z1-z0, sections=sections)
    c.apply_translation([x,y,(z0+z1)/2]); return c
def rpt(t,m):
    print(f"  {t:34s} wt={m.is_watertight} vol={m.volume/1000:7.2f} cm3 "
          f"bbox={np.round(m.extents,2)} bodies={m.body_count}"); return m

print(f"=== SHORT VARIANT   BOSS_X={BOSS_X}  BACK_END={BACK_END:.3f}  X_END={X_END:.3f}")
print(f"    case length = {abs(-71.5 - X_END):.3f} mm  (keep-donor-screws variant: 53.500)\n")
front=trimesh.load('stl/front1.stl'); back=trimesh.load('stl/back_cover.stl')
back_asm=back.copy(); back_asm.apply_translation([DX,DY,DZ])
BIG=400.0

print("=== FRONT ===")
f=rpt('1 cut at X<=%.3f'%X_END, trimesh.boolean.intersection([front, box(-BIG,X_END,-BIG,BIG,-BIG,BIG)],engine=ENG))
for sy in (BOSS_Y,-BOSS_Y):
    f=trimesh.boolean.union([f, cyl(BOSS_X,sy,-14.0,7.0,BOSS_R)],engine=ENG)
f=rpt('2 + 2 boss COLUMNS (z -14..+7)', f)
f=rpt('3 + top-slat fill', trimesh.boolean.union([f, box(TOP_FILL_X0,X_END,-ENV_Y,ENV_Y,*TOP_Z)],engine=ENG))
f=rpt('4 + end wall (plugs old bore)', trimesh.boolean.union([f, box(X_END-WALL_T,X_END,-ENV_Y,ENV_Y,-ENV_Z,ENV_Z)],engine=ENG))
for sy in (BOSS_Y,-BOSS_Y):
    f=trimesh.boolean.difference([f, cyl(BOSS_X,sy,-14.5,BORE_Z[1],BORE_R)],engine=ENG)
front_new=rpt('5 - 2 insert bores', f)

# --- 6. CAP the 7 panel apertures (5x LED, 2x button) with a 1.0 mm skin flush with the
#     outer face. The button and light-pipe parts are not printed; white PETG diffuses the
#     LEDs through the skin, and the remaining 2 mm of the 3 mm panel stays as a light well.
#     Done as a boolean (slab minus shell) so the caps follow the ovals' outward taper
#     exactly, instead of me reconstructing their profile.
PANEL_SKIN = 1.0
# The slab must sit ONLY where the outer face is exactly flat at z=19: the shell has a small
# corner radius, and overshooting it leaves zero-volume flakes. Inset well clear -- the
# apertures live at X -49..-51, |Y|<=32, so a generous inset costs nothing. Asserted below.
CAP_BOX = (-70.0, X_END-1.0, -53.0, 53.0)
_xs=np.arange(CAP_BOX[0]+0.25, CAP_BOX[1], 0.5); _ys=np.arange(CAP_BOX[2]+0.25, CAP_BOX[3], 0.5)
_o=np.array([[x,y,200.] for y in _ys for x in _xs]); _d=np.tile([0,0,-1.],(len(_o),1))
_,_r,_l=front_new.ray.intersects_id(_o,_d,multiple_hits=False,return_locations=True)
_z=np.full(len(_o),19.0); _z[_r]=_l[:,2]
_hit=np.zeros(len(_o),bool); _hit[_r]=True
# Non-flat is expected in a ring around each aperture (the donor chamfers the lead-in, down
# to z=18.40) -- the cap is meant to fill that too. Everywhere ELSE must be flat at 19.000,
# or the slab overshoots the surface and leaves zero-volume flakes.
_APXY=[(-49.09,y,2.0) for y in (-14.,-7.,0.,7.,14.)]+[(-51.34,26.70,None),(-51.34,-26.70,None)]
_bad=_hit & (np.abs(_z-19.0)>1e-3)
_XY=_o[:,:2]
_nearap=np.zeros(len(_o),bool)
for _ax,_ay,_r0 in _APXY:
    _nearap |= (np.hypot(_XY[:,0]-_ax,_XY[:,1]-_ay)<4.0) if _r0 else \
               ((np.abs(_XY[:,0]-_ax)<12.0)&(np.abs(_XY[:,1]-_ay)<8.0))
_notflat=int((_bad & ~_nearap).sum())
assert _notflat==0, f"outer face is not flat at z=19 in {_notflat} spots away from any aperture"
print(f"  [precondition] outer face flat at z=19.000 outside the aperture chamfers "
      f"({int(_bad.sum())} chamfer samples, 0 stray)")
cap_slab = box(CAP_BOX[0], CAP_BOX[1], CAP_BOX[2], CAP_BOX[3], 19.0-PANEL_SKIN, 19.0)
# Union the whole slab, not just the extracted void: the slab overlaps 1 mm into the 3 mm
# panel everywhere else, so the added solid INTERSECTS existing material instead of being
# face-tangent to the aperture walls. The tangent version produced 3 coincident-but-distinct
# vertices (euler -4) that survived is_watertight but pinched on export.
V_CAPS = trimesh.boolean.difference([cap_slab, front_new], engine=ENG).volume
front_new = rpt('6 + panel caps (7 apertures)', trimesh.boolean.union([front_new, cap_slab], engine=ENG))


print("\n=== BACK ===")
b=rpt('1 cut at X<=%.3f'%BACK_END, trimesh.boolean.intersection([back_asm, box(-BIG,BACK_END,-BIG,BIG,-BIG,BIG)],engine=ENG))
b=rpt('2 + plate-grille fill', trimesh.boolean.union([b, box(PLATE_FILL_X0,BACK_END,-PLATE_FILL_Y,PLATE_FILL_Y,*PLATE_Z)],engine=ENG))
for sy in (BOSS_Y,-BOSS_Y):
    b=trimesh.boolean.difference([b, cyl(BOSS_X,sy,-19.5,CB_Z[1],CB_R)],engine=ENG)          # counterbore
    b=trimesh.boolean.difference([b, cyl(BOSS_X,sy,MEMBRANE_Z[1],-13.5,HOLE_R)],engine=ENG)  # through-hole above the membrane
back_new=rpt('3 - counterbores + holes', b)

# ------------------------------------------------------------------ verify
print("\n=== VERIFY ===")
ok=True
def check(c,m):
    global ok; print(("  PASS  " if c else "  FAIL  ")+m); ok=ok and bool(c)
def zcol(m,x,y):
    l,_,_=m.ray.intersects_location([[x,y,300]],[[0,0,-1]]); return np.sort(l[:,2])[::-1]

def integrity(m, tag):
    """is_watertight alone is not enough: it passes on coincident-but-distinct vertices,
    which merge into a pinch the moment the mesh is written to STL. Check the artifact."""
    import tempfile, os as _os
    dup = len(m.vertices) - len(np.unique(np.round(m.vertices,6), axis=0))
    pieces = len(m.split(only_watertight=False))
    with tempfile.TemporaryDirectory() as td:
        f_ = _os.path.join(td,'rt.stl'); m.export(f_); rt = trimesh.load(f_)
    check(m.is_watertight and m.body_count==1 and pieces<=1 and dup==0
          and rt.is_watertight and len(trimesh.repair.broken_faces(rt))==0,
          f"{tag} sound: watertight={m.is_watertight} pieces={pieces} dup-verts={dup} "
          f"euler={m.euler_number} | after STL round-trip watertight={rt.is_watertight} "
          f"broken-faces={len(trimesh.repair.broken_faces(rt))}")
integrity(front_new, 'front')
integrity(back_new, 'back')
check(abs(abs(-71.5-X_END)-45.445)<0.01, f"case length {abs(-71.5-X_END):.3f} mm (was 53.500)")

# electronics region untouched
def clip(m,x1):
    return trimesh.boolean.intersection([m, box(-BIG,x1,-BIG,BIG,-BIG,BIG)],engine=ENG)
for tag,new,don in (('front',front_new,front),('back',back_new,back_asm)):
    a,c=clip(new,-38.0), clip(don,-38.0)
    d1=trimesh.proximity.closest_point(c,a.sample(12000))[1].max()
    dv=a.volume-c.volume
    if tag=='front':
        check(abs(dv-V_CAPS)<1.0,
              f"{tag} X<=-38 differs from donor ONLY by the panel caps "
              f"(dV={dv:.2f} mm3 vs cap volume {V_CAPS:.2f} mm3)")
    else:
        check(abs(dv)<1e-3 and d1<1e-4,
              f"{tag} X<=-38 (cell bore, door rail) identical to donor "
              f"(dV={abs(dv):.6f} mm3, dev={d1:.6f} mm)")

# new screw features
for sy in (BOSS_Y,-BOSS_Y):
    zf=zcol(front_new,BOSS_X,sy); zb=zcol(back_new,BOSS_X,sy)
    check(len(zf)>=2 and abs(zf[-1]-BORE_Z[1])<1e-3, f"front insert bore blind at z={zf[-1]:.3f} (want {BORE_Z[1]})")
    check(len(zb)==2 and abs((zb[0]-zb[1])-0.22)<1e-3, f"back membrane {zb[0]-zb[1]:.3f} mm at z={zb[0]:.2f} (donor 0.22)")
    # coaxiality from the as-built solids
    def centre(m,z,r0,r1):
        s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1]); sl,T=s.to_2D()
        for e in sl.entities:
            p=sl.vertices[e.points]; c=p.mean(0); r=np.linalg.norm(p-c,axis=1)
            if r.std()<0.15 and r0<r.mean()<r1:
                w=(T@np.array([c[0],c[1],0,1]))[:3]
                if abs(w[0]-BOSS_X)<3 and abs(w[1]-sy)<3: return w,r.mean()
        return None
    cf,cb=centre(front_new,-10.0,1.5,3.0), centre(back_new,-18.0,2.5,4.0)
    if cf and cb:
        off=np.hypot(cf[0][0]-cb[0][0], cf[0][1]-cb[0][1])
        check(off<0.05, f"new screw axes coaxial at Y={sy}: {off:.4f} mm "
                        f"(bore r={cf[1]:.2f}, c'bore r={cb[1]:.2f})")
    else: check(False, f"could not fit both screw circles at Y={sy}")
    # boss wall thickness and clearance to the battery-bay end wall
    wall=BOSS_R-BORE_R
    check(wall>=1.5, f"boss wall {wall:.2f} mm around the insert bore")
    l,_,_=back_new.ray.intersects_location([[-200,sy,-10.0]],[[1,0,0]])
    xs=np.sort(l[:,0]); near=xs[(xs>-45)&(xs<-30)]
    gap=(BOSS_X-BOSS_R)-near.max() if len(near) else 99
    check(gap>0.4, f"boss clears the battery-bay end wall by {gap:.2f} mm")

# panel caps: every aperture closed, exactly PANEL_SKIN thick, light well preserved
APERTURES=[(-49.09,y,'LED') for y in (-14.0,-7.0,0.0,7.0,14.0)]+[(-51.34,26.70,'button'),(-51.34,-26.70,'button')]
check(0.30e3 < V_CAPS < 0.55e3, f"cap volume {V_CAPS:.1f} mm3 (7 apertures x ~1 mm: expect 300-550)")
for ax,ay,kind in APERTURES:
    z=zcol(front_new,ax,ay)
    good = len(z)==2 and abs(z[0]-19.0)<1e-3 and abs(z[1]-(19.0-PANEL_SKIN))<1e-3
    check(good, f"{kind} aperture ({ax},{ay}) capped: z {np.round(z,3)} "
                f"(want 19.000 -> {19.0-PANEL_SKIN:.3f}, i.e. {PANEL_SKIN} mm skin + open well behind)")
# nothing else on the outer face changed: it must now be 100% closed
xs_p=np.arange(-71.0,X_END-0.4,0.5); ys_p=np.arange(-54.5,54.6,0.5)
o=np.array([[x,y,200.] for y in ys_p for x in xs_p]); d=np.tile([0,0,-1.],(len(o),1))
_,ray,loc=front_new.ray.intersects_id(o,d,multiple_hits=False,return_locations=True)
zz=np.full(len(o),-99.); zz[ray]=loc[:,2]
nopen=int((np.abs(zz-19.0)>0.3).sum())
check(nopen==0, f"outer face now fully closed: {nopen} open cells of {len(o)}")

# thread engagement: M3x8, head on the counterbore floor
eng=(CB_Z[1]+8.0)-BORE_Z[0]
check(eng>=4.0, f"M3x8 thread engagement into the insert: {eng:.2f} mm (donor 4.50)")

# donor's OLD screw features must be entirely gone / plugged.
# The old axis (X=-25.925) is now outside the part, so probe inside the old bore's
# footprint at X=-27.0, which the end wall (X -29.055..-26.055) must have filled solid.
for sy in (BOSS_Y,-BOSS_Y):
    zf=zcol(front_new,-27.0,sy)
    check(len(zf)==2 and abs(zf[0]-19.0)<1e-3 and abs(zf[1]+19.0)<1e-3,
          f"old front bore remnant at Y={sy} filled solid by the end wall "
          f"(z {zf[0]:.2f}..{zf[1]:.2f}, want 19.00..-19.00)")
    check(len(zcol(front_new,OLD_SCREW_X,sy))==0, f"old front boss axis at Y={sy} is past the new end face")
    check(len(zcol(back_new,-27.0,sy))==0 and len(zcol(back_new,OLD_SCREW_X,sy))==0,
          f"old back counterbore at Y={sy} removed entirely with the cut")

# joint clearance, measured against the donor's own joint
def gaps(fr,bk):
    g=[]
    for y,z in [(0,-18),(0,-16),(30,-18),(-30,-18),(45,-15),(-45,-15)]:
        lf,_,_=fr.ray.intersects_location([[-200,y,z]],[[1,0,0]])
        lb,_,_=bk.ray.intersects_location([[-200,y,z]],[[1,0,0]])
        if len(lf)>=2 and len(lb): g.append(np.sort(lf[:,0])[-2]-np.sort(lb[:,0])[-1])
    return np.array(g)
dg,ng=gaps(front,back_asm), gaps(front_new,back_new)
check(dg.std()<0.005, f"donor joint measures {dg.mean():.4f} mm (n={len(dg)})")
check(np.all(np.abs(ng-dg.mean())<0.01), f"new joint matches it: {np.round(ng,4)}")

# light-tightness, with the donor-fails power assertion
def pinholes(m,xs,ys,zf,zd):
    o=np.array([[x,y,zf] for y in ys for x in xs]); d=np.tile([0,0,float(zd)],(len(o),1))
    _,ray,_=m.ray.intersects_id(o,d,multiple_hits=False,return_locations=True)
    h=np.zeros(len(o),bool); h[ray]=True; return int((~h).sum()), len(o)
xs=np.arange(-32.0,X_END-0.05,0.5); ys=np.arange(-54,54.01,1.0)
nn,t=pinholes(front_new,xs,ys,80.0,-1); no,_=pinholes(front,xs,ys,80.0,-1)
check(no>0, f"[power] donor front leaks here: {no}/{t}")
check(nn==0, f"front top face sealed: {nn}/{t}")
xs2=np.arange(-31.0,BACK_END+0.05,0.5); ys2=np.arange(-49,49.01,1.0)
nn,t=pinholes(back_new,xs2,ys2,-80.0,1); no,_=pinholes(back_asm,xs2,ys2,-80.0,1)
check(no>0, f"[power] donor back leaks here: {no}/{t}")
# the two new screw holes are legitimately open
check(nn<=int(2*np.pi*CB_R**2/0.5/1.0)+40, f"back plate sealed except the 2 screw holes: {nn}/{t}")

def through(ms,xs,zs,y0,yd,tilt):
    dv=np.array([0.,float(yd),float(tilt)]); dv/=np.linalg.norm(dv)
    o=np.array([[x,y0,z] for z in zs for x in xs]); d=np.tile(dv,(len(o),1))
    bl=np.zeros(len(o),bool)
    for m in ms:
        _,ray,_=m.ray.intersects_id(o,d,multiple_hits=False,return_locations=True); bl[ray]=True
    return ~bl
xs=np.arange(-71,X_END-0.4,0.5); zs=np.arange(-18.3,18.3,0.5)
for yd,tag in ((1,'-Y'),(-1,'+Y')):
    add=sum(int((through([front_new,back_new],xs,zs,-90.0*yd,yd,t)&
                ~through([front,back_asm],xs,zs,-90.0*yd,yd,t)).sum()) for t in (0.003,-0.003))
    check(add==0, f"{tag} face: no openings the donor did not have (NEW {add})")

rng=np.random.default_rng(11)
p=back_new.vertices[rng.choice(len(back_new.vertices),15000,replace=False)]
check(front_new.contains(p).sum()<=3, f"interference: {front_new.contains(p).sum()}/15000")

print(f"\n  front {front.volume/1000:.1f} -> {front_new.volume/1000:.1f} cm3   "
      f"back {back_asm.volume/1000:.1f} -> {back_new.volume/1000:.1f} cm3")
print(f"  assembled: {abs(-71.5-X_END):.1f} x 110.0 x 38.0 mm")
front_new.export(f'{OUT}/charger_front_short.stl')
bl=back_new.copy(); bl.apply_translation([-DX,-DY,-DZ]); bl.export(f'{OUT}/charger_back_short.stl')
front_new.export(f'{OUT}/asm_front.stl'); back_new.export(f'{OUT}/asm_back.stl')
print("\nALL CHECKS PASSED" if ok else "\n*** SOME CHECKS FAILED ***")
