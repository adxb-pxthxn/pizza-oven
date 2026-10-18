#!/usr/bin/env python3
"""Private 1D steady-state wall model with a radiating air gap. Not in the repo."""
import math
SIGMA = 5.670374419e-8

def h_ext(t_s, t_a, eps):
    d = max(0.2, t_s - t_a)
    h_c = max(4.0, min(25.0, 1.5 * (d ** 0.33)))
    h_r = eps * SIGMA * (t_s + t_a) * (t_s * t_s + t_a * t_a)
    return h_c + h_r

def eps_eff(e1, e2):
    return 1.0 / (1.0 / e1 + 1.0 / e2 - 1.0)

def march(layers, flux, t_in, h_in):
    t = t_in - flux / h_in
    temps = [t_in, t]
    for L in layers:
        if L["kind"] == "solid":
            t = t - flux * (L["th_mm"] / 1000.0) / L["k"]
        else:
            th = L["th_mm"] / 1000.0
            t_hot = t
            ee = eps_eff(L["eps_hot"], L["eps_cold"])
            k_air = 0.034
            t_cold = max(250.0, t_hot - 40.0)
            for _ in range(60):
                hr = ee * SIGMA * (t_hot + t_cold) * (t_hot * t_hot + t_cold * t_cold)
                h = k_air / th + hr
                t_new = t_hot - flux / max(h, 1e-6)
                t_cold = 0.4 * t_cold + 0.6 * t_new
            t = t_cold
        temps.append(t)
    return temps

def solve(layers, t_in_c=500.0, t_amb_c=20.0, h_in=30.0, ext_eps=0.88):
    t_in = t_in_c + 273.15
    t_amb = t_amb_c + 273.15
    lo, hi = 20.0, 4000.0
    temps = None
    flux = None
    for _ in range(60):
        flux = 0.5 * (lo + hi)
        temps = march(layers, flux, t_in, h_in)
        t_skin = temps[-1]
        if t_skin < t_amb + 0.2:
            hi = flux
            continue
        q_ext = h_ext(t_skin, t_amb, ext_eps) * (t_skin - t_amb)
        if q_ext > flux:
            lo = flux
        else:
            hi = flux
    t_skin = temps[-1]
    return {
        "flux": flux,
        "t_skin_c": t_skin - 273.15,
        "temps_c": [x - 273.15 for x in temps],
        "h_ext": h_ext(t_skin, t_amb, ext_eps),
    }

K_SS, K_MS = 16.0, 45.0
K_FIBRE, K_WOOD = 0.10, 0.17
K_CLAY, K_PERL, K_MICRO, K_CASI = 1.0, 0.20, 0.030, 0.07

def line(label, r, idxs):
    bits = "  ".join(f"{n} {r['temps_c'][i]:.1f}" for n, i in idxs)
    print(f"{label:52s} flux {r['flux']:6.1f}  skin {r['t_skin_c']:5.1f}  | {bits}")

print("Steel shrouds, fibre k=0.10")
for t in (30, 40, 50, 60, 75, 90):
    r = solve([
        {"kind":"solid","k":K_SS,"th_mm":1.2},
        {"kind":"solid","k":K_FIBRE,"th_mm":t},
        {"kind":"solid","k":K_MS,"th_mm":1.2},
    ])
    line(f"fibre {t} mm direct to steel", r, [("fibre cold", 3)])

print("\nSteel + 12 mm foil gap (0.80/0.15) then steel")
for t in (40, 50, 60, 75):
    r = solve([
        {"kind":"solid","k":K_SS,"th_mm":1.2},
        {"kind":"solid","k":K_FIBRE,"th_mm":t},
        {"kind":"gap","th_mm":12,"eps_hot":0.80,"eps_cold":0.15},
        {"kind":"solid","k":K_MS,"th_mm":1.2},
    ])
    line(f"fibre {t} + foil gap", r, [("after fibre", 3), ("steel inner", 4)])

print("\nSame but unlined gap 0.85/0.85")
for t in (50, 75):
    r = solve([
        {"kind":"solid","k":K_SS,"th_mm":1.2},
        {"kind":"solid","k":K_FIBRE,"th_mm":t},
        {"kind":"gap","th_mm":12,"eps_hot":0.85,"eps_cold":0.85},
        {"kind":"solid","k":K_MS,"th_mm":1.2},
    ])
    line(f"fibre {t} + bare gap", r, [("after fibre", 3), ("steel inner", 4)])

print("\nSkill-comparable k=0.08, no radiation model, direct")
for t in (40, 75):
    r = solve([
        {"kind":"solid","k":18.0,"th_mm":1.2},
        {"kind":"solid","k":0.08,"th_mm":t},
        {"kind":"solid","k":45.0,"th_mm":1.2},
    ])
    line(f"k0.08 fibre {t}", r, [("fibre cold", 3)])

print("\nWOOD IN CONTACT behind fibre, 12 mm clay liner, 18 mm hardwood, k_fibre=0.10")
for t in (40, 60, 80, 100, 120, 150, 180, 220, 260):
    r = solve([
        {"kind":"solid","k":K_CLAY,"th_mm":12},
        {"kind":"solid","k":K_FIBRE,"th_mm":t},
        {"kind":"solid","k":K_WOOD,"th_mm":18},
    ])
    line(f"fibre {t}", r, [("wood inner", 3), ("wood outer", 4)])

print("\nWood contact k sensitivity, 150 mm fibre")
for k in (0.08, 0.09, 0.10, 0.12, 0.16):
    r = solve([
        {"kind":"solid","k":K_CLAY,"th_mm":12},
        {"kind":"solid","k":k,"th_mm":150},
        {"kind":"solid","k":K_WOOD,"th_mm":18},
    ])
    line(f"k={k}", r, [("wood inner", 3), ("wood outer", 4)])

print("\nWOOD after foil gap 15 mm, fibre then gap then 18 mm wood")
for t in (50, 75, 100, 125):
    r = solve([
        {"kind":"solid","k":K_SS,"th_mm":1.2},
        {"kind":"solid","k":K_FIBRE,"th_mm":t},
        {"kind":"gap","th_mm":15,"eps_hot":0.80,"eps_cold":0.15},
        {"kind":"solid","k":K_WOOD,"th_mm":18},
    ])
    line(f"fibre {t} foil", r, [("after fibre", 3), ("wood inner", 4), ("wood outer", 5)])

print("\nSummer 35 C, wood contact, find thickness for wood inner <= 60")
for t in (150, 200, 250, 300):
    r = solve([
        {"kind":"solid","k":K_CLAY,"th_mm":12},
        {"kind":"solid","k":0.10,"th_mm":t},
        {"kind":"solid","k":K_WOOD,"th_mm":18},
    ], t_amb_c=35)
    line(f"amb35 fibre {t}", r, [("wood inner", 3), ("wood outer", 4)])

print("\nPerlite 80/100/150 mm then wood")
for t in (80, 100, 150, 200):
    r = solve([
        {"kind":"solid","k":K_PERL,"th_mm":t},
        {"kind":"solid","k":K_WOOD,"th_mm":18},
    ])
    line(f"perlite {t}", r, [("wood inner", 2), ("wood outer", 3)])

print("\nMicroporous 20 and 30 mm + foil gap 10 + wood")
for t in (20, 30, 40):
    r = solve([
        {"kind":"solid","k":K_SS,"th_mm":1.2},
        {"kind":"solid","k":K_MICRO,"th_mm":t},
        {"kind":"gap","th_mm":10,"eps_hot":0.50,"eps_cold":0.15},
        {"kind":"solid","k":K_WOOD,"th_mm":18},
    ])
    line(f"micro {t}", r, [("wood inner", 4), ("wood outer", 5)])

print("\nRecommended: 304 1.2 + fibre 75 k0.10 + foil gap 12 + steel 1.2, amb 20 and 35")
base = [
    {"kind":"solid","k":K_SS,"th_mm":1.2},
    {"kind":"solid","k":0.10,"th_mm":75},
    {"kind":"gap","th_mm":12,"eps_hot":0.80,"eps_cold":0.15},
    {"kind":"solid","k":K_MS,"th_mm":1.2},
]
for amb in (20, 35):
    r = solve(base, t_amb_c=amb)
    line(f"amb {amb}", r, [("after fibre", 3), ("steel inner", 4)])

print("\nOptional wood sleeve OUTSIDE a 60 C steel shroud, 20 mm ventilated gap, eps wood 0.9, steel outer eps 0.88")
# Model: stop at steel skin known ~ calculate steel skin then a ventilated gap is not sealed.
# Approximate the sleeve as seeing radiation from a 55 C steel face across a ventilated 20 mm gap, both sides open.
# Use gap then wood with the inner boundary being the steel at the temperature from the wall solve.
r = solve(base, t_amb_c=20)
print("steel skin", round(r["t_skin_c"],1))
# Second solve is wrong if I stack wood on the oven because that adds R and heats the steel.
# A ventilated sleeve dumps heat to ambient air in the gap, so wood inner is close to a mix of air and radiation.
# Bound it: sealed sleeve (worst) vs open.
sealed = base + [
    {"kind":"gap","th_mm":20,"eps_hot":0.88,"eps_cold":0.90},
    {"kind":"solid","k":K_WOOD,"th_mm":18},
]
r = solve(sealed)
line("SEALED sleeve on 75 mm stack (worst)", r, [("steel", 4), ("wood inner", 5), ("wood outer", 6)])

print("\n== GEOMETRY AND STONE ==")
ovens = [
 ("Arc Lite", 430,481,297,325,355,150,325,85,12,12,3.4),
 ("Tread", 418,484,320,310,380,150,310,85,12,13.5,3.7),
 ("Dome XL", 946,697,997,724,543,238,470,140,30,73,10.6),
]
for n,W,D,H,iW,iD,iH,mW,mH,st,kg,kw in ovens:
    side=(W-iW)/2
    floor=iW*iD/1e6
    mass=floor*(st/1000)*2100
    e=mass*950*480/1e6
    # net at 40% draft
    net=kw*0.4
    # stone-only minutes ignoring liner and loss
    mins=e/(net*60)*1000 if net else float("inf")
    print(f"{n}: side {side:.1f} mm  mouth/apex {mH/iH:.3f}  mouth/width {mW/iW:.3f}  floor {floor:.3f} m2  stone {mass:.2f} kg  E {e:.2f} MJ  stone-only @{kw}kW*0.4 = {mins:.0f} min")

print("\nGAS CALORIFIC")
for name,g,kw in [("Arc plate",0.252,3.4),("Tread",0.2738,3.7),("XL UK",0.784,10.6),("compare XL",0.75,10.6),("Arc compare",0.2738,3.4)]:
    print(f"{name}: {g*1000:.0f} g/h -> LHV {g*46.4/3.6:.2f} kW  HHV {g*50.35/3.6:.2f} kW  plate {kw}")
print("AU XL 36.1 MJ/h", 36.1/3.6)
print("AU Dome 31.3", 31.3/3.6)
print("BTU Arc", 11687*0.000293071)
print("BTU Tread", 12500*0.000293071)

print("\nRECOMMENDED STONE 0.40*0.40*0.020*2100")
m=0.16*0.02*2100
print("mass", m, "MJ", m*950*480/1e6)
print("wood cord 2 kg/h * 16 MJ * 0.35 eff", 2*16*0.35, "kW useful")
