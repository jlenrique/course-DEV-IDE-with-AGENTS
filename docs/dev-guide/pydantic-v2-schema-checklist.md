# Pydantic-v2 Schema Checklist

**Audience:** dev agents authoring schema-shape stories (31-2, 31-3, 29-1, 32-2, future).
**Source:** extracted from Story 31-1 G5+G6 findings (MF-1 through MF-6, SF-1 through SF-13, and R2 riders W-1/S-3/S-4/Q-5).
**Companion:** `docs/dev-guide/scaffolds/schema-story/` pre-wires every idiom below. If you use the scaffold, you inherit this checklist automatically.

This is a working reference, not a spec. Every rule here maps to a real bug that was caught at G6 on 31-1 and would have been a production-grade miss if the layered code review hadn't landed it. Follow these and you will not see those same findings again.

---

## 1. Model configuration — every model

Every Pydantic model in a schema-shape story must carry `model_config` with at minimum these flags:

```python
from pydantic import BaseModel, ConfigDict

class MyShape(BaseModel):
    model_config = ConfigDict(
        extra="forbid",            # unknown fields raise, don't silently accept
        validate_assignment=True,  # mutation re-validates (catches MF-1, MF-2, MF-3)
    )
```

**Why `validate_assignment=True` is mandatory:** without it, `instance.field = bad_value` assigns without re-running validators. On 31-1, this let a mutated `EventEnvelope` with a naive datetime slip past MF-4's timezone-aware enforcement because the validator only fired at construction. G6 Edge Case Hunter caught it. The fix is the flag. Default-off is a Pydantic-v2 footgun.

**When to add `frozen=True`:** for value-objects and references (31-1's `LearningModel`, `PlanRef`) where immutability is part of the contract. Don't add it to mutable primitives like the top-level plan — that breaks revision updates.

## 2. Timezone-aware datetimes — every timestamp field

Every `datetime` field needs a validator that rejects naive (no-tzinfo) values:

```python
from datetime import UTC, datetime
from pydantic import field_validator

class MyShape(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    @field_validator("created_at")
    @classmethod
    def _enforce_tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("datetime field must be timezone-aware")
        return v
```

**Never use `datetime.utcnow()`.** It's deprecated as of Python 3.12 and returns a naive datetime. Use `datetime.now(tz=UTC)`. This is G6 MF-4 distilled.

**All five 31-1 datetime fields hit this on G6.** `created_at`, `updated_at`, `ratified_at`, `locked_at`, event `timestamp`. Every one needed the validator. For a schema-shape story with datetime fields, add the validator to each.

## 3. UUID4 validation — if the story has event IDs

If the schema has a field that holds a UUID, validate that it's UUID4 specifically (version-4):

```python
from uuid import UUID
from pydantic import field_validator

@field_validator("event_id")
@classmethod
def _enforce_uuid4(cls, v: str) -> str:
    try:
        parsed = UUID(v, version=4)
    except (ValueError, AttributeError, TypeError) as e:
        raise ValueError("event_id must be a UUID4 string") from e
    if parsed.version != 4:
        raise ValueError("event_id must be UUID4 specifically")
    return str(parsed)
```

This is G6 SF-5 from 31-1. Without the version check, UUID1/UUID3/UUID5 strings pass a naive `UUID(v)` parse and land in the log, then fail at a downstream consumer that assumed UUID4 randomness. Fail at construction.

## 4. Closed enums get three red-rejection surfaces

Closed-set literal fields (like 31-1's `weather_band`) must reject invalid values via three independent surfaces:

| Surface | What it asserts | 31-1 test |
|---------|----------------|-----------|
| Pydantic validator | `Literal` type rejects at construction and on assignment | `test_weather_band_rejects_red_on_direct_construction` |
| JSON Schema `enum` array | Emitted schema enumerates the valid set | `test_lesson_plan_json_schema_parity` |
| `TypeAdapter` round-trip | External validators (jsonschema lib) see the same set | `test_weather_band_rejects_red_via_type_adapter` |

All three must pass for a closed-enum field. G5 Murat caught the missing TypeAdapter surface on 31-1 — if you skip it, a red value can come through an external `jsonschema.validate()` call without hitting your Pydantic validator.

## 5. Internal audit fields — `Field(exclude=True) + SkipJsonSchema`

Fields that should never leak to operator-facing output — audit-only provenance, internal actors — use this pattern:

```python
from typing import Literal
from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

class ScopeDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    proposed_by: Literal["system", "operator"]                              # public surface
    _internal_proposed_by: SkipJsonSchema[
        Literal["marcus", "marcus-intake", "marcus-orchestrator", "irene", "maya"]
    ] = Field(
        default="marcus",
        exclude=True,
        description="Audit-surface actor; never serialized to operator-facing payloads.",
    )
```

Three things to know:

1. **`exclude=True` in Pydantic v2 cannot be overridden by `model_dump(exclude=set())`.** If a caller genuinely needs audit-surface output, provide a dedicated opt-in helper (31-1 pattern: `to_audit_dump()` method). Do not expose a flag that flips `exclude`.
2. **Give the internal field a default.** Otherwise round-tripping a Maya-facing payload through `model_validate_json` fails because the field is absent and has no default. 31-1 uses `default="marcus"` for this reason.
3. **`SkipJsonSchema[...]` wrapping the type keeps the field out of the emitted JSON Schema.** Without it, the JSON Schema exposes the internal taxonomy even though `exclude=True` hides it from `model_dump`.

R2 rider S-4 from 31-1 codified this whole pattern. G6 MF-4 on 31-1 is a variant of the same trap.

## 6. Free-text verbatim fields — no `min_length`

If the field is a `rationale` or `commentary` or any verbatim string, it must accept empty / single-char / whitespace-only:

```python
rationale: str = Field(
    default="",
    description="Free text, stored verbatim, surfaced verbatim. No parsing.",
)
# NO min_length. NO regex. NO normalization.
```

This is R1 ruling amendment 16 + R2 rider S-2. If you add `min_length=1`, you break the "stored verbatim" contract, and Maya's empty-string scope decision rationale gets rejected silently. If you add normalization (strip whitespace, collapse newlines), Marcus's confirmation echo doesn't match what Maya typed and the single-writer invariant is leaky.

**Test it with adversarial inputs:** empty string, single space, single tab (`\t`), `\r\n`, emoji, single character, leading/trailing whitespace. 31-1's `test_rationale_verbatim_roundtrip.py` covers twelve parametrized cases.

## 7. Revision monotonicity — real method, not test helper

If the schema carries a `revision` field (31-1's `LessonPlan.revision`), the "next revision" check must live on the model, not in a test helper:

```python
class LessonPlan(BaseModel):
    revision: int = Field(default=0, ge=0)

    def apply_revision(self, new_revision: int) -> "LessonPlan":
        if new_revision <= self.revision:
            raise StaleRevisionError(
                f"new revision {new_revision} not greater than current {self.revision}"
            )
        return self.model_copy(update={"revision": new_revision})
```

31-1's original implementation had the monotonicity check in the test helper. G6 MF-6 flagged this as tautological ("test helper raises if its own helper raises"). The fix moves the check onto the model via a real method. Test then exercises the real method.

## 8. Shape-pin tests — per-family, not batched

Per R2 rider AM-1 from 31-1, **each shape family gets its own snapshot-allowlist pin test file**:

- `test_lesson_plan_shape_stable.py` — for the LessonPlan family
- `test_fit_shape_stable.py` — for the FitReport family
- `test_scope_shape_stable.py` — for the ScopeDecision family

Do not combine. When one family changes, its test fails in isolation. This is what allows per-family version bumps and per-family SCHEMA_CHANGELOG entries.

## 9. Required-vs-optional bidirectional parity

Per R2 rider AM-2 from 31-1, the JSON Schema ↔ Pydantic parity test must assert the mapping in **both directions**:

- Every Pydantic-required field appears in JSON Schema's `required` array.
- Every JSON-Schema-`required` field is Pydantic-required.

Without the bidirectional check, a field demoted from required to optional on the Pydantic side drifts out of sync with its emitted JSON Schema silently. The scaffold's `test_json_schema_parity.py.tmpl` has both directions wired up.

## 10. Digest determinism tests

If the schema carries a `digest` (sha256 of canonical-JSON payload), the determinism test must cover these edge cases per R2 rider AM-3:

- Nested list order changes digest: `{"a": [1, 2]}` ≠ `{"a": [2, 1]}`.
- `None` vs missing field changes digest: `{"a": None}` ≠ `{}`.
- Key construction order does NOT change digest: `dict([("a", 1), ("b", 2)])` digest equals `dict([("b", 2), ("a", 1)])`.
- Unicode normalization is NOT applied (no NFC/NFD pass). `"é"` (single char) and `"e\u0301"` (combining) digest differently. Document this in the digest module docstring.

## 11. No-leak grep test — R1 amendment 17, mandatory

Every schema-shape story ships a `test_no_intake_orchestrator_leak_<schema_name>.py` per R2 rider S-3. Scans:

- All user-facing Pydantic `Field(description=...)` strings.
- All companion Markdown docs (`dials-spec.md`, SCHEMA_CHANGELOG entries).
- All `model_dump()` / `model_dump_json()` output.

Forbidden tokens: `intake`, `orchestrator` (case-insensitive, word-boundary). Marcus is one voice. Internal Python module names, attribute names, and Literal taxonomy values on private `_internal_*` audit fields are exempt. Lines carrying `# noqa: no-leak-grep` are exempt.

**This test is non-negotiable.** If you omit it, R1 ruling amendment 17 is violated and the story fails at G5 party-mode review.

## 12. Warn-once deduplication

If your schema has a validator that warns (not raises) on unknown inputs — 31-1's `validate_event_type` pattern — the warning must deduplicate per-process:

```python
_seen_unknown_event_types: set[str] = set()

def validate_event_type(event_type: str) -> None:
    if event_type in KNOWN_EVENT_TYPES:
        return
    if event_type not in _seen_unknown_event_types:
        _seen_unknown_event_types.add(event_type)
        warnings.warn(f"unknown event_type: {event_type}", stacklevel=2)
```

G6 SF-4 from 31-1. Without dedup, a busy loop emits the same warning thousands of times and the signal gets lost in the noise.

## 13. State-machine bypass guard — if applicable

If your schema has a state machine (31-1's `ScopeDecision`), add a `model_validator(mode="after")` that rejects illegal state combinations that couldn't be caught field-by-field:

```python
@model_validator(mode="after")
def _guard_locked_requires_maya(self) -> "ScopeDecision":
    if self.state == "locked" and self.ratified_by != "maya":
        raise ValueError("state == 'locked' requires ratified_by == 'maya'")
    return self
```

This is R2 rider Q-5 from 31-1. The guard catches construction paths that would otherwise let an unauthorized actor "lock" a decision by assembling fields in the wrong order.

## 14. JSON Schema round-trip — `additionalProperties: false`

Verify that `extra="forbid"` in your model propagates to `additionalProperties: false` in the emitted JSON Schema. If it doesn't, external jsonschema validators will accept unknown fields that Pydantic would reject. This is in the scaffold's parity test.

---

## Scaffold maintenance discipline

When a new Pydantic-v2 pitfall is caught at G6 on a real story:

1. Fix the story code.
2. Add the idiom to `docs/dev-guide/scaffolds/schema-story/src/schema.py.tmpl` with a comment referencing the finding.
3. Add a rule to this document describing the pitfall + fix.
4. If the idiom also surfaces in test-authoring patterns, propagate to the scaffold's test templates.

Scaffold and checklist update together. A scaffold without a matching checklist entry is a leak waiting to happen.

---

## Changelog

| Version | Date | Source |
|---------|------|--------|
| v1 | 2026-04-18 | Extracted from Story 31-1 G5+G6 closure (MF-1..MF-6 + SF-1..SF-13 + R2 riders W-1/Q-5/S-2/S-3/S-4/AM-1/AM-2/AM-3) |
