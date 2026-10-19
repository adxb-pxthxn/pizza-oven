# Bench spindle — start at Makerspace Adelaide

One shaft on a bench. It turns, drills, sands, and takes a light milling cut. It is not an oven, and it is not a Modulathe. Cut the bed tomorrow morning. The motor comes from the ProForm if it is in the room.

The drawing is `bench-spindle.html`. The numbers live in `model.mjs`. Hardware is CERN-OHL-P v2. This sheet is CC-BY-4.0.

Published, inferred, and design stay apart.

**Published.** Consumer Reports m204502, ProForm Pro 2000: motor 3.6 CHP, 12 mph, belt 58.5 × 20 in, incline 10.7%, capacity 300 lb, mass 264 lb, envelope 77 × 35.25 × 77 in. That is the treadmill, not this machine.

**Inferred.** Not measured on that treadmill. A DC treadmill motor of this class is taken at 4900 rpm free. John Hasler, r/Machinists 164px6a: the printed horsepower is about double what the shaft will do once the fan is slow, so 1.8 hp is the continuous figure used here. It is a class estimate. Shaft ends on these motors are odd. Many controllers give up torque at low speed. Do not treat 1.8 hp as a test.

**Design.** Two 40 × 40 × 3 mild SHS rails, 600 mm. Two UCP204 pillow blocks, 20 mm bore, catalogue centre height 33.3 mm. Bright mild shaft Ø20 × 280 mm. Pulleys Ø100 and Ø50, so the shaft ceiling is 2450 rpm. Centres 168 mm. Open belt pitch 575 mm. Sanding disc Ø120. Footprint 730 × 340 × 210 mm against an unmeasured bench taken as 1800 × 600. Measure the bench before it is bolted down.

The motor can turn mild and aluminium, and it can mill both, because the cuts below are a few tens of watts. The 40 × 40 rails and the pillow blocks are the limit.

## If the treadmill is not in the room

Cut the rails. Turn the shaft. Bolt the pillow blocks. Stop there. Do not buy a motor to match the 3.6 CHP badge.

## 1. Bed

Machines you may name: cold cut saw, the existing metal lathe, the mill, hand tools. No brake and no fibre laser at the makerspace. Do not weld mild to aluminium. No galvanised stock. No zinc-plated screws. One Torx family, plain or stainless.

1. Cold cut saw. Two 40 × 40 × 3 mild SHS, 600 mm. Deburr.
2. Two sleepers and a bridge from 6 mm mild plate. The bridge carries both pillow blocks. Bolt it. The 20 mm module is the shaft and the rail pitch where it does not fight the spindle. The nose and the pulley diameters stay off the module.
3. Guard: 1.0 mm aluminium. It lifts off. Do not bond it to the steel. Engrave 2450 only after the Ø100 and Ø50 pulleys are on the shafts. That number is the shaft ceiling, not the motor.
4. Jarrah feet under the bench plate. They are not glued to the steel.

## 2. Shaft

On the existing lathe.

1. Bright mild Ø20, 280 mm. Leave the seats at Ø20 for the two UCP204 blocks. Do not bore a housing.
2. Nose to suit the 13 mm drill chuck already in the shop.
3. Pulley: 6 mm mild, Ø100, bored to the shaft, inboard of the sanding disc.
4. Sanding disc: 6 mm mild, Ø120, outboard of that pulley, on the same shaft. Pin or bolt it. It is not a weld.
5. Motor pulley: 6 mm mild, Ø50.

Bolt the pillow blocks to the bridge. The shaft drops in. The caps close on the shaft. They do not clamp a turned shoulder.

## 3. What the shaft does on day one

The 13 mm chuck holds pins and the drill. A Ø22 jarrah grip does not belong in that chuck. Turn grips on the makerspace lathe until a larger chuck is bolted on.

| Job | Number | Where it comes from |
| --- | --- | --- |
| Turn mild Ø20 | 398 rpm, about 30 W at 0.3 mm and 0.08 mm/rev | Design, 25 m/min |
| Drill Ø8.4 | 758 rpm | Design, 20 m/min. This is the oven pintle barrel |
| Pin Ø7.2 | Turn it. The radial gap in the barrel is 0.6 mm | Same pin as the oven |
| Sand Ø120 | 924 m/min at 2450 rpm | Jarrah, aluminium, a light deburr. Not a 2×72 belt |
| Mill aluminium | 8 mm wide, 0.3 mm, 80 mm/min, about 2 W | Hand feed |
| Mill mild | 6 mm wide, 0.3 mm, 40 mm/min, about 4 W | Hand feed |

Spindle torque at the class estimate is about 5 N·m, with the belt at 95%. That is not a measured cut.

## 4. Belt, carriage, tail

1. Open belt, pitch 575 mm, at 168 mm centres. A longer belt means the motor slides back. If the belt is not cut tomorrow, the disc still sands: turn the shaft by hand, or fit the belt the day it is in the shop.
2. Carriage: a slab on the rails, an M10 rod for the cross screw, a jarrah handwheel. Wood stays at the hand. It is not bonded to the screw.
3. Tool bit for the 0.3 mm cut. Stop at 0.3 mm. A deeper cut is a different machine.
4. Tail centre faces the chuck. The drill lives in the chuck, not in the tail.

## 5. Motor

Keep the original controller, the safety key, and the motor leads. Do not lengthen them and do not sketch a mains circuit on this sheet. Someone who already wires mains checks the plug before it is used.

The motor's own fan dies when the shaft is slow. Sit a separate fan on the mount for work under about 500 rpm.

Do not run the motor at the treadmill's top speed without the 2:1 pulleys. 4900 rpm at the shaft is not this machine. 2450 is.

No gloves at the spindle.

## 6. Later, not tomorrow

Modulathe v2 is the pattern for a stiffer metal lathe: a cast bed, an MT5 spindle, linear rails, a real cross-slide. It is not a morning's work, and this bed is not that casting. Use this spindle until a cut shows the rails twisting. Then start the stiffer bed. Do not begin with bored headstock seats. The pillow blocks are the answer to that job.
