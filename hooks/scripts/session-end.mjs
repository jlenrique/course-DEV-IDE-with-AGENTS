/**
 * Session end hook — placeholder for run reporting integration (Epic 4).
 *
 * Cursor hooks communicate via stdio JSON. This placeholder reads stdin,
 * logs the session end event, and returns a pass-through response.
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
  message: "Session ended — run reporting will be integrated in Epic 4",
  timestamp: new Date().toISOString(),
};

process.stdout.write(JSON.stringify(response));
