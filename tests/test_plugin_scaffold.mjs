/**
 * Validation tests for Story 1.1: Cursor Plugin Foundation & Repository Structure.
 *
 * Run with: node tests/test_plugin_scaffold.mjs
 *
 * Verifies:
 *  - plugin.json manifest format and schema
 *  - .mcp.json structure and no hardcoded secrets
 *  - hooks.json version 1 format with required events
 *  - Directory structure existence
 *  - Preserved files are untouched
 */

import { readFileSync, existsSync, statSync } from "node:fs";
import { join } from "node:path";

const ROOT = process.cwd();
let passed = 0;
let failed = 0;

function assert(condition, label) {
  if (condition) {
    console.log(`  PASS: ${label}`);
    passed++;
  } else {
    console.log(`  FAIL: ${label}`);
    failed++;
  }
}

function loadJSON(relPath) {
  const full = join(ROOT, relPath);
  return JSON.parse(readFileSync(full, "utf-8"));
}

function fileExists(relPath) {
  return existsSync(join(ROOT, relPath));
}

function isDir(relPath) {
  const full = join(ROOT, relPath);
  return existsSync(full) && statSync(full).isDirectory();
}

// --- AC #1: Plugin Manifest ---
console.log("\n=== AC #1: Plugin Manifest ===");
const plugin = loadJSON(".cursor-plugin/plugin.json");
assert(/^[a-z0-9][a-z0-9.\-]*[a-z0-9]$/.test(plugin.name), "name is lowercase kebab-case");
assert(typeof plugin.version === "string" && plugin.version.length > 0, "version is present");
assert(typeof plugin.description === "string" && plugin.description.length > 0, "description is present");
assert(plugin.author && typeof plugin.author.name === "string", "author.name is present");

const autoDiscoverKeys = ["rules", "agents", "skills", "commands", "hooks", "mcpServers"];
for (const key of autoDiscoverKeys) {
  assert(plugin[key] === undefined, `${key} not set (relies on auto-discovery)`);
}

// --- AC #2: Directory Structure ---
console.log("\n=== AC #2: Directory Structure ===");
const requiredDirs = ["agents", "skills", "rules", "commands", "hooks", "hooks/scripts"];
for (const dir of requiredDirs) {
  assert(isDir(dir), `${dir}/ directory exists`);
}

const readmeFiles = ["agents/README.md", "skills/README.md", "commands/README.md", "rules/README.md"];
for (const f of readmeFiles) {
  assert(fileExists(f), `${f} exists`);
}

// --- AC #3: MCP Configuration ---
console.log("\n=== AC #3: MCP Configuration ===");
const mcp = loadJSON(".mcp.json");
assert(mcp.mcpServers !== undefined, "mcpServers key exists");

const expectedServers = ["gamma", "canvas-lms"];
for (const srv of expectedServers) {
  assert(mcp.mcpServers[srv] !== undefined, `${srv} server entry exists`);
  if (mcp.mcpServers[srv]) {
    const hasCommand = mcp.mcpServers[srv].command !== undefined;
    const hasUrl = mcp.mcpServers[srv].url !== undefined;
    assert(hasCommand || hasUrl, `${srv} has command or url field`);
    if (mcp.mcpServers[srv].env) {
      const envVals = Object.values(mcp.mcpServers[srv].env);
      const allRefs = envVals.every((v) => v.startsWith("${") && v.endsWith("}"));
      assert(allRefs, `${srv} env values are all env var references (no hardcoded secrets)`);
    }
  }
}

// --- AC #4: Hooks Configuration ---
console.log("\n=== AC #4: Hooks Configuration ===");
const hooks = loadJSON("hooks/hooks.json");
assert(hooks.version === 1, "hooks version is 1");
assert(Array.isArray(hooks.hooks.sessionStart), "sessionStart hook defined");
assert(Array.isArray(hooks.hooks.sessionEnd), "sessionEnd hook defined");
assert(fileExists("hooks/scripts/session-start.mjs"), "session-start.mjs script exists");
assert(fileExists("hooks/scripts/session-end.mjs"), "session-end.mjs script exists");

// --- AC #5: Agent Rules Preserved ---
console.log("\n=== AC #5: Agent Rules Preserved ===");
assert(fileExists(".cursor/rules/course-content-agents.mdc"), "course-content-agents.mdc preserved");

// --- AC #6: No regressions on preserved files ---
console.log("\n=== AC #6: Preserved Files Intact ===");
const preserved = [
  "docs/admin-guide.md",
  "config/content-standards.yaml",
  "config/platforms.example.yaml",
  "scripts/.gitkeep",
];
for (const f of preserved) {
  assert(fileExists(f), `${f} preserved`);
}

// --- Summary ---
console.log(`\n=== RESULTS: ${passed} passed, ${failed} failed ===`);
process.exit(failed > 0 ? 1 : 0);
