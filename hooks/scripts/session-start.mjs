/**
 * Session start hook — placeholder for pre-flight check integration (Story 1.4).
 *
 * Cursor hooks communicate via stdio JSON. This placeholder reads stdin,
 * logs the session start event, and returns a pass-through response.
 */

import { readFileSync } from "node:fs";

const input = readFileSync(process.stdin.fd, "utf-8").trim();

let payload;
try {
  payload = JSON.parse(input);
} catch {
  payload = {};
}

const response = {
  status: "ok",
  message: "Session started — pre-flight checks will be integrated in Story 1.4",
  timestamp: new Date().toISOString(),
};

process.stdout.write(JSON.stringify(response));
