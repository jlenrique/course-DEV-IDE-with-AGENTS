"""Retrieval dispatcher — Shape 3-Disciplined orchestration (Story 27-0).

Two code paths (AC-B.4):

- **Single-provider** (default): formulate → execute → apply mechanical +
  provider-scored → acceptance check → refine → loop until met / budget /
  non-improvement. Model A iteration; dispatcher-owned loop.

- **Multi-provider cross-validation** (`intent.cross_validate=True`): fan out
  to every `provider_hints` entry, run each adapter independently under
  single-provider rules, merge by identity key, annotate each merged row
  with a structural `ConvergenceSignal`.

AC-C.11 dumbness clauses enforced here:
  - `convergence_signal` is STRUCTURAL (row-count-agreement, id-overlap,
    identity-key match), NOT semantic.
  - Non-retrying, non-fallback: cross-provider retry is Marcus re-dispatch,
    not a Texas feature. Adapter-level transient-failure is the adapter's
    concern.

Anti-patterns guarded (each has explicit test):
  - Cross-validation is a DISTINCT code path even when `provider_hints` has
    length 1 — we do not fold single-provider into the multi-provider merger.
  - Unknown acceptance-criteria keys log to `refinement_log` (not silent drop).
  - Adapter without `identity_key` + `cross_validate=True` → dispatch-time
    `ValueError`, not silent merge failure.
"""

import logging
from typing import Any

from .base import RetrievalAdapter
from .contracts import (
    AcceptanceCriteria,
    ConvergenceSignal,
    ProviderHint,
    ProviderResult,
    RefinementLogEntry,
    RetrievalIntent,
    TexasRow,
)
from .provider_directory import get_registered_adapter_class

logger = logging.getLogger(__name__)


class DispatchError(ValueError):
    """Dispatcher pre-flight / resolution errors."""


class AdapterFactory:
    """Resolves a `ProviderHint.provider` string to an instantiated adapter.

    Default resolution consults the runtime registry populated via
    `RetrievalAdapter.__init_subclass__`. Tests inject an explicit mapping
    to avoid depending on import-time registration order.
    """

    def __init__(self, overrides: dict[str, RetrievalAdapter] | None = None) -> None:
        self._overrides = dict(overrides or {})

    def get(self, provider: str) -> RetrievalAdapter:
        if provider in self._overrides:
            return self._overrides[provider]
        cls = get_registered_adapter_class(provider)
        if cls is None:
            raise DispatchError(
                f"No RetrievalAdapter registered for provider {provider!r}. "
                f"Check PROVIDER_INFO.id on the adapter subclass and ensure "
                f"the module has been imported."
            )
        try:
            return cls()  # type: ignore[call-arg]
        except TypeError as exc:
            raise DispatchError(
                f"Provider {provider!r} adapter {cls.__name__} has a non-default "
                f"constructor; tests must supply an instance via overrides. "
                f"Underlying error: {exc}"
            ) from exc


def dispatch(
    intent: RetrievalIntent,
    *,
    factory: AdapterFactory | None = None,
) -> list[ProviderResult] | ProviderResult:
    """Route a `RetrievalIntent` to the correct path.

    Returns:
      - `ProviderResult` when `intent.cross_validate is False` (single-provider;
        first hint is used; additional hints logged).
      - `list[ProviderResult]` when `intent.cross_validate is True`; results
        are already merged-and-annotated by `_cross_validate_merge`.

    The two return types are distinct on purpose — the caller branches on
    `cross_validate` in the directive, so we reflect that in the signature
    rather than hiding the distinction.
    """
    factory = factory or AdapterFactory()

    if not intent.provider_hints:
        raise DispatchError(
            "provider_hints is required v1 — no provider discovery"
        )

    if intent.cross_validate:
        return _dispatch_cross_validate(intent, factory)
    return _dispatch_single_provider(intent, factory)


def _dispatch_single_provider(
    intent: RetrievalIntent, factory: AdapterFactory
) -> ProviderResult:
    if len(intent.provider_hints) > 1:
        logger.info(
            "single-provider dispatch with %d hints; using first (%s). "
            "Pass cross_validate=True for fan-out.",
            len(intent.provider_hints),
            intent.provider_hints[0].provider,
        )
    hint = intent.provider_hints[0]
    adapter = factory.get(hint.provider)
    return _run_iteration_loop(adapter, intent, hint)


def _dispatch_cross_validate(
    intent: RetrievalIntent, factory: AdapterFactory
) -> list[ProviderResult]:
    # Pre-flight: every adapter must supply identity_key.
    adapters: list[tuple[ProviderHint, RetrievalAdapter]] = []
    for hint in intent.provider_hints:
        adapter = factory.get(hint.provider)
        _assert_identity_key_available(adapter, hint.provider)
        adapters.append((hint, adapter))

    per_provider: list[ProviderResult] = []
    for hint, adapter in adapters:
        per_provider.append(_run_iteration_loop(adapter, intent, hint))

    merged_rows, signal_by_key, dup_log_by_provider = _cross_validate_merge(
        per_provider,
        adapters_by_provider={h.provider: a for h, a in adapters},
    )

    # Index adapters once; avoids O(N^2) lookup in the annotation loop.
    adapter_by_provider = {h.provider: a for h, a in adapters}

    # Re-emit each provider's result with merged rows annotated + any
    # intra-provider duplicate-identity log entries from the merger
    # (MUST-FIX CR-3).
    annotated_results: list[ProviderResult] = []
    for result in per_provider:
        annotated_rows: list[TexasRow] = []
        adapter = adapter_by_provider[result.provider]
        for row in result.rows:
            key = adapter.identity_key(row)
            # SHOULD-FIX bh-m7: signal_by_key is populated for every key
            # present in the merge; the None-check was dead. Keeping a
            # defensive fallback in case of future invariant change, but
            # removing the explicit `if signal is not None` branch.
            signal = signal_by_key.get(key)
            annotated_rows.append(
                row.model_copy(update={"convergence_signal": signal})
            )
        extra_log = dup_log_by_provider.get(result.provider, [])
        annotated_results.append(
            result.model_copy(
                update={
                    "rows": annotated_rows,
                    "refinement_log": result.refinement_log + extra_log,
                }
            )
        )
    return annotated_results


def _run_iteration_loop(
    adapter: RetrievalAdapter,
    intent: RetrievalIntent,
    hint: ProviderHint,
) -> ProviderResult:
    """Model A iteration loop — dispatcher-owned (AC-B.4)."""
    budget = intent.iteration_budget
    criteria = intent.acceptance_criteria
    refinement_log: list[RefinementLogEntry] = []

    # Log any criteria keys the adapter declares it cannot honor.
    _log_unknown_criteria(adapter, criteria, hint.provider, refinement_log)

    query: Any = adapter.formulate_query(intent)
    raw = adapter.execute(query)
    raw = adapter.apply_mechanical(raw, criteria.mechanical)
    raw = adapter.apply_provider_scored(raw, criteria.provider_scored)

    iterations_used = 1
    if _acceptance_met(raw, criteria.mechanical):
        rows = adapter.normalize(raw)
        return ProviderResult(
            provider=hint.provider,
            rows=rows,
            acceptance_met=True,
            iterations_used=iterations_used,
            refinement_log=refinement_log,
        )

    prev_raw = raw
    if budget == 1:
        # MUST-FIX CR-1 / bh-m1: degenerate single-shot case. Loop below would
        # log a spurious "budget_exhausted" via its else-clause even though
        # refinement was never attempted. Skip the loop entirely and tag the
        # log with a distinct reason so operators see the real cause.
        refinement_log.append(
            RefinementLogEntry(
                iteration=iterations_used,
                reason="single_shot_unmet_budget_too_small_to_refine",
                provider=hint.provider,
            )
        )
    while iterations_used < budget:
        new_query = adapter.refine(query, prev_raw, criteria)
        if new_query is None:
            refinement_log.append(
                RefinementLogEntry(
                    iteration=iterations_used,
                    reason="refine_returned_none",
                    provider=hint.provider,
                )
            )
            break
        curr_raw = adapter.execute(new_query)
        curr_raw = adapter.apply_mechanical(curr_raw, criteria.mechanical)
        curr_raw = adapter.apply_provider_scored(
            curr_raw, criteria.provider_scored
        )
        iterations_used += 1

        delta = adapter.quality_delta(prev_raw, curr_raw)
        if intent.convergence_required and delta <= 0:
            # MUST-FIX bh-m2: do NOT overwrite prev_raw with the worse result
            # before breaking. The whole point of abort-on-non-improvement is
            # to commit to the BETTER (pre-regression) data set. Prior version
            # mutated prev_raw + query in this branch; removed.
            refinement_log.append(
                RefinementLogEntry(
                    iteration=iterations_used,
                    reason="non_improvement_abort",
                    provider=hint.provider,
                    quality_delta=delta,
                )
            )
            break

        prev_raw = curr_raw
        query = new_query

        if _acceptance_met(curr_raw, criteria.mechanical):
            rows = adapter.normalize(curr_raw)
            return ProviderResult(
                provider=hint.provider,
                rows=rows,
                acceptance_met=True,
                iterations_used=iterations_used,
                refinement_log=refinement_log,
            )
    else:
        if budget > 1:
            # The budget==1 case is handled above before the loop; don't
            # double-log when the loop body never ran.
            refinement_log.append(
                RefinementLogEntry(
                    iteration=iterations_used,
                    reason="budget_exhausted",
                    provider=hint.provider,
                )
            )

    rows = adapter.normalize(prev_raw)
    met = _acceptance_met(prev_raw, criteria.mechanical)
    return ProviderResult(
        provider=hint.provider,
        rows=rows,
        acceptance_met=met,
        iterations_used=iterations_used,
        refinement_log=refinement_log,
    )


def _acceptance_met(
    results: Any, mechanical_criteria: dict[str, Any]
) -> bool:
    """Minimal default acceptance rule: `min_results` satisfied.

    Additional mechanical predicates are applied via `apply_mechanical` at
    the adapter level; by the time we reach this check, provider-specific
    filtering has already happened. The dispatcher only needs to gate on
    the count-floor to decide whether to keep iterating.

    MUST-FIX CR-2 + M-5 (code-review 2026-04-18): `min_results` must be a
    positive integer. `0` (trivially-met footgun), negative values, and
    non-parseable strings (operator typo) all raise `DispatchError` — we
    NEVER silently fall back to `count > 0` when a caller tried to pass a
    floor and we couldn't interpret it.
    """
    try:
        count = len(results)
    except TypeError:
        count = 0
    min_results = mechanical_criteria.get("min_results")
    if min_results is None:
        return count > 0
    try:
        min_floor = int(min_results)
    except (TypeError, ValueError) as exc:
        raise DispatchError(
            f"acceptance_criteria.mechanical['min_results'] must be a "
            f"positive integer; got {min_results!r} "
            f"(type {type(min_results).__name__})"
        ) from exc
    if min_floor < 1:
        raise DispatchError(
            f"acceptance_criteria.mechanical['min_results'] must be >= 1; "
            f"got {min_floor}. Use `min_results: 1` if any-row acceptance "
            f"is intended; omit the key if acceptance should always pass."
        )
    return count >= min_floor


def _log_unknown_criteria(
    adapter: RetrievalAdapter,
    criteria: AcceptanceCriteria,
    provider: str,
    refinement_log: list[RefinementLogEntry],
) -> None:
    """Emit WARNING + refinement_log entry per key the adapter does not honor.

    Forward-compatible semantics per AC-B.2 strengthening (Winston MUST-FIX #3):
    we never silently drop criteria keys. Dispatcher keeps running with the
    known criteria; unknown keys surface in the returned `refinement_log`.
    """
    honored = adapter.declare_honored_criteria()
    all_keys = set(criteria.mechanical) | set(criteria.provider_scored)
    for key in sorted(all_keys - honored):
        logger.warning(
            "criterion %r not evaluable by provider %r (adapter %s)",
            key,
            provider,
            type(adapter).__name__,
        )
        refinement_log.append(
            RefinementLogEntry(
                iteration=0,
                reason="not evaluable by this provider",
                provider=provider,
                criterion_key=key,
            )
        )


def _assert_identity_key_available(
    adapter: RetrievalAdapter, provider: str
) -> None:
    """Cross-validation requires a working `identity_key`. Fail fast at dispatch."""
    try:
        probe = TexasRow(source_id="__probe__", provider=provider)
        adapter.identity_key(probe)
    except NotImplementedError as exc:
        raise DispatchError(
            f"Provider {provider!r} does not implement identity_key; cannot "
            f"participate in cross_validate=true fan-out. Drop cross_validate "
            f"from the intent or use a different provider. Underlying: {exc}"
        ) from exc


def _cross_validate_merge(
    per_provider_results: list[ProviderResult],
    *,
    adapters_by_provider: dict[str, RetrievalAdapter],
) -> tuple[list[TexasRow], dict[str, ConvergenceSignal], dict[str, list[RefinementLogEntry]]]:
    """Structural merger over identity keys.

    Returns:
      - merged_rows: deduplicated TexasRows, preserving first-seen instance per provider
      - signal_by_key: per-identity-key ConvergenceSignal annotation
      - dup_log_by_provider: per-provider refinement-log entries recording intra-provider
        identity-key duplicates (MUST-FIX CR-3: don't silently drop)
    """
    # identity_key -> {provider: row}
    rows_by_key: dict[str, dict[str, TexasRow]] = {}
    dup_log_by_provider: dict[str, list[RefinementLogEntry]] = {}
    for result in per_provider_results:
        adapter = adapters_by_provider[result.provider]
        for row in result.rows:
            key = adapter.identity_key(row)
            bucket = rows_by_key.setdefault(key, {})
            if result.provider not in bucket:
                bucket[result.provider] = row
            else:
                # MUST-FIX CR-3: intra-provider identity-key duplicate surfaces
                # as a refinement-log entry rather than a silent drop. Common
                # case: a scholarly provider returning multiple context windows
                # for the same DOI — we keep the first, but the caller needs
                # to know duplicates existed (for adapter-side pagination-bug
                # detection and for quality metrics).
                dup_log_by_provider.setdefault(result.provider, []).append(
                    RefinementLogEntry(
                        iteration=0,
                        reason="intra_provider_identity_key_duplicate",
                        provider=result.provider,
                        criterion_key=key,
                    )
                )

    all_providers = [r.provider for r in per_provider_results]
    signal_by_key: dict[str, ConvergenceSignal] = {}
    merged_rows: list[TexasRow] = []

    for key, bucket in rows_by_key.items():
        found_in = sorted(bucket.keys())
        # SHOULD-FIX bh-m8: match sort order with `found_in` for consistent display.
        missing_from = sorted(p for p in all_providers if p not in bucket)
        # Semantic: "agreeing" requires at least two providers to have
        # independently surfaced the same identity. A single provider in the
        # fan-out (N=1 degenerate case, or N>1 with only one provider finding
        # the row) always flags `single_source_only` — the row cannot be
        # corroborated when no peer had it. SHOULD-FIX H-5: populate
        # `providers_disagreeing` in the single-source branch too so
        # downstream consumers see WHICH peers were checked-and-missed.
        if len(found_in) >= 2 and len(found_in) == len(all_providers):
            signal = ConvergenceSignal(
                providers_agreeing=found_in,
                providers_disagreeing=[],
                single_source_only=[],
            )
        elif len(found_in) == 1:
            signal = ConvergenceSignal(
                providers_agreeing=[],
                providers_disagreeing=missing_from,
                single_source_only=found_in,
            )
        else:
            signal = ConvergenceSignal(
                providers_agreeing=found_in,
                providers_disagreeing=missing_from,
                single_source_only=[],
            )
        signal_by_key[key] = signal
        merged_rows.append(next(iter(bucket.values())))

    return merged_rows, signal_by_key, dup_log_by_provider


__all__ = [
    "AdapterFactory",
    "DispatchError",
    "dispatch",
]
