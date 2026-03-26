import { loadEnv } from "./lib/load_env.cjs";

loadEnv();

if (!process.env.ELEVENLABS_API_KEY) {
  console.error("Missing ELEVENLABS_API_KEY in .env");
  process.exit(1);
}

const response = await fetch("https://api.elevenlabs.io/v1/voices", {
  headers: {
    "xi-api-key": process.env.ELEVENLABS_API_KEY,
  },
  signal: AbortSignal.timeout(15000),
});

if (!response.ok) {
  console.error(`ElevenLabs API failed: HTTP ${response.status}`);
  process.exit(1);
}

const data = await response.json();
const voices = data.voices || [];

console.log("ElevenLabs smoke check passed.");
console.log(`Voices available: ${voices.length}`);
if (voices.length > 0) {
  const sample = voices.slice(0, 5).map((voice) => voice.name).join(", ");
  console.log(`Sample voices: ${sample}`);
}
