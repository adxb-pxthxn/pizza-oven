import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "../../../../.agents/skills/anatomy/kit/iso-kit.mjs";
import { kitScript } from "../../../../.agents/skills/anatomy/scripts/inline-kit.mjs";

// Reconstructed Dome XL, 1 unit = 4 mm. Published ratios, inferred body.
// The moving part is the door: shut, the gas burner is not allowed to run.

const HERE = dirname(fileURLToPath(import.meta.url));
const theme = process.argv.includes("--light") ? "light" : "dark";
const U = 0.22;

const EXT_W = 946 * U;
const EXT_D = 697 * U;
const BODY_H = 520 * U;
const INST_H = 997 * U;
const INT_W = 724 * U;
const INT_D = 543 * U;
const INT_H = 238 * U;
const MOUTH_W = 470 * U;
const MOUTH_H = 140 * U;
const HEARTH = 187 * U;
const STONE = 30 * U;
const FRONT = 64 * U;
const SIDE = (EXT_W - INT_W) / 2;

const PLATE = { x: -EXT_W / 2 - 28, y: -36, w: EXT_W + 70, d: EXT_D + 78, r: 6 };
const WIDTH = 760;
const HEIGHT = 520;

const P = k.fitProjection(
  [
    ...k.boxCorners(PLATE, -18, 0),
    [-EXT_W / 2, 0, INST_H],
    [EXT_W / 2, EXT_D, BODY_H],
    [0, -20, HEARTH + MOUTH_H],
  ],
  WIDTH,
  HEIGHT,
  { pad: 28, azimuth: 38, elevation: 28 },
);

const at = (point) => k.iso(point, P);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (points, style) => k.dotsSvg(points, style);

function feet() {
  const out = [`<path class="iso-halo" d="${k.haloOf(PLATE, -16, 10, P)}"/>`];
  for (const [x, y] of k.corners(PLATE, 16)) {
    out.push(S(k.cylinder(x, y, 7, -16, 3, P, 20), { tone: "lo" }));
    out.push(S(k.cylinder(x, y, 5, -13, 13, P, 20), { tone: "mid" }));
  }
  out.push(S(k.slabOf(PLATE, -8, 8, P, 6, 1.2), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(PLATE, 6), 0, P), { tone: "lo" }));
  const screws = k.corners(PLATE, 12);
  out.push(L(screws.map(([x, y]) => k.ring(x, y, 2.2, 0, P, 14)).join(""), { tone: "lo" }));
  out.push(D(screws.map(([x, y]) => at([x, y, 0])), { size: 0.45 }));
  const strip = { x: PLATE.x + 18, y: PLATE.y + PLATE.d - 14, w: PLATE.w - 36, d: 6, r: 1 };
  out.push(S(k.slabOf(strip, 0, 0.6, P, 3), { tone: "lo", crease: "none" }));
  const ticks = k.topTicks(strip.x + 4, strip.x + strip.w - 4, 8, 5, strip.y + 0.8, 0.6, [1.6, 3.2], P);
  out.push(L(ticks.minor, { tone: "lo" }), L(ticks.major, { tone: "mid" }));
  const label = { x: PLATE.x + 14, y: PLATE.y + 12, w: 42, d: 16, r: 1 };
  out.push(S(k.slabOf(label, 0, 0.8, P, 3), { tone: "lo", crease: "none" }));
  out.push(L(k.planOutline(k.insetPlan(label, 2), 0.8, P), { tone: "lo" }));
  out.push(L(k.lineOnTop([label.x + 4, label.y + 5], [label.x + label.w - 4, label.y + 5], 0.8, P), { tone: "mid" }));
  out.push(L(k.lineOnTop([label.x + 4, label.y + 9], [label.x + label.w - 10, label.y + 9], 0.8, P), { tone: "lo" }));
  return out.join("");
}

function archSegments(x0, width, y0, depth, z0, rise, tone, steps = 5) {
  const out = [];
  const seg = depth / steps;
  for (let i = 0; i < steps; i += 1) {
    const t = (i + 0.5) / steps;
    const crown = Math.sin(Math.PI * t) * rise;
    const h = 8 + crown;
    out.push(S(k.slabOf({ x: x0, y: y0 + i * seg, w: width, d: seg + 0.4, r: 1 }, z0, h, P, 2, 0.4), { tone }));
  }
  return out.join("");
}

function body(doorShift) {
  const out = [];
  const skirt = { x: -EXT_W / 2, y: 0, w: EXT_W, d: EXT_D, r: 4 };
  out.push(S(k.slabOf(skirt, 0, HEARTH - STONE - 6, P, 4, 0.8), { tone: "lo" }));
  out.push(L(k.sideSeam(k.insetPlan(skirt, 3), (HEARTH - STONE) * 0.45, P), { tone: "faint" }));
  // Under-stone board, visible as a pale band.
  out.push(S(k.slabOf({ x: -INT_W / 2 + 2, y: FRONT, w: INT_W - 4, d: INT_D, r: 1 }, HEARTH - STONE - 5, 5, P, 2), { tone: "mid" }));
  out.push(S(k.slabOf({ x: -INT_W / 2 + 4, y: FRONT + 2, w: INT_W - 8, d: INT_D - 4, r: 1 }, HEARTH - STONE, STONE, P, 2), { tone: "hi" }));
  // Three blankets on the right cheek, the published layer count.
  const blanketT = 25 * U;
  for (let layer = 0; layer < 3; layer += 1) {
    const inset = SIDE - (layer + 1) * blanketT;
    out.push(S(k.slabOf({
      x: INT_W / 2 - inset,
      y: FRONT + 4,
      w: blanketT - 0.6,
      d: INT_D - 8,
      r: 0.4,
    }, HEARTH, INT_H * 0.72, P, 2), { tone: layer === 1 ? "mid" : "lo" }));
  }
  // Liner, full width, low.
  out.push(archSegments(-INT_W / 2, INT_W, FRONT, INT_D, HEARTH, INT_H - 10, "hi", 6));
  // Outer skin only on the left, so the blankets stay visible.
  out.push(archSegments(-EXT_W / 2, EXT_W * 0.46, 2, EXT_D - 4, HEARTH, INT_H + 8, "mid", 6));
  // Lintel: the weir. Mouth is 140 / 238 of the apex.
  out.push(S(k.slabOf({ x: -MOUTH_W / 2, y: 1, w: MOUTH_W, d: 5, r: 0.6 }, HEARTH + MOUTH_H, 7, P, 2, 0.4), { tone: "hi" }));
  out.push(S(k.slabOf({ x: -MOUTH_W / 2 - 6, y: 0, w: 6, d: 6, r: 0.4 }, HEARTH, MOUTH_H, P, 2), { tone: "mid" }));
  out.push(S(k.slabOf({ x: MOUTH_W / 2, y: 0, w: 6, d: 6, r: 0.4 }, HEARTH, MOUTH_H, P, 2), { tone: "mid" }));
  // Landing.
  out.push(S(k.slabOf({ x: -MOUTH_W / 2, y: -8, w: MOUTH_W, d: 10, r: 1 }, HEARTH - 4, 4, P, 2, 0.3), { tone: "mid" }));
  // Burner, the lit part, on the left wall.
  out.push(S(k.slabOf({ x: -INT_W / 2 + 4, y: FRONT + 16, w: 7, d: INT_D * 0.62, r: 2 }, HEARTH + 10, 6, P, 3, 0.3), { tone: "mid", lit: true }));
  out.push(S(k.cylinder(-INT_W / 2 + 8, FRONT + 14, 4, HEARTH + 4, 8, P, 16), { tone: "mid" }));
  out.push(D([at([-INT_W / 2 + 8, FRONT + 14, HEARTH + 12])], { size: 0.7 }));
  // Valve and knurled dial on the dock, outside the hot box.
  const dock = { x: -EXT_W / 2 - 16, y: EXT_D * 0.35, w: 16, d: 28, r: 2 };
  out.push(S(k.slabOf(dock, 8, 22, P, 3, 0.6), { tone: "lo" }));
  out.push(L(k.knurl(dock.x + 8, dock.y + 8, 5, 30, 36, 10, P), { tone: "mid" }));
  out.push(S(k.cylinder(dock.x + 8, dock.y + 8, 5, 30, 6, P, 16), { tone: "hi" }));
  for (let i = 0; i < 3; i += 1) {
    out.push(L(k.lineOnTop([dock.x + 3, dock.y + 16 + i * 3], [dock.x + 13, dock.y + 16 + i * 3], 30, P), { tone: "faint" }));
  }
  // Flue, inferred rise from the 520 mm body to the published 997 mm.
  out.push(S(k.cylinder(0, FRONT + 18, 12, BODY_H - 4, INST_H - BODY_H, P, 24), { tone: "mid" }));
  out.push(S(k.cylinder(0, FRONT + 18, 14, BODY_H - 2, 3, P, 24), { tone: "lo" }));
  out.push(S(k.cylinder(0, FRONT + 18, 15, INST_H - 3, 2, P, 24), { tone: "hi" }));
  out.push(L(k.ring(0, FRONT + 18, 13, INST_H - 6, P, 24), { tone: "lo" }));
  // Grate on the right, where the manual puts the wood.
  for (let i = 0; i < 4; i += 1) {
    out.push(S(k.slabOf({ x: INT_W / 2 - 28, y: FRONT + 20 + i * 10, w: 22, d: 2.2, r: 0.4 }, HEARTH + 2, 2, P, 2), { tone: "lo" }));
  }
  // Door, in front of the mouth. doorShift 0 is clear of the opening; 1 covers it.
  const doorZ = HEARTH + (1 - doorShift) * (MOUTH_H + 16);
  out.push(S(k.slabOf({ x: -MOUTH_W / 2 - 2, y: -16, w: MOUTH_W + 4, d: 4, r: 1 }, doorZ, MOUTH_H + 4, P, 2, 0.4), { tone: "mid" }));
  out.push(S(k.cylinder(0, -14, 2.2, doorZ + MOUTH_H * 0.45, 5, P, 12), { tone: "hi" }));
  return out.join("");
}

const svg = k.figureSvg({
  width: WIDTH,
  height: HEIGHT,
  label: "dome-xl",
  body: `<g id="static">${feet()}</g><g id="oven"></g>`,
});

const openArt = body(0);
const shutArt = body(1);

const script = `
const oven = document.getElementById("oven");
const readout = document.querySelector("[data-readout]");
const stage = document.querySelector(".iso-stage");
const still = window.matchMedia("(prefers-reduced-motion: reduce)");
const openArt = ${JSON.stringify(openArt)};
const shutArt = ${JSON.stringify(shutArt)};
let door = 0;
let target = 0;
let frame = 0;
let last = 0;
let visible = true;
const draw = () => {
  oven.innerHTML = door < 0.5 ? openArt : shutArt;
  const shut = door >= 0.5;
  if (readout) readout.textContent = shut ? "door shut · gas off" : "door clear · gas may run";
  stage.setAttribute("aria-valuenow", shut ? "1" : "0");
};
const tick = (now) => {
  const dt = last ? Math.min((now - last) / 1000, 0.05) : 0.016;
  last = now;
  const next = still.matches ? target : door + (target - door) * (1 - Math.exp(-dt / 0.18));
  const prev = door < 0.5;
  door = Math.abs(target - next) < 0.01 ? target : next;
  if ((door < 0.5) !== prev || door === target) draw();
  frame = visible && door !== target ? requestAnimationFrame(tick) : 0;
};
const run = () => { if (!frame && visible) { last = 0; frame = requestAnimationFrame(tick); } };
new IntersectionObserver((entries) => {
  visible = entries[entries.length - 1].isIntersecting;
  if (visible) run();
}).observe(stage);
stage.addEventListener("pointermove", (event) => {
  const box = stage.getBoundingClientRect();
  target = (event.clientX - box.left) / box.width > 0.55 ? 1 : 0;
  run();
});
stage.addEventListener("keydown", (event) => {
  if (event.key !== "ArrowRight" && event.key !== "ArrowLeft" && event.key !== "Enter" && event.key !== " ") return;
  event.preventDefault();
  target = target > 0.5 ? 0 : 1;
  run();
});
draw();
`;

const pageBody = k.plateHtml({
  fig: "Fig 1",
  title: "Dome XL cutaway",
  hint: "Hover the right half to shut the door",
  readout: "door clear · gas may run",
  keys: [
    { mark: "lit", label: "Lateral burner. Gas stays off while the door covers the mouth" },
    { mark: "hi", label: "304 liner and the lintel. Mouth height is 140 / 238 of the apex" },
    { mark: "lo", label: "Three insulation blankets on the open cheek, and the skirt" },
  ],
  caption:
    "Reconstructed Dome XL. The mouth is narrower than the chamber, so the right cheek can hold a wood grate and the left cheek a gas burner. Three blanket layers show in the cutaway. The flue is the inferred rise from a 520 mm body to the published 997 mm installed height. The 219 mm drawing callout is not used as the hearth. Shutting the door is the manual's rule: the door goes on only after the flame is out.",
  body: `<div class="iso-stage" tabindex="0" role="slider" aria-label="Dome XL door" aria-valuemin="0" aria-valuemax="1" aria-valuenow="0">${svg}</div>`,
});

const html = k.pageHtml({
  title: "Dome XL cutaway",
  theme,
  body: pageBody,
  script: kitScript() + script,
  width: 780,
});

const name = theme === "light" ? "dome-xl-light.html" : "dome-xl.html";
writeFileSync(join(HERE, name), html);
console.log("wrote", name);
