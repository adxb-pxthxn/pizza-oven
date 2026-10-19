import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "../../../.agents/skills/anatomy/kit/iso-kit.mjs";
import * as G from "../../../.agents/skills/anatomy/kit/lathe.mjs";
import * as A from "../../../.agents/skills/anatomy/kit/audit.mjs";
import { kitScript } from "../../../.agents/skills/anatomy/scripts/inline-kit.mjs";
import * as model from "./model.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const theme = process.argv.includes("--light") ? "light" : "dark";
const u = (mm) => mm / model.UNIT_MM;

const WIDTH = 760;
const HEIGHT = 460;
const PLATE = { x: u(-80), y: u(-230), w: u(900), d: u(460), r: u(10) };
const PLATE_Z = u(-18);
const PLATE_H = u(18);
const FOOT = u(16);
const RAIL_X = u(40);
const RAIL_L = u(640);
const RAIL_T = u(40);
const RAIL_Z = u(12);
const RAIL_TOP = RAIL_Z + RAIL_T;
const FAR = { x: RAIL_X, y: u(-70), w: RAIL_L, d: RAIL_T, r: u(1.5) };
const NEAR = { x: RAIL_X, y: u(30), w: RAIL_L, d: RAIL_T, r: u(1.5) };
const BRIDGE_H = u(12);
const AXIS_Y = 0;
const AXIS_Z = RAIL_TOP + BRIDGE_H + u(model.UCP204_CENTRE_MM);
const SHAFT_R = u(model.design.shaftMm / 2);
const SPINDLE_X = u(8);
const SP = G.frameAlong([SPINDLE_X, AXIS_Y, AXIS_Z], [1, 0, 0]);

const DISC = [-u(36), -u(18)];
const PULLEY = [u(10), u(26)];
const SHAFT = [u(26), u(200)];
const NOSE = [u(200), u(224)];
const CHUCK = [u(224), u(258)];

const PULLEY_CX = SPINDLE_X + (PULLEY[0] + PULLEY[1]) / 2;
const MOTOR_P_W = u(16);
const MOTOR_X = PULLEY_CX - MOTOR_P_W / 2;
const MOTOR_Y = u(-model.design.pulleyCentreMm);
const MOTOR_R = u(44);
const MO = G.frameAlong([MOTOR_X, MOTOR_Y, AXIS_Z], [1, 0, 0]);
const BODY = [-u(110), 0];
const FLY = [-u(124), -u(110)];

const P = k.fitProjection(
  [
    ...k.boxCorners(PLATE, PLATE_Z - FOOT, 0),
    [SPINDLE_X, AXIS_Y, AXIS_Z + u(64)],
    [MOTOR_X + FLY[0], MOTOR_Y - MOTOR_R - u(10), AXIS_Z + u(56)],
    [RAIL_X + RAIL_L + u(20), u(130), RAIL_TOP + u(80)],
  ],
  WIDTH,
  HEIGHT,
  { pad: 30, azimuth: 38, elevation: 28 },
);

const at = (point) => k.iso(point, P);
const S = (paths, style) => k.solidSvg(paths, style);
const Ln = (d, style) => (d ? k.lineSvg(d, style) : "");
const Dots = (points, style) => k.dotsSvg(points, style);
const R = A.recorder(P);
const hidden = [];

function tag(svg, part) {
  return part ? svg.replace("<g ", `<g data-part="${part}" `) : svg;
}

function put(name, svg, shapes, atPoint) {
  R.put({ name, at: atPoint, svg, shapes: shapes.map((shape) => R.solid(shape)) });
}

function box(name, plan, z, h, tone, opt = {}) {
  const paths = k.slabOf(plan, z, h, P, opt.steps ?? 4, opt.bevel ?? 0.4);
  const svg = tag(S(paths, { tone, crease: opt.crease ?? "faint", lit: Boolean(opt.lit) }), opt.part);
  const drawn = (opt.extra ?? "") + svg;
  const shape = A.slab(plan, z, h, { name, ground: Boolean(opt.ground) });
  if (opt.hide) {
    hidden.push(`<g data-part="${opt.part || name}" style="display:none">${drawn}</g>`);
    return;
  }
  put(name, drawn, [shape], [plan.x + plan.w / 2, plan.y + plan.d / 2, z + h / 2]);
}

function round(name, F, meridian, tone, opt = {}) {
  const paths = G.lathe(meridian, F, P, { steps: opt.steps ?? 36, rims: "ends" });
  const svg = tag(S(paths, { tone, crease: opt.crease ?? "lo", lit: Boolean(opt.lit) }), opt.part);
  const s = (meridian[0][0] + meridian[meridian.length - 1][0]) / 2;
  const drawn = (opt.extra ?? "") + svg;
  const shape = A.solid(F, meridian, { name });
  if (opt.hide) {
    hidden.push(`<g data-part="${opt.part || name}" style="display:none">${drawn}</g>`);
    return;
  }
  put(name, drawn, [shape], G.pointOf(F, s, 0, 0));
}

function screws(plan, z, inset) {
  return Dots(k.corners(plan, inset).map(([x, y]) => at([x, y, z])), { size: 0.42 });
}

function splitBlock(name, x, footZ, footTop, radius) {
  const gap = 0.4;
  const inner = radius + gap;
  const cheekD = u(14);
  const reach = inner + cheekD;
  const capZ = AXIS_Z + radius + 0.1;
  const foot = { x: x - u(26), y: -reach, w: u(52), d: reach * 2, r: u(1.5) };
  box(`${name}.foot`, foot, footZ, footTop - footZ, "mid", { bevel: 0.3, extra: screws(foot, footTop, u(6)) });
  for (const side of [-1, 1]) {
    const cheek = {
      x: x - u(14),
      y: side > 0 ? inner : -inner - cheekD,
      w: u(28),
      d: cheekD,
      r: u(1),
    };
    box(`${name}.cheek.${side}`, cheek, footTop, capZ - footTop, "mid", { bevel: 0.2, crease: "none" });
  }
  const cap = { x: x - u(16), y: -reach, w: u(32), d: reach * 2, r: u(1.2) };
  box(`${name}.cap`, cap, capZ, u(8), "mid", { bevel: 0.25 });
  return capZ + u(8);
}

const bench = () => {
  const groove = Ln(k.planOutline(k.insetPlan(PLATE, u(8)), 0, P, 6), { tone: "lo" });
  box("stand.bench", PLATE, PLATE_Z, PLATE_H, "mid", { steps: 6, bevel: 1.05, ground: true, extra: groove });
  for (const [x, y] of k.corners(PLATE, u(32))) {
    box(`foot.${x}.${y}`, { x: x - u(12), y: y - u(12), w: u(24), d: u(24), r: u(2) }, PLATE_Z - FOOT, FOOT - u(6), "lo", { steps: 3 });
    box(`pad.${x}.${y}`, { x: x - u(8), y: y - u(8), w: u(16), d: u(16), r: u(2) }, PLATE_Z - u(6), u(6), "hi", { steps: 3, bevel: 0.2 });
  }
  const strip = { x: u(30), y: PLATE.y + PLATE.d - u(24), w: u(520), d: u(8), r: u(1) };
  const ticks = k.topTicks(strip.x + u(8), strip.x + strip.w - u(8), u(20), 5, strip.y + u(0.6), u(1.2), [u(2), u(4)], P);
  const ends = Dots([
    at([strip.x + u(2), strip.y + strip.d / 2, u(1.2)]),
    at([strip.x + strip.w - u(2), strip.y + strip.d / 2, u(1.2)]),
  ], { size: 0.4 });
  box("ruler", strip, 0, u(1.2), "lo", {
    steps: 2,
    bevel: 0,
    crease: "none",
    extra: Ln(ticks.minor, { tone: "lo" }) + Ln(ticks.major, { tone: "mid" }) + ends,
  });
  const label = { x: u(640), y: PLATE.y + u(18), w: u(78), d: u(32), r: u(1.5) };
  const rules = [u(20), u(32), u(46)].map((len, index) => Ln(k.lineOnTop(
    [label.x + u(6), label.y + u(8) + index * u(7)],
    [label.x + u(6) + len, label.y + u(8) + index * u(7)],
    u(1.5),
    P,
  ), { tone: "lo", free: true }));
  box("label", label, 0, u(1.5), "lo", { steps: 3, bevel: 0.2, extra: rules.join("") + screws(label, u(1.5), u(4)) });
};

const bed = () => {
  for (const [name, x] of [["sleeper.head", u(36)], ["sleeper.tail", u(630)]]) {
    box(name, { x, y: u(-96), w: u(28), d: u(192), r: u(1.5) }, 0, RAIL_Z, "mid", { bevel: 0.35 });
  }
  const farSeam = Ln(k.sideSeam(FAR, RAIL_Z + RAIL_T / 2, P, 4), { tone: "faint" });
  const nearSeam = Ln(k.sideSeam(NEAR, RAIL_Z + RAIL_T / 2, P, 4), { tone: "faint" });
  box("rail.far", FAR, RAIL_Z, RAIL_T, "mid", { bevel: 0.45, extra: farSeam });
  box("rail.near", NEAR, RAIL_Z, RAIL_T, "mid", { bevel: 0.45, extra: nearSeam + screws(NEAR, RAIL_TOP, u(16)) });
  const bridge = { x: u(70), y: u(-90), w: u(160), d: u(180), r: u(2) };
  box("bridge", bridge, RAIL_TOP, BRIDGE_H, "mid", { bevel: 0.5, extra: screws(bridge, RAIL_TOP + BRIDGE_H, u(10)) });
  const mark = { x: bridge.x + u(50), y: bridge.y + u(10), w: u(62), d: u(16), r: u(1) };
  box("guard.plate", mark, RAIL_TOP + BRIDGE_H, u(1.6), "hi", {
    steps: 2,
    bevel: 0.15,
    extra: k.faceTextSvg(
      k.topMatrix([mark.x + u(6), mark.y + u(4)], RAIL_TOP + BRIDGE_H + u(1.6), P, "x"),
      "2450",
      { size: 3.2, tone: "mid" },
    ),
  });
};

const spindle = () => {
  const footTop = AXIS_Z - SHAFT_R - 0.1;
  splitBlock("pillow.a", u(78), RAIL_TOP + BRIDGE_H, footTop, SHAFT_R);
  splitBlock("pillow.b", u(150), RAIL_TOP + BRIDGE_H, footTop, SHAFT_R);
  round("disc", SP, [[DISC[0], u(8)], [DISC[0] + u(1.5), u(60)], [DISC[1] - u(1.5), u(60)], [DISC[1], u(8)]], "hi", { steps: 48, part: "disc" });
  round("neck", SP, [[DISC[1], SHAFT_R], [PULLEY[0], SHAFT_R]], "hi", { steps: 20, crease: "none" });
  round("pulley", SP, [[PULLEY[0], u(12)], [PULLEY[0] + u(2), u(50)], [PULLEY[1] - u(2), u(50)], [PULLEY[1], u(12)]], "mid", { steps: 48 });
  round("shaft", SP, [[SHAFT[0], SHAFT_R], [SHAFT[1], SHAFT_R]], "hi", { steps: 28, crease: "none" });
  round("nose", SP, [[NOSE[0], u(8)], [NOSE[1], u(8)]], "hi", { steps: 24, crease: "none" });
  round("chuck", SP, [
    [CHUCK[0], u(14)],
    [CHUCK[0] + u(4), u(26)],
    [CHUCK[1] - u(8), u(26)],
    [CHUCK[1], u(18)],
  ], "mid", { steps: 40 });
  const key = { x: SPINDLE_X + CHUCK[0] + u(8), y: u(-4), w: u(8), d: u(8), r: u(1) };
  box("chuck.key", key, AXIS_Z + u(26), u(8), "mid", { steps: 2, bevel: 0.15 });
};

const motor = () => {
  const mountTop = AXIS_Z - MOTOR_R - 0.1;
  const mount = { x: MOTOR_X + BODY[0], y: MOTOR_Y - MOTOR_R - u(8), w: -BODY[0] + u(8), d: MOTOR_R * 2 + u(16), r: u(2) };
  box("motor.mount", mount, 0, mountTop, "mid", { bevel: 0.4, extra: screws(mount, mountTop, u(8)) });
  round("flywheel", MO, [[FLY[0], u(18)], [FLY[0] + u(3), u(52)], [FLY[1], u(20)]], "lo", { steps: 48 });
  const finMarks = [u(28), u(62), u(96)].map((s) => Ln(
    G.lathe([[BODY[0] + s, MOTOR_R], [BODY[0] + s + u(1.2), MOTOR_R]], MO, P, { steps: 24, rims: "none" }).outline,
    { tone: "faint" },
  )).join("");
  round("motor.body", MO, [
    [BODY[0], u(20)],
    [BODY[0] + u(8), MOTOR_R],
    [BODY[1] - u(6), MOTOR_R],
    [BODY[1], u(16)],
  ], "mid", { steps: 40, extra: finMarks });
  round("motor.pulley", MO, [[0, u(10)], [u(2), u(25)], [MOTOR_P_W - u(2), u(25)], [MOTOR_P_W, u(10)]], "mid", { steps: 36 });
  const fan = { x: mount.x + mount.w, y: MOTOR_Y - u(14), w: u(10), d: u(28), r: u(1) };
  box("fan", fan, mountTop - u(24), u(24), "lo", { bevel: 0.2 });
};

function belt() {
  const c1 = [PULLEY_CX, AXIS_Y, AXIS_Z];
  const c2 = [MOTOR_X + MOTOR_P_W / 2, MOTOR_Y, AXIS_Z];
  const r1 = u(model.design.spindlePulleyMm / 2);
  const r2 = u(model.design.motorPulleyMm / 2);
  const dy = c2[1] - c1[1];
  const dz = c2[2] - c1[2];
  const dist = Math.hypot(dy, dz);
  const gamma = Math.atan2(dz, dy);
  const beta = Math.acos(Math.max(-1, Math.min(1, (r1 - r2) / dist)));
  const halfN = 0.32;
  const kiss = halfN + 0.05;
  const along = (radius) => Math.sqrt(kiss * (2 * radius + kiss));
  [[0, 1], [1, -1]].forEach(([index, sign]) => {
    const angle = gamma + sign * beta;
    const n = [0, Math.cos(angle), Math.sin(angle)];
    const a = [c1[0], c1[1] + r1 * n[1], c1[2] + r1 * n[2]];
    const b = [c2[0], c2[1] + r2 * n[1], c2[2] + r2 * n[2]];
    const delta = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
    const len = Math.hypot(...delta) || 1;
    const axis = delta.map((v) => v / len);
    const a2 = a.map((v, i) => v + axis[i] * along(r1));
    const b2 = b.map((v, i) => v - axis[i] * along(r2));
    const span = [b2[0] - a2[0], b2[1] - a2[1], b2[2] - a2[2]];
    const spanLen = Math.hypot(...span) || 1;
    const run = span.map((v) => v / spanLen);
    const side = [1, 0, 0];
    const up = G.unit3(G.cross3(run, side));
    const mid = [(a2[0] + b2[0]) / 2, (a2[1] + b2[1]) / 2, (a2[2] + b2[2]) / 2];
    const draw = Ln(k.segment(a, b, P), { tone: "mid" }) + Dots([at(a), at(b)], { size: 0.55, tone: "hi" });
    put(`belt.${index}`, draw, [
      A.orientedBox(mid, [run, side, up], [spanLen / 2, 0.4, halfN], { name: `belt.${index}` }),
    ], mid);
  });
}

const carriageX = u(300);
const carriage = () => {
  const slab = { x: carriageX, y: u(-78), w: u(86), d: u(150), r: u(2) };
  const slide = { x: carriageX + u(16), y: u(6), w: u(54), d: u(48), r: u(1.5) };
  const post = { x: carriageX + u(30), y: u(18), w: u(22), d: u(24), r: u(1) };
const postZ = RAIL_TOP + u(22);
const postH = AXIS_Z - u(3) - postZ;
  const bitY = u(11) + 1.2;
const bit = { x: carriageX + u(36), y: bitY, w: u(7), d: u(22) - bitY, r: u(0.4) };
  const wheelX = carriageX + u(42);
  const wheelY = slab.y + slab.d + u(22);
  const wheelR = u(16);
  const neck = { x: wheelX - u(4), y: slab.y + slab.d, w: u(8), d: wheelY - wheelR - (slab.y + slab.d), r: u(1) };
  const wheelZ = RAIL_TOP + u(6);
  const parts = [
    S(k.slabOf(slab, RAIL_TOP, u(12), P, 4, 0.45), { tone: "mid" }),
    screws(slab, RAIL_TOP + u(12), u(8)),
    S(k.slabOf(slide, RAIL_TOP + u(12), u(10), P, 3, 0.35), { tone: "mid" }),
    S(k.slabOf(post, postZ, postH, P, 3, 0.3), { tone: "hi" }),
    S(k.slabOf(neck, wheelZ + u(2), u(6), P, 2, 0.2), { tone: "mid", crease: "none" }),
    S(k.cylinder(wheelX, wheelY, wheelR, wheelZ, u(12), P, 32, 0.4), { tone: "hi", crease: "lo" }),
    Ln(k.knurl(wheelX, wheelY, wheelR, wheelZ, wheelZ + u(12), 26, P), { tone: "lo" }),
    Ln(k.lineOnTop([wheelX - u(3), wheelY], [wheelX + wheelR - u(2), wheelY], wheelZ + u(12.2), P), { tone: "hi" }),
  ];
  put(
    "carriage",
    `<g data-part="carriage">${parts.join("")}</g>`,
    [
      A.slab(slab, RAIL_TOP, u(12), { name: "carriage.slab" }),
      A.slab(slide, RAIL_TOP + u(12), u(10), { name: "carriage.slide" }),
      A.slab(post, postZ, postH, { name: "carriage.post" }),
      A.slab(neck, wheelZ + u(2), u(6), { name: "carriage.neck" }),
      A.cylinder(wheelX, wheelY, wheelR, wheelZ, u(12), { name: "carriage.wheel" }),
    ],
    [slab.x + slab.w / 2, 0, RAIL_TOP + u(8)],
  );
  box("bit", bit, AXIS_Z - u(3), u(6), "hi", { steps: 2, bevel: 0.15, part: "bit" });
};

const tail = () => {
  const origin = u(620);
  const TF = G.frameAlong([origin, AXIS_Y, AXIS_Z], [-1, 0, 0]);
  const qR = u(7);
  const footTop = AXIS_Z - qR - 0.1;
  const capTop = splitBlock("tail", origin - u(30), RAIL_TOP + u(14), footTop, qR);
  const block = { x: origin - u(78), y: u(-86), w: u(86), d: u(172), r: u(2) };
  box("tail.block", block, RAIL_TOP, u(14), "mid", { bevel: 0.4, extra: screws(block, RAIL_TOP + u(14), u(8)) });
  round("quill", TF, [[0, qR], [u(34), qR]], "hi", { steps: 24, crease: "none", part: "quill" });
  round("centre", TF, [[u(34), u(6)], [u(50), u(0.8)]], "hi", { steps: 20, part: "centre" });
  const lockX = origin - u(30);
  const lockY = u(8);
  put(
    "tail.lock",
    S(k.cylinder(lockX, lockY, u(6), capTop, u(9), P, 20, 0.25), { tone: "mid" })
      + Ln(k.knurl(lockX, lockY, u(6), capTop, capTop + u(9), 14, P), { tone: "lo" }),
    [A.cylinder(lockX, lockY, u(6), capTop, u(9), { name: "tail.lock" })],
    [lockX, lockY, capTop + u(4)],
  );
  round("drill", TF, [[u(34), u(4)], [u(78), u(0.7)]], "hi", { steps: 16, hide: true, part: "drill" });
};

const work = () => {
  const start = SPINDLE_X + CHUCK[1];
  const BF = G.frameAlong([start, AXIS_Y, AXIS_Z], [1, 0, 0]);
  round("blank", BF, [[0, u(11)], [u(150), u(11)]], "hi", { lit: true, steps: 32, part: "blank" });
  const cutter = G.frameAlong([start, AXIS_Y, AXIS_Z], [1, 0, 0]);
  round("cutter", cutter, [[0, u(4)], [u(28), u(4)]], "hi", { steps: 16, hide: true, part: "cutter" });
  const plate = { x: carriageX + u(18), y: u(-8), w: u(50), d: u(10), r: u(0.8) };
  box("mill.plate", plate, RAIL_TOP + u(22), u(4), "hi", { hide: true, part: "plate", steps: 2 });
};

const controls = () => {
  const plan = { x: u(250), y: u(-214), w: u(108), d: u(46), r: u(3) };
  box("controller", plan, 0, u(32), "mid", { steps: 4, bevel: 0.55, extra: screws(plan, u(32), u(6)) });
  const knobX = u(286);
  const knobY = u(-191);
  put(
    "controller.knob",
    S(k.cylinder(knobX, knobY, u(9), u(32), u(11), P, 28, 0.3), { tone: "hi" })
      + Ln(k.knurl(knobX, knobY, u(9), u(32), u(43), 18, P), { tone: "lo" })
      + Ln(k.lineOnTop([knobX, knobY], [knobX + u(7), knobY], u(43.2), P), { tone: "hi" }),
    [A.cylinder(knobX, knobY, u(9), u(32), u(11), { name: "controller.knob" })],
    [knobX, knobY, u(38)],
  );
  box("controller.key", { x: u(318), y: u(-206), w: u(22), d: u(10), r: u(1) }, u(32), u(4), "hi", { steps: 2, bevel: 0.15, part: "key" });
};

const sander = () => {
  const arm = { x: SPINDLE_X, y: u(78), w: u(14), d: u(40), r: u(1.5) };
  const armZ = AXIS_Z - u(6);
  box("arm", arm, armZ, u(12), "mid", { bevel: 0.25 });
  box("arm.post", { x: arm.x + u(2), y: arm.y + u(8), w: u(10), d: u(12), r: u(1) }, 0, armZ, "mid", { bevel: 0.2, crease: "none" });
  const idlerR = u(16);
const idlerY = arm.y + arm.d + idlerR;
  const IF = G.frameAlong([SPINDLE_X + u(7), idlerY, AXIS_Z], [1, 0, 0]);
  round("idler", IF, [[0, u(5)], [u(3), u(16)], [u(12), u(16)], [u(15), u(5)]], "hi", { steps: 28 });
};

bench();
bed();
spindle();
motor();
belt();
carriage();
tail();
work();
controls();
sander();

A.settle(R, P);
R.items.sort((a, b) => a.key - b.key);
if (process.argv.includes("--audit")) A.auditOrExit(R, P, {});

const halo = `<path class="iso-halo" d="${k.haloOf(PLATE, PLATE_Z - FOOT, PLATE_H, P)}"/>`;
const svg = k.figureSvg({
  width: WIDTH,
  height: HEIGHT,
  label: "A bench spindle. A treadmill motor turns one shaft that can turn, drill, sand, or take a light milling cut.",
  body: halo + R.items.map((item) => item.svg).join("") + hidden.join(""),
});

const live = `
const P = ${JSON.stringify(P)};
const modes = ["turn", "drill", "sand", "mill"];
const say = {
  turn: "turn · ${model.jobs.turnMild.rpm.toFixed(0)} rpm · mild Ø20",
  drill: "drill · Ø8.4 · ${model.jobs.drill.rpm.toFixed(0)} rpm",
  sand: "sand · ${model.jobs.sand.mPerMin.toFixed(0)} m/min on the disc",
  mill: "mill · 0.3 mm · mild and aluminium",
};
const shift = { turn: 0, drill: 16, sand: -8, mill: 22 };
const watch = { turn: "blank", drill: "drill", sand: "disc", mill: "cutter" };
const stage = document.querySelector(".iso-stage");
const readout = document.querySelector("[data-readout]");
const carriage = stage.querySelector('[data-part="carriage"]');
const show = { drill: ["drill"], mill: ["cutter", "plate"] };
let mode = 0;
let frame = 0;
let last = 0;
let clock = 0;
let visible = false;
let idle = 0;
const still = matchMedia("(prefers-reduced-motion: reduce)");
let touring = !still.matches;
function apply(index) {
  mode = (index + modes.length) % modes.length;
  const name = modes[mode];
  const blank = stage.querySelector('[data-part="blank"]');
  const centre = stage.querySelector('[data-part="centre"]');
  const bit = stage.querySelector('[data-part="bit"]');
  if (blank) blank.style.display = name === "turn" ? "" : "none";
  if (centre) centre.style.display = name === "drill" ? "none" : "";
  if (bit) bit.style.display = name === "mill" ? "none" : "";
  for (const part of ["drill", "cutter", "plate"]) {
    const el = stage.querySelector('[data-part="' + part + '"]');
    if (!el) continue;
    el.style.display = (show[name] || []).includes(part) ? "" : "none";
  }
  stage.querySelectorAll("[data-part]").forEach((el) => el.removeAttribute("data-lit"));
  stage.querySelector('[data-part="' + watch[name] + '"]')?.setAttribute("data-lit", "");
  if (carriage) carriage.setAttribute("transform", translateAlong(P, [shift[name], 0, 0]));
  if (readout.textContent !== say[name]) readout.textContent = say[name];
  stage.setAttribute("aria-valuenow", String(mode));
  stage.setAttribute("aria-valuetext", say[name]);
}
function tick(now) {
  const dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
  last = now;
  if (touring && !still.matches) {
    clock += dt;
    const next = Math.floor(clock / 2.6) % modes.length;
    if (next !== mode) apply(next);
  }
  frame = visible && touring ? requestAnimationFrame(tick) : 0;
}
const run = () => { if (!frame && visible) { last = 0; frame = requestAnimationFrame(tick); } };
function steer(index) {
  touring = false;
  apply(index);
  clearTimeout(idle);
  idle = setTimeout(() => { touring = !still.matches; clock = mode * 2.6; run(); }, 3600);
}
new IntersectionObserver((entries) => {
  visible = entries[entries.length - 1].isIntersecting;
  if (visible) run();
}, { rootMargin: "120px 0px" }).observe(stage);
stage.addEventListener("pointerdown", () => steer(mode + 1));
stage.addEventListener("keydown", (event) => {
  if (event.key === "ArrowRight" || event.key === "ArrowUp") { event.preventDefault(); steer(mode + 1); }
  if (event.key === "ArrowLeft" || event.key === "ArrowDown") { event.preventDefault(); steer(mode - 1); }
  if (event.key === "Home") { event.preventDefault(); steer(0); }
  if (event.key === "End") { event.preventDefault(); steer(modes.length - 1); }
  const n = Number(event.key);
  if (n >= 1 && n <= 4) { event.preventDefault(); steer(n - 1); }
});
apply(0);
if (!still.matches) run();
`;

const body = k.plateHtml({
  fig: "Fig 1",
  title: "Bench spindle",
  hint: "Click or press 1–4",
  readout: `turn · ${model.jobs.turnMild.rpm.toFixed(0)} rpm · mild Ø20`,
  keys: [
    { mark: "lit", label: "Whatever the shaft is doing: blank, drill, disc, or cutter" },
    { mark: "raised", label: "Jarrah at the handwheel, the feet, and the safety key" },
  ],
  caption:
    `Started on the bench, not cast. Two 600 mm rails, two pillow blocks, one shaft. The ProForm motor is geared 2:1, so a 4900 rpm class motor is 2450 at the shaft. The open belt is about ${model.beltLengthMm.toFixed(0)} mm at ${model.design.pulleyCentreMm} mm centres. Turn, drill, sand on the outboard disc, or take a 0.3 mm mill cut. The rails are the limit, not the motor. Footprint 730 by 340 mm.`,
  body: `<div class="iso-stage" tabindex="0" role="slider" aria-label="Bench spindle. Keys 1 to 4 choose turn, drill, sand, or mill." aria-valuemin="0" aria-valuemax="3" aria-valuenow="0">${svg}</div>`,
});

const file = theme === "light" ? "bench-spindle-light.html" : "bench-spindle.html";
writeFileSync(join(HERE, file), k.pageHtml({
  title: "Bench spindle",
  theme,
  body,
  script: kitScript() + live,
  width: 820,
}));
console.log("wrote", file, "parts", R.items.length);
