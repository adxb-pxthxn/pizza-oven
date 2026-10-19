import assert from "node:assert/strict";
import * as m from "./model.mjs";

assert.equal(m.UNIT_MM, 2);
assert.equal(m.donor.motorChp, 3.6);
assert.equal(m.donor.source, "Consumer Reports m204502");
assert.equal(m.inferred.continuousHp, 1.8);
assert.equal(m.ratio, 2);
assert.equal(m.spindleMaxRpm, 2450);
assert.ok(m.beltLengthMm > 560 && m.beltLengthMm < 590, m.beltLengthMm);

assert.ok(m.motorTorqueNm > 2.4 && m.motorTorqueNm < 2.8, m.motorTorqueNm);
assert.ok(m.spindleTorqueNm > 4.5 && m.spindleTorqueNm < 5.4, m.spindleTorqueNm);

assert.ok(m.jobs.turnMild.rpm > 380 && m.jobs.turnMild.rpm < 420);
assert.ok(m.jobs.turnMild.watts < 80, m.jobs.turnMild.watts);
assert.ok(m.jobs.drill.rpm > 700 && m.jobs.drill.rpm < 820);
assert.ok(m.jobs.drill.rpm < m.spindleMaxRpm);
assert.ok(m.jobs.sand.mPerMin > 800 && m.jobs.sand.mPerMin < 1100);
assert.ok(m.jobs.millAluminium.watts < 20);
assert.ok(m.jobs.millMild.watts < 20);
assert.ok(m.jobs.millMild.watts < m.spindleWattsAtMax);
assert.ok(m.fitsBench());

const [length, depth, height] = m.design.footprintMm;
assert.ok(length < m.design.benchTargetMm[0]);
assert.ok(depth < m.design.benchTargetMm[1]);
assert.ok(height < 400);

console.log(JSON.stringify({
  spindleMaxRpm: m.spindleMaxRpm,
  motorTorqueNm: Number(m.motorTorqueNm.toFixed(2)),
  spindleTorqueNm: Number(m.spindleTorqueNm.toFixed(2)),
  turnMildRpm: Number(m.jobs.turnMild.rpm.toFixed(1)),
  turnMildW: Number(m.jobs.turnMild.watts.toFixed(1)),
  drillRpm: Number(m.jobs.drill.rpm.toFixed(1)),
  sandMPerMin: Number(m.jobs.sand.mPerMin.toFixed(0)),
  millMildW: Number(m.jobs.millMild.watts.toFixed(1)),
  millAlW: Number(m.jobs.millAluminium.watts.toFixed(1)),
  beltLengthMm: Number(m.beltLengthMm.toFixed(1)),
}, null, 2));
