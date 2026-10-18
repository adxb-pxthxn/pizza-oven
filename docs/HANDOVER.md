# Agent Handover Protocol & Session Status

**Active Agent:** cursor
**Timestamp:** 2026-10-18T18:15:00Z
**Current Branch / Commit:** design/stream-1-original
**Overall Status:** IN_PROGRESS

---

## 1. Executive Summary (10-Second Briefing)
Stream 1 is the long barrel after Morning and Moondancer. Best current oven is the Vermax body: 37.3 kg, 240 mm broil bay, pizza floor 301°C, open cool-down 0.66× the Tread. Bread is Sunfyre's gas, 230°C, floor 211°C, on the Tessarion solid. Do not merge to main.

## 2. Completed in This Session
- [x] Shop stack and heat model in `cad/freecad/stream_physics.py`.
- [x] Stormcloud solid, interference gate, four views.
- [x] Tyraxes solid. Door xmax −337.8 mm, skin xmin −334.8 mm. Ferrule press fits only.
- [x] Arrax solid. Sill ymax −86.8 mm, steel ymin 40 mm, side gap 10 mm. 43 solids.
- [x] Vermax solid. Plate ymin 280 mm, broil bay 240 mm, 48 solids, ferrules only.
- [x] Tessarion solid. Door starts 3 mm above the deck. Sill top is 1 mm below it. Bread pose.

## 3. Immediate Next Steps (For Incoming Agent)
1. The family is Stormcloud through Tessarion. A further dragon needs a new measured fault.
2. Keep wood off the arch. The sky plate stays removable.
3. Argon answers text. Do not pull a sandbox over `/workspace`.

## 4. Guiding Invariants
- Fuel is gas. Floor is normalised mild steel, free, no cordierite, no zinc.
- Skin aim 55°C, hard touch limit 60°C. Underside 60°C. Grip 40°C.
- Commit format: `feat(stream): subject [agent:cursor]`.

## 5. Active Locks & Touched Files
- **Active Locks:** None.
- **Key paths:** `cad/freecad/stream_physics.py`, `design/stream-1/`.
