const fs = require("node:fs");
const path = require("node:path");

function loadEnv(repoRoot = path.resolve(__dirname, "..", "..")) {
  const envPath = path.join(repoRoot, ".env");
  if (!fs.existsSync(envPath)) {
    throw new Error(
      "Missing .env file. Create `.env` at the project root and add your keys " +
        "(see docs/admin-guide.md — API Keys and Credentials)."
    );
  }

  const lines = fs.readFileSync(envPath, "utf8").split(/\r?\n/);
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
    if (value && !process.env[key]) {
      process.env[key] = value;
    }
  }

  return envPath;
}

module.exports = { loadEnv };
