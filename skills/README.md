# Skills

SKILL.md directories providing tool-specific capabilities for the collaborative intelligence system. Cursor auto-discovers skill subdirectories containing a `SKILL.md` file.

Each skill directory follows the BMad progressive disclosure pattern:

```
skills/{tool-name}/
├── SKILL.md          # Capability routing and agent interface
├── references/       # Detailed capability instructions (loaded on demand)
├── scripts/          # Python code for API calls, file operations, state management
└── assets/           # Templates and starter files for output generation
```

**Note:** This directory holds production skills for the course content system, distinct from `.cursor/skills/` which contains BMad Method development skills.

## Planned Skills

| Skill | Purpose | Epic |
|-------|---------|------|
| `gamma-api-mastery/` | Gamma slide generation integration | Epic 3 |
| `elevenlabs-audio/` | ElevenLabs voice synthesis integration | Epic 3 |
| `canvas-deployment/` | Canvas LMS deployment workflows | Epic 3 |
| `production-coordination/` | Multi-agent workflow coordination | Epic 4 |
| `quality-control/` | Quality validation and accessibility checking | Epic 3-4 |
| `pre-flight-check/` | System validation and connectivity verification | Epic 1 |
| `run-reporting/` | Production intelligence and run analysis | Epic 4 |
