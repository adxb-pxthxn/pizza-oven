// Bench spindle. Numbers the figure, the shop sheet, and the test all share.
// 1 world unit in the figure is 2 mm. Published, inferred, and design stay apart.

export const UNIT_MM = 2;

export const donor = {
  name: "ProForm Pro 2000",
  source: "Consumer Reports m204502",
  motorChp: 3.6,
  maxMph: 12,
  beltLengthIn: 58.5,
  beltWidthIn: 20,
  inclinePct: 10.7,
  capacityLb: 300,
  massLb: 264,
  lengthIn: 77,
  widthIn: 35.25,
  heightIn: 77,
};

// Not measured on this treadmill. The 4900 rpm figure is the class of DC
// treadmill motor reported for a 2 hp unit. Hasler, r/Machinists 164px6a:
// the printed horsepower is about double what the motor is good for once
// the fan is slow. 1.8 hp is that half, not a shaft test.
export const inferred = {
  freeRpm: 4900,
  continuousHp: donor.motorChp / 2,
  note: "class estimate, not a measurement of m204502",
};

// Catalogue centre height of a UCP204 / NTN-pattern 20 mm pillow block.
export const UCP204_CENTRE_MM = 33.3;

export const design = {
  bedMm: 600,
  rail: "40×40×3 mild SHS",
  railCount: 2,
  railPitchMm: 100,
  shaftMm: 20,
  shaftLengthMm: 280,
  motorPulleyMm: 50,
  spindlePulleyMm: 100,
  pulleyCentreMm: 168,
  beltEfficiency: 0.95,
  discMm: 120,
  swingOverBedMm: 140,
  centreHeightMm: 52 + UCP204_CENTRE_MM,
  benchTargetMm: [1800, 600],
  footprintMm: [730, 340, 210],
  cutMm: 0.3,
  specificEnergy: { aluminium: 0.7, mild: 3.0, jarrah: 0.15 },
};

export const ratio = design.spindlePulleyMm / design.motorPulleyMm;

export function openBeltLengthMm(centreMm, largeDiameterMm, smallDiameterMm) {
  const large = largeDiameterMm / 2;
  const small = smallDiameterMm / 2;
  return 2 * centreMm + Math.PI * (large + small) + ((large - small) ** 2) / centreMm;
}

export const beltLengthMm = openBeltLengthMm(design.pulleyCentreMm, design.spindlePulleyMm, design.motorPulleyMm);

export const spindleMaxRpm = inferred.freeRpm * (design.motorPulleyMm / design.spindlePulleyMm);

const HP_W = 745.7;

export function torqueNm(hp, rpm) {
  return (hp * HP_W) / (rpm * (2 * Math.PI / 60));
}

export const motorTorqueNm = torqueNm(inferred.continuousHp, inferred.freeRpm);

export const spindleTorqueNm = motorTorqueNm * ratio * design.beltEfficiency;

export function rpmFor(diameterMm, surfaceMPerMin) {
  return (1000 * surfaceMPerMin) / (Math.PI * diameterMm);
}

export function discSurfaceMPerMin(rpm, diameterMm) {
  return (Math.PI * (diameterMm / 1000) * rpm);
}

// Turning power for a light cut. MRR ≈ π D doc feed n, in mm³/s.
export function turningWatts(diameterMm, docMm, feedMm, rpm, joulesPerMm3) {
  const mm3PerMin = Math.PI * diameterMm * docMm * feedMm * rpm;
  return (mm3PerMin / 60) * joulesPerMm3;
}

export function millingWatts(widthMm, docMm, feedMmPerMin, joulesPerMm3) {
  const mm3PerMin = widthMm * docMm * feedMmPerMin;
  return (mm3PerMin / 60) * joulesPerMm3;
}

export const jobs = {
  turnMild: { rpm: rpmFor(20, 25), watts: turningWatts(20, design.cutMm, 0.08, rpmFor(20, 25), design.specificEnergy.mild) },
  turnJarrah: { rpm: rpmFor(22, 200), watts: turningWatts(22, 1.0, 0.2, Math.min(spindleMaxRpm, rpmFor(22, 200)), design.specificEnergy.jarrah) },
  drill: { rpm: rpmFor(8.4, 20) },
  sand: { mPerMin: discSurfaceMPerMin(spindleMaxRpm, design.discMm) },
  millAluminium: { watts: millingWatts(8, design.cutMm, 80, design.specificEnergy.aluminium) },
  millMild: { watts: millingWatts(6, design.cutMm, 40, design.specificEnergy.mild) },
};

export const spindleWattsAtMax = inferred.continuousHp * HP_W;

export function fitsBench() {
  const [length, depth] = design.footprintMm;
  const [benchL, benchD] = design.benchTargetMm;
  return length < benchL - 400 && depth < benchD - 80;
}
