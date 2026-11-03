// CI frame renderer: BridgeShort (1080x1920 portrait), dpr 0.5 buffer, scale 0.5 output (540x960, correctly framed)
// v2: GL "angle" (matches the locally proven config), concurrency 1 for heavy WebGL frames,
// and a per-frame renderStill fallback (900s page timeout) if renderFrames dies on a heavy frame.
import fs from "node:fs";
import { bundle } from "@remotion/bundler";
import { renderFrames, renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
const [outDir, a, b] = process.argv.slice(2);
const A = Number(a), B = Number(b);
fs.mkdirSync(outDir, { recursive: true });
const fileFor = (f) => path.join(outDir, `element-${String(f).padStart(3, "0")}.jpeg`);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const inputProps = { post: { dpr: 0.5 } };
const chromiumOptions = { gl: "angle" };
const composition = await selectComposition({ serveUrl, id: "BridgeShort", inputProps, chromiumOptions, timeoutInMilliseconds: 900000 });
const missing = () => { const m = []; for (let f = A; f <= B; f++) if (!fs.existsSync(fileFor(f))) m.push(f); return m; };
const t0 = Date.now(); let n = 0;
try {
  await renderFrames({ composition, serveUrl, outputDir: outDir, inputProps, imageFormat: "jpeg", jpegQuality: 88,
    timeoutInMilliseconds: 900000, concurrency: 1, frameRange: [A, B], scale: 0.5, chromiumOptions,
    onFrameUpdate: () => { n++; if (n % 25 === 0) console.log(`frames=${n} elapsed=${((Date.now() - t0) / 1000).toFixed(0)}s`); },
    onStart: () => console.log("render start") });
} catch (e) {
  console.log("renderFrames failed, falling back to per-frame stills:", e && e.message ? e.message.slice(0, 300) : e);
}
let rest = missing();
if (rest.length) {
  console.log(`fallback stills for ${rest.length} frames: ${rest[0]}..${rest[rest.length - 1]}`);
  for (const f of rest) {
    const t1 = Date.now();
    await renderStill({ composition, serveUrl, frame: f, output: fileFor(f), imageFormat: "jpeg", jpegQuality: 88,
      scale: 0.5, inputProps, chromiumOptions, timeoutInMilliseconds: 900000 });
    console.log(`still frame=${f} ${((Date.now() - t1) / 1000).toFixed(1)}s`);
  }
}
rest = missing();
if (rest.length) { console.error(`INCOMPLETE range ${A}-${B}: missing ${rest.length} frames`); process.exit(1); }
console.log(`DONE range ${A}-${B}: ${B - A + 1} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
