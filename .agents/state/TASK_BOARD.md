# Pizza Oven Project Kanban Task Board

Multi-agent state tracking for Antigravity, Cursor, Claude Code, and Codex.

---

## IN_PROGRESS
- [ ] **[TASK-006]** `STREAM-1`: Long-vault prototypes on `design/stream-1-original` *(Priority: HIGH, Assigned: cursor)*
  - Best oven is Caraxes, 38.7 kg. Shop sheet is `design/stream-1/caraxes/BUILD.md`. Inspiration re-read 2026-10-18 (five Wright lessons): module and flat skin stay; veneer, flush crane niche, side flues, and levelling screws stay out. Re-read the store file every few iterations. Do not merge to main.
- [ ] **[TASK-006]** `DESIGN`: Stream 2 modular stack, Vermax onward *(Priority: HIGH, Assigned: cursor)*
  - Branch `design/stream-2-modular`. Now on `main` as 5254441.
  - Terrax is current: 34.1 kg, brow, tunnel, and door grips on mild pads, Quicksilver pintle. Pit 11.0 kg still heaviest. The door grip pulls the door. Sheet module is 20 mm for pads, wind-back, and rivet pitch. Mouth and deck stay off it. Shop sequence is `design/stream-2/terrax/BUILD.md`. Stream 1 has used Stormcloud, Tyraxes, Vermax, Arrax, Tessarion, Sunfyre, Grey Ghost, and Seasmoke.

---

## READY
- [ ] **[TASK-004]** `DESIGN`: Adib answers the open questions on the Angas 430 *(Priority: HIGH, Assigned: unassigned)*
  - Questions are in `design/tailgate/CONCEPTS.md`.
  - Gas burner, FFD, regulator, and hose stay bought certified.
  - Do not return a wood shell without a new mass budget. The Cask-430 is about 43 kg stone-out.

---

## UNDER_REVIEW
- [ ] **[TASK-006]** `TOOLS`: Claude Opus 5.5 CAD harness *(Priority: HIGH, Assigned: cursor)*
  - Branch `tools/opus-harness`. Draft PR. Do not merge from the harness session.
  - `python3 tools/opus/test_opus.py` passes offline. `ping` needs `ANTHROPIC_API_KEY`.
  - Global cap defaults to $21. Task files are in `tools/opus/tasks/`.
- [ ] **[TASK-005]** `DESIGN`: Morning and Moondancer, the early Angas prototypes *(Priority: HIGH, Assigned: cursor)*
  - Branch `design/morning-moondancer`. Ready-for-review PR against `main`. Ported from `cursor/angas-dragon-variants-d981` with no `research/` files.
  - Morning 19.12 kg wood body. Moondancer 15.57 kg aluminium shell. Stone in. Cap was 20 kg.
  - Comparison in `design/variants/COMPARISON.md`. Interference in `design/variants/interference-report.md`.
- [ ] **[TASK-003]** `DESIGN`: Angas 430 tailgate oven *(Priority: HIGH, Assigned: cursor)*
  - Branch `design/tailgate-oven`. Draft PR against `research/argon-anatomy`.
  - Modelled envelope Ø675 × 340 mm, 31.5 kg without the stone.
  - Concepts A and C are not the build.

---

## DONE
- [x] **[TASK-002]** `RESEARCH`: Gozney Arc Lite, Tread, and Dome XL reconstruction *(Priority: HIGH, Assigned: cursor)*
  - Branch `research/argon-anatomy`. Insulation network reused by the tailgate design.
- [x] **[TASK-001]** `COORDINATION`: Multi-agent orchestration, Cursor sync, and automated review pipeline *(Priority: HIGH, Assigned: antigrav)*
- [x] **[TASK-000]** `SETUP`: Repository initialization, CERN-OHL-P v2 & CC-BY licenses, open hardware skills foundation *(Priority: HIGH, Assigned: antigrav)*

---

## BACKLOG
