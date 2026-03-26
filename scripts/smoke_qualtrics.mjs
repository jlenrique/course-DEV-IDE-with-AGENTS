import { loadEnv } from "./lib/load_env.cjs";

loadEnv();

if (!process.env.QUALTRICS_API_TOKEN || !process.env.QUALTRICS_BASE_URL) {
  console.error("Missing QUALTRICS_API_TOKEN or QUALTRICS_BASE_URL in .env");
  process.exit(1);
}

async function getJson(url) {
  const response = await fetch(url, {
    headers: {
      "X-API-TOKEN": process.env.QUALTRICS_API_TOKEN,
    },
    signal: AbortSignal.timeout(15000),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} for ${url}`);
  }

  return response.json();
}

const whoAmI = await getJson(`${process.env.QUALTRICS_BASE_URL}/API/v3/whoami`);
const surveys = await getJson(`${process.env.QUALTRICS_BASE_URL}/API/v3/surveys?pageSize=3`);

const username = whoAmI?.result?.userName || "unknown";
const surveyList = surveys?.result?.elements || [];

console.log("Qualtrics smoke check passed.");
console.log(`Authenticated user: ${username}`);
console.log(`Retrieved ${surveyList.length} survey records from sample page.`);
if (surveyList.length > 0) {
  const sample = surveyList.map((survey) => survey.name || survey.id).join(", ");
  console.log(`Sample surveys: ${sample}`);
}
