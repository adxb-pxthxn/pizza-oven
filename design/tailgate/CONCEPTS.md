# Tailgate oven concepts

Adib's oven is personal first. It cooks a 15 inch pizza, it is round, it rides in a BYD Shark 6, and the gas train is bought certified. The look he asked for is a turned wood body with metal accents. Argon was also asked for the oven it would build if the wood look were not a goal. Both are here, plus a hybrid that tries to keep the wood and the cool skin. The oven that is modelled is the Angas 430.

Four Argon passes, `gemini-4-argon`, thinking level HIGH:

1. `design/tailgate/argon/01-wood.md` — Cooper's Dome, Cask-430.
2. `design/tailgate/argon/01-optimal.md` — Angas 430, unconstrained.
3. `design/tailgate/argon/01-third.md` — Angas Binnacle, the hybrid.
4. `design/tailgate/argon/02-critique.md` — the lock. It also withdraws the claim that the stone comes out through the mouth.

The first concept round had socket timeouts. The files above are the completed passes.

## The three pictures

| | Cask-430 | Angas 430 | Angas Binnacle |
|---|---|---|---|
| Picture | `design/tailgate/concepts/cask-430.png` | `design/tailgate/concepts/angas-430.png` | `design/tailgate/concepts/angas-binnacle.png` |
| What it is | 24 dry-coopered blackwood staves, stainless crown | Double-skin 304, brass cinch, jarrah handles | Cool stainless cupola standing in a blackwood ring |
| Trade-off in one line | The heirloom look, and a two-person lift | The oven that fits one person and the tub | Pays for a steel vessel and a wood vessel, and is the heaviest |

The Cask and the Binnacle pictures are massing studies. The Angas 430 picture, the lifted crown, and the cutaway are shaded from the manufacturing solids.

## Side by side

Masses for A and C are Argon's hand totals. The Angas 430 column is the build123d model, table feet on, tripod tubes off. Argon's own hand total for that oven was 27.7 kg stone-out at Ø625. The model is heavier because the wall was thickened to match the crown, so the skin is one surface. Costs are ESTIMATE, AUD, Adelaide, October 2026, bottle excluded. Heat-up times are Argon's estimates, not a closed energy balance.

| | A. Cask-430, the wood body | B. Angas 430, Argon-optimal, modelled | C. Angas Binnacle, the hybrid |
|---|---|---|---|
| Plan | Ø765 belly | Ø675 shell, 1165 over the handles | Ø768 wood ring |
| Stowed height | about 420–455 mm | 340 mm body, 405 mm on the 65 mm feet | 410 mm |
| Weight, stone out | 42.6 kg | **31.5 kg** | 45.1 kg |
| Weight, ready | 52.6 kg with tripod | **37.6 kg** on the table feet | 54.1 kg |
| Shark tub | Handles and belly crowd a 1224 mm gap between the arches | Handles on, 1165 mm, inside 1224. Body plus feet 405 mm, inside the 517 mm tub depth | Ø768 still fits the width and punishes the lift |
| Sits on the lowered tailgate | No. The tailgate is 517 mm deep | No. Ø675 does not sit on 517 mm, and a flame there has no 300 mm clearance to the ute | No |
| Heat-up | 24–28 min at 6.8 kW | 22–25 min at 5.8 kW, Argon's estimate | 26–30 min at 6.5 kW on a Ø450 stone |
| Durability | Fair. Dry staves move with the season. Hoops need tightening after a corrugated road | The shell is stainless. Two dowels and the band bolt hold the crown. The stone can ride in a bag | The steel is fine. The wood ring and the air gap collect grit, and the oven is 45 kg of that grit shaking |
| Safety | Wood inner face 69°C, under 80°C. Outer wood about 45°C. Certified gas | Wall skin 53°C, crown skin 55°C. Handles are the touch surfaces. Certified gas. No wood in the stack | Wood inner face 78.5°C if the gap chokes. That is 1.5°C of margin |
| Premium feel | The thing he described: blackwood, brass hoops, a steel crown | Brushed stainless, a brass equator, jarrah in the hands. The wood is where you touch it | A binnacle. Beautiful, and it is two ovens |
| Build, Makerspace Adelaide | Hardest. Compound-bevel staves on the table saw and thicknesser. No published lathe swings a 600 mm drum. Crown is university TIG | Sheet rolls and TIG at the university shop. Makerspace: table saw and thicknesser for jarrah blanks and calcium-silicate bevels, WorkBee for MDF bucks and board trimming, metal lathe for ferrules and handles, lasers for templates only | Both of the others |
| AUD, estimate | 980–1,120 | **530–845** | 920–1,150 |

## Recommendation

Build the Angas 430.

The wood body is the look, and it is the wrong object to carry out of a ute. It stays under 80°C, and it is still a 43 kg, Ø765, two-person oven. The binnacle does not rescue it. A steel shell plus a wood ring is heavier than the wood shell alone, and the wood is one choked vent away from the char limit.

The hybrid that survives is already in the Angas 430. Jarrah where a hand closes. Brass where the eye looks for the joint. Stainless everywhere the heat is. A wood costume glued over the hot shell is the thing this design refuses to be.

## What the critique changed, and what it did not

Adopted:

- Mouth 420 × 95 mm. A 381 mm pizza has 19.5 mm per side. Argon priced the extra opening at about 280 W, roughly 5% of a 5.8 kW burner.
- Apex 165 mm above the stone, mouth/apex 0.576.
- Floor stays Ø430 × 20. Radial clearance is 24.5 mm. A Ø450 floor was declined.
- Crown insulation 100 mm of AES, skin 54.5°C. The wall was brought to the same total, 75 mm AES plus 25 mm calcium silicate, so the outer skin is one surface. Wall skin 52.8°C. That is why the plan is Ø675 and not Argon's Ø625.
- A 420 × 45 mm stainless peel landing in front of the sill.
- The stone does not pass the mouth. Argon checked it again: a Ø430 × 20 disk needs about 112 mm of opening height to tilt through a 420 mm mouth, and the mouth is 95 mm.

Kept against the critique's parting-line sketch:

- The skirt is 120 mm, taller than the mouth, so the cinch is a complete ring above the arch. Lifting the crown does not split the lintel. Argon's locked sketch put the parting line on the lintel.
- The road lock in the model is two Ø5 dowels through the band plus the band bolt. The critique's six V-channel clips and a night pin are the same idea, drawn as hardware Adib can file. They are not separate solids.

## Modelled envelope

From `cad/tailgate/spec.py` and `design/tailgate/models/manifest.json`.

- Shell Ø674.8 mm, body 340.1 mm, handle span 1164.8 mm.
- Floor Ø430 × 20 cordierite, shifted 8 mm so a crescent remains for the burner.
- Chamber Ø470. Mouth 420 × 95. Apex 165. Ratio 0.576.
- Wall: 1.2 liner, 75 AES, 25 calcium silicate, 1.2 skin. Crown: 1.2 liner, 100 AES, 1.2 skin.
- Brass band 35 × 3. Jarrah handles Ø32 × 220 on 35 mm stands. Stub feet 65 mm. Tripod tubes Ø25.4 × 1.6 × 750, in the tripod export.
- Mass, table configuration: 31.5 kg stone out, 37.6 kg ready, stone 6.1 kg. Steel is the heavy part. The 1.5 mm base pan alone is 4.2 kg.
- One person lifts it without the stone. With the stone in, slide it or take a second person.

Drawings: `design/tailgate/drawings/ga-arrangement.svg`, `ga-section.svg`, `ga-exploded.svg`, `ga-stowed.svg`. Shaded views: `design/tailgate/concepts/angas-430.png`, `angas-430-exploded.png`, `angas-430-cutaway.png`. Solids: `design/tailgate/models/`, STEP AP214 and STL.

## Open questions for Adib

Each one changes a dimension or a purchase.

1. Which certified burner is in hand before the deck slot is cut? A 5.5–6.5 kW bought assembly with its own injector, thermocouple, and flame-failure valve. No jet is drawn.
2. One-piece stone, crown off to remove it, or two D-halves that can leave through the mouth and leave a seam in the deck?
3. Can the university shop slip-roll and TIG 1.2 mm 304? Makerspace Adelaide does not publish a roll, a brake, or a metal-capable laser. That assumption is the crown.
4. Gas only. A wood fire was dropped in all three concepts. Confirm it stays dropped.
5. Usual stand: the camp table and the 65 mm feet, or the 750 mm tripod as well?
6. Handles: jarrah, or blackwood or red gum already in the shed?
7. A Ø52 dial thermometer in a brass boss, or an unbroken crown and an infrared gun on the stone?
8. Tie-down: four stainless eyes on the base, or a cradle that uses the Shark's existing points?
9. The carry: 31.5 kg without the stone is a one-person lift for a short distance. If that is too much, the next kilograms to give back are the mouth frame and a thinner base pan, not a return to a wood shell.
