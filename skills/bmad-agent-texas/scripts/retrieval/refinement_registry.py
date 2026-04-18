"""Deterministic refinement strategies registry — Story 27-0.

Flat registry of named refinement strategies adapters can call from their
`refine()` implementations. All strategies are DETERMINISTIC Python (AC-C.6)
— no LLM calls, no network, no clock dependence.

Default strategy `drop_filters_in_order` removes one mechanical-criteria
key per call, in the order specified by the adapter. This is the 27-2 scite
default per Amelia R2 pre-dev check.

Adapters can extend the registry via `register_strategy(name, fn)`. The
registry is module-level and persists across the process; tests reset via
`_STRATEGIES.clear(); _register_builtin_strategies()` patterns.
"""

from collections.abc import Callable
from typing import Any

from .contracts import AcceptanceCriteria

RefinementStrategy = Callable[[dict[str, Any], AcceptanceCriteria, int], dict[str, Any] | None]
"""Refinement strategy signature.

Args:
  current_criteria_mechanical: dict of currently-active mechanical filters
  original_criteria: the full `AcceptanceCriteria` from the intent
  iteration: 1-based refinement round (first refine call is iteration=1)

Returns:
  A NEW mechanical-criteria dict (looser than the current), or None when
  the strategy can no longer loosen the criteria.
"""


_STRATEGIES: dict[str, RefinementStrategy] = {}


def register_strategy(name: str, fn: RefinementStrategy) -> None:
    """Register or override a refinement strategy under `name`."""
    _STRATEGIES[name] = fn


def get_strategy(name: str) -> RefinementStrategy:
    """Fetch a registered strategy, or raise KeyError."""
    if name not in _STRATEGIES:
        raise KeyError(
            f"No refinement strategy registered under {name!r}. "
            f"Known: {sorted(_STRATEGIES)}"
        )
    return _STRATEGIES[name]


def list_strategies() -> list[str]:
    """Sorted list of registered strategy names."""
    return sorted(_STRATEGIES)


def drop_filters_in_order(
    current_mechanical: dict[str, Any],
    _original: AcceptanceCriteria,
    iteration: int,
    *,
    order: list[str] | None = None,
) -> dict[str, Any] | None:
    """Drop one filter key per iteration, in declared order.

    `order` defaults to the current dict's key order (insertion order in
    Python 3.7+). Iteration N (1-based) drops the Nth key in `order`. Returns
    None once every key in `order` has been dropped.
    """
    keys = list(order if order is not None else current_mechanical.keys())
    if iteration < 1 or iteration > len(keys):
        return None
    drop_target = keys[iteration - 1]
    new_mechanical = dict(current_mechanical)
    new_mechanical.pop(drop_target, None)
    return new_mechanical


def _register_builtin_strategies() -> None:
    register_strategy(
        "drop_filters_in_order",
        lambda current, original, iteration: drop_filters_in_order(
            current, original, iteration
        ),
    )


_register_builtin_strategies()


__all__ = [
    "RefinementStrategy",
    "drop_filters_in_order",
    "get_strategy",
    "list_strategies",
    "register_strategy",
]
