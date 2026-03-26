const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");

function loadDotEnv(dotEnvPath) {
  if (!fs.existsSync(dotEnvPath)) {
    return {};
  }

  const env = {};
  const lines = fs.readFileSync(dotEnvPath, "utf8").split(/\r?\n/);
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx === -1) {
      continue;
    }
    const key = trimmed.slice(0, eqIdx).trim();
    const value = trimmed.slice(eqIdx + 1).trim();
    env[key] = value;
  }
  return env;
}

const serverName = process.argv[2];
if (!serverName) {
  console.error("Missing MCP server name argument.");
  process.exit(1);
}

const repoRoot = path.resolve(__dirname, "..");
const dotEnv = loadDotEnv(path.join(repoRoot, ".env"));

const serverConfigs = {
  gamma: {
    command: "npx",
    args: ["-y", "@raydeck/gamma-app-mcp"],
    requiredEnv: ["GAMMA_API_KEY"],
    envMap: {
      GAMMA_API_KEY: "GAMMA_API_KEY",
    },
  },
  "canvas-lms": {
    command: "npx",
    args: ["-y", "canvas-mcp-server"],
    requiredEnv: ["CANVAS_ACCESS_TOKEN", "CANVAS_DOMAIN"],
    envMap: {
      CANVAS_API_TOKEN: "CANVAS_ACCESS_TOKEN",
      CANVAS_DOMAIN: "CANVAS_DOMAIN",
    },
  },
  notion: {
    command: "npx",
    args: ["-y", "@notionhq/notion-mcp-server"],
    requiredEnv: ["NOTION_API_KEY"],
    envMap: {
      NOTION_TOKEN: "NOTION_API_KEY",
    },
  },
};

const config = serverConfigs[serverName];
if (!config) {
  console.error(`Unknown MCP server: ${serverName}`);
  process.exit(1);
}

const missing = config.requiredEnv.filter((key) => !dotEnv[key]);
if (missing.length > 0) {
  console.error(
    `Missing required environment variables for ${serverName}: ${missing.join(", ")}`
  );
  process.exit(1);
}

const childEnv = { ...process.env };
for (const [targetKey, sourceKey] of Object.entries(config.envMap)) {
  childEnv[targetKey] = dotEnv[sourceKey];
}

const child = spawn(config.command, config.args, {
  cwd: repoRoot,
  env: childEnv,
  stdio: "inherit",
  shell: process.platform === "win32",
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 0);
});
