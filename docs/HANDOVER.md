# Agent Handover Protocol & Session Status

**Active Agent:** cursor
**Timestamp:** 2026-10-18T22:55:00Z
**Current Branch / Commit:** design/stream-1-original
**Overall Status:** IN_PROGRESS

---

## 1. Executive Summary (10-Second Briefing)
Best oven is Caraxes: Vermithor's door and skin, with a finger hollow in the grip. 38.7 kg, pizza floor 305°C, cool-down 42 min, 0.67× the Tread. Shop sheet is `design/stream-1/caraxes/BUILD.md`. Design inputs, including `inspiration.md`, are read from `/cursor/stores/store-97fe1fa0-fd19-44b4-ac7d-36d872774744/`. Do not merge to main.

## 2. Completed in This Session
- [x] Shop stack and heat model in `cad/freecad/stream_physics.py`.
- [x] Stormcloud solid, interference gate, four views.
- [x] Tyraxes solid. Door xmax −337.8 mm, skin xmin −334.8 mm. Ferrule press fits only.
- [x] Arrax solid. Sill ymax −86.8 mm, steel ymin 40 mm, side gap 10 mm. 43 solids.
- [x] Vermax solid. Plate ymin 280 mm, broil bay 240 mm, 48 solids, ferrules only.
- [x] Tessarion solid. Door starts 3 mm above the deck. Sill top is 1 mm below it. Bread pose.

## 3. Immediate Next Steps (For Incoming Agent)
1. Caraxes is the oven to build. A further dragon needs a new measured fault, and a stable one gets its own `BUILD.md`.
2. Re-read `inspiration.md` in the store folder at the start of each iteration. Frank Lloyd Wright is first. On 2026-10-19 it is still the 20 mm grid, board-and-batten, and the swing crane, plus Teenage Engineering flat-pack. Battens and a kickstand stay out.
3. Keep wood off the arch. The sky plate stays removable. Argon answers text. Do not pull a sandbox over `/workspace`.

## 4. Guiding Invariants
- Fuel is gas. Floor is normalised mild steel, free, no cordierite, no zinc.
- Skin aim 55°C, hard touch limit 60°C. Underside 60°C. Grip 40°C.
- Commit format: `feat(stream): subject [agent:cursor]`.

## 5. Active Locks & Touched Files
- **Active Locks:** None.
- **Key paths:** `cad/freecad/stream_physics.py`, `design/stream-1/`.
