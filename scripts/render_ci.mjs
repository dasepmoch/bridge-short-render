// CI frame renderer: BridgeShort (1080x1920 portrait), dpr 0.5 buffer, scale 0.5 output (540x960, correctly framed)
import fs from "node:fs";
import { bundle } from "@remotion/bundler";
import { renderFrames, selectComposition } from "@remotion/renderer";
import path from "node:path";
const [outDir, a, b] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const composition = await selectComposition({ serveUrl, id: "BridgeShort", inputProps: { post: { dpr: 0.5 } } });
const t0 = Date.now(); let n = 0;
await renderFrames({ composition, serveUrl, outputDir: outDir, inputProps: { post: { dpr: 0.5 } }, imageFormat: "jpeg", jpegQuality: 88,
  timeoutInMilliseconds: 600000, concurrency: 2, frameRange: [Number(a), Number(b)], scale: 0.5,
  onFrameUpdate: () => { n++; if (n % 25 === 0) console.log(`frames=${n} elapsed=${((Date.now()-t0)/1000).toFixed(0)}s`); },
  onStart: () => console.log("render start") });
console.log(`DONE range ${a}-${b}: ${n} frames`);
