# Diagnostic Procedures

Step-by-step troubleshooting for pre-flight check failures, organized by failure type.

## Authentication Failures (401/403)

**Symptoms**: `FAIL: HTTP 401` or `HTTP 403` in heartbeat output.

1. Verify the API key is set in `.env` (not `.env.example`)
2. Confirm the key has not expired or been rotated
3. Check the key has sufficient permissions/scopes for the endpoint being tested
4. For Canvas: verify token is scoped to the correct institution URL
5. For Qualtrics: verify data center ID matches the base URL

**Tool-specific**:
- **Gamma**: Regenerate key at Settings > API Keys. Requires Pro+ plan.
- **ElevenLabs**: Check quota at elevenlabs.io dashboard. Free tier: 10k credits/month.
- **Canvas**: Token generated at `{institution}/profile/settings`. Check for expiry.
- **Qualtrics**: Token from Account Settings > Qualtrics IDs. Verify data center.

## Connection Failures

**Symptoms**: `FAIL: Connection error` or `FAIL: timeout`.

1. Check internet connectivity
2. Verify the base URL is correct (no typos, correct protocol)
3. Check if the service is experiencing an outage (check status pages)
4. For institutional services (Canvas, Panopto): check VPN requirements

## Rate Limit Errors (429)

**Symptoms**: `FAIL: HTTP 429` in heartbeat.

1. Wait and retry — pre-flight uses read-only endpoints with minimal impact
2. Check if another process is consuming API quota
3. Gamma: 50 generations/hour limit (heartbeat uses themes endpoint, should not trigger)
4. Canva: 20 requests/minute per user

## MCP Configuration Issues

**Symptoms**: MCP server not listed in pre-flight MCP check.

1. Verify `.mcp.json` or `.cursor/mcp.json` has the server entry
2. Check `scripts/run_mcp_from_env.cjs` has the server name in its `serverConfigs`
3. Verify `.env` has the required keys for that MCP server
4. Restart Cursor to reload MCP configuration

## Missing API Keys

**Symptoms**: `SKIP: {KEY} not set in .env`.

1. Copy the key template from `.env.example`
2. Fill in the actual key value
3. For OAuth-based tools (Canva): follow MCP auth flow in Cursor instead

## Known Blockers

| Tool | Blocker | Workaround |
|---|---|---|
| Canva MCP | Cursor OAuth redirect URL rejected | Use Connect API directly via Python client |
| ElevenLabs MCP | Cursor filters tools with names >60 chars | Use REST API via smoke script |
| Qualtrics MCP | Not on npm, needs local `git clone` + build | Use REST API via smoke script |
