// gta6-clipper-01 — entry program (Node 22, standard library only).
//
// The entry is the video itself: this program only hands the house the
// video's address. It reads VIDEO.json from the repository root, checks it
// is a JSON object naming a YouTube address, and writes the same bytes to
// the output directory, where the gate reads them. It takes no input, makes
// no network calls, and writes the same bytes on every run.
//
// Run locally the way the grader does:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const FILE_NAME = "VIDEO.json";

const sourcePath = join(BOT_DIR, FILE_NAME);
let raw: string;
try {
  raw = readFileSync(sourcePath, "utf8");
} catch (err) {
  console.error(`Could not read ${sourcePath}: ${(err as Error).message}`);
  process.exit(1);
}

let parsed: unknown;
try {
  parsed = JSON.parse(raw);
} catch (err) {
  console.error(`${FILE_NAME} is not valid JSON: ${(err as Error).message}`);
  process.exit(1);
}

if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
  console.error(`${FILE_NAME} must be a JSON object with a "url" field.`);
  process.exit(1);
}

const url = (parsed as Record<string, unknown>).url;
if (typeof url !== "string" || url.length === 0) {
  console.error(`${FILE_NAME} must name the video in a "url" string.`);
  process.exit(1);
}

mkdirSync(OUTPUT_DIR, { recursive: true });
writeFileSync(join(OUTPUT_DIR, FILE_NAME), raw);
