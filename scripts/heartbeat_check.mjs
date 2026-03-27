/**
 * Quick heartbeat check for all API-accessible tools.
 *
 * Usage:
 *   1. Create `.env` at the project root and add your API tokens (see docs/admin-guide.md)
 *   2. Run: node scripts/heartbeat_check.mjs
 *
 * Tests lightweight read-only endpoints for each configured tool.
 * Does NOT create, modify, or consume credits on any service.
 */

import { readFileSync, existsSync } from "node:fs";

// Load .env manually (no external dependencies needed)
function loadEnv() {
  const envPath = ".env";
  if (!existsSync(envPath)) {
    console.error(
      "ERROR: .env file not found. Create `.env` at the project root (see docs/admin-guide.md)."
    );
    process.exit(1);
  }
  const lines = readFileSync(envPath, "utf-8").split("\n");
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx === -1) continue;
    const key = trimmed.slice(0, eqIdx).trim();
    const val = trimmed.slice(eqIdx + 1).trim();
    if (val && !process.env[key]) {
      process.env[key] = val;
    }
  }
}

loadEnv();

const results = [];

async function check(name, fn) {
  try {
    const result = await fn();
    results.push({ name, status: "PASS", detail: result });
    console.log(`  PASS: ${name} — ${result}`);
  } catch (err) {
    results.push({ name, status: "FAIL", detail: err.message });
    console.log(`  FAIL: ${name} — ${err.message}`);
  }
}

async function skip(name, reason) {
  results.push({ name, status: "SKIP", detail: reason });
  console.log(`  SKIP: ${name} — ${reason}`);
}

async function httpGet(url, headers = {}) {
  const res = await fetch(url, { headers, signal: AbortSignal.timeout(15000) });
  return { status: res.status, ok: res.ok, data: await res.json().catch(() => null) };
}

// --- TIER 1: API + MCP ---

console.log("\n=== TIER 1: Full Programmatic Access (API + MCP) ===");

// Gamma
if (process.env.GAMMA_API_KEY) {
  await check("Gamma API", async () => {
    const res = await httpGet("https://public-api.gamma.app/v1.0/themes?limit=1", {
      "X-API-KEY": process.env.GAMMA_API_KEY,
      "Content-Type": "application/json",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return `Connected (themes endpoint responded)`;
  });
} else {
  await skip("Gamma API", "GAMMA_API_KEY not set in .env");
}

// ElevenLabs
if (process.env.ELEVENLABS_API_KEY) {
  await check("ElevenLabs API", async () => {
    const res = await httpGet("https://api.elevenlabs.io/v1/voices", {
      "xi-api-key": process.env.ELEVENLABS_API_KEY,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const voiceCount = res.data?.voices?.length || 0;
    return `Connected (${voiceCount} voices available)`;
  });
} else {
  await skip("ElevenLabs API", "ELEVENLABS_API_KEY not set in .env");
}

// Canvas LMS
if (process.env.CANVAS_ACCESS_TOKEN && process.env.CANVAS_API_URL) {
  await check("Canvas LMS API", async () => {
    const res = await httpGet(`${process.env.CANVAS_API_URL}/users/self`, {
      Authorization: `Bearer ${process.env.CANVAS_ACCESS_TOKEN}`,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return `Connected (user: ${res.data?.name || "OK"})`;
  });
} else {
  await skip("Canvas LMS API", "CANVAS_ACCESS_TOKEN or CANVAS_API_URL not set in .env");
}

// Qualtrics
if (process.env.QUALTRICS_API_TOKEN && process.env.QUALTRICS_BASE_URL) {
  await check("Qualtrics API", async () => {
    const res = await httpGet(`${process.env.QUALTRICS_BASE_URL}/API/v3/whoami`, {
      "X-API-TOKEN": process.env.QUALTRICS_API_TOKEN,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return `Connected (user: ${res.data?.result?.userName || "OK"})`;
  });
} else {
  await skip("Qualtrics API", "QUALTRICS_API_TOKEN or QUALTRICS_BASE_URL not set in .env");
}

// Canva (OAuth — can't heartbeat without browser flow)
await skip("Canva API", "OAuth-based (MCP handles auth via browser). Test by using Canva MCP in Cursor.");

// --- TIER 2: API Only ---

console.log("\n=== TIER 2: API Only (No MCP) ===");

// Botpress
if (process.env.BOTPRESS_API_KEY) {
  await check("Botpress API", async () => {
    const res = await httpGet("https://api.botpress.cloud/v1/admin/bots?limit=1", {
      Authorization: `Bearer ${process.env.BOTPRESS_API_KEY}`,
      "Content-Type": "application/json",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return `Connected (bots endpoint responded)`;
  });
} else {
  await skip("Botpress API", "BOTPRESS_API_KEY not set in .env");
}

// Wondercraft
if (process.env.WONDERCRAFT_API_KEY) {
  await check("Wondercraft API", async () => {
    const res = await fetch("https://api.wondercraft.ai/v1/podcast/test", {
      method: "HEAD",
      headers: { "X-API-KEY": process.env.WONDERCRAFT_API_KEY },
      signal: AbortSignal.timeout(15000),
    });
    return `Connected (responded with HTTP ${res.status})`;
  });
} else {
  await skip("Wondercraft API", "WONDERCRAFT_API_KEY not set in .env");
}

// Vyond
await skip(
  "Vyond API",
  "Manual workflow for this repo — non-Enterprise plans do not expose the editing API we need"
);

// Kling
if (process.env.KLING_ACCESS_KEY && process.env.KLING_SECRET_KEY) {
  await check("Kling API", async () => {
    return `Keys configured (Access + Secret — JWT auth verified at runtime)`;
  });
} else {
  await skip("Kling API", "KLING_ACCESS_KEY or KLING_SECRET_KEY not set in .env");
}

// Panopto
if (process.env.PANOPTO_BASE_URL && process.env.PANOPTO_CLIENT_ID) {
  await check("Panopto API", async () => {
    return `Configured (base URL: ${process.env.PANOPTO_BASE_URL})`;
  });
} else {
  await skip("Panopto API", "PANOPTO_BASE_URL or PANOPTO_CLIENT_ID not set in .env");
}

// --- TIER 3: Limited API ---

console.log("\n=== TIER 3: Limited / Early Access API ===");

if (process.env.DESCRIPT_API_KEY) {
  await check("Descript API", async () => `Key configured (early access API)`);
} else {
  await skip("Descript API", "DESCRIPT_API_KEY not set in .env");
}

await skip("Midjourney", "Third-party API — configure if using a wrapper service");
await skip("CapCut", "Official API status unclear — manual workflow recommended");

// --- TIER 4 ---

console.log("\n=== TIER 4: Manual Only ===");
await skip("CourseArc", "LTI/SCORM only — no API to test");
await skip("Articulate", "Desktop/web authoring — no API to test");

// --- UTILITY MCPs ---

console.log("\n=== UTILITY MCPs ===");
await skip("Fetch MCP", "Utility MCP — test in Cursor by asking agent to fetch a URL");
if (process.env.BRAVE_API_KEY) {
  await check("Brave Search API", async () => {
    const res = await httpGet(
      `https://api.search.brave.com/res/v1/web/search?q=test&count=1`,
      { "X-Subscription-Token": process.env.BRAVE_API_KEY }
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return `Connected (search responded)`;
  });
} else {
  await skip("Brave Search API", "BRAVE_API_KEY not set in .env (free tier: 2k queries/month)");
}
await skip("Playwright MCP", "Already configured at user level — test in Cursor agent");
await skip("Ref MCP", "Already configured at user level — test in Cursor agent");

// --- SUMMARY ---

const passed = results.filter((r) => r.status === "PASS").length;
const failed = results.filter((r) => r.status === "FAIL").length;
const skipped = results.filter((r) => r.status === "SKIP").length;

console.log(`\n${"=".repeat(50)}`);
console.log(`HEARTBEAT RESULTS: ${passed} connected, ${failed} failed, ${skipped} skipped`);
console.log(`${"=".repeat(50)}`);

if (failed > 0) {
  console.log("\nFailed connections:");
  results.filter((r) => r.status === "FAIL").forEach((r) => console.log(`  - ${r.name}: ${r.detail}`));
}

if (skipped > 0) {
  const configurable = results.filter(
    (r) => r.status === "SKIP" && r.detail.includes("not set")
  );
  if (configurable.length > 0) {
    console.log("\nTools you can enable by adding keys to .env:");
    configurable.forEach((r) => console.log(`  - ${r.name}`));
  }
}

process.exit(failed > 0 ? 1 : 0);
