"""Marcus dispatch contract surfaces.

This package centralizes the standard envelope/receipt/error contracts used by
Marcus boundary dispatch edges.
"""

from .contract import (
    DISPATCH_KIND_TO_SPECIALIST,
    DispatchContractError,
    DispatchEnvelope,
    DispatchError,
    DispatchErrorKind,
    DispatchInternalError,
    DispatchKind,
    DispatchOutcome,
    DispatchReceipt,
    DispatchSpecialistUnavailableError,
    DispatchTimeoutError,
    DispatchValidationFailedError,
    SpecialistId,
    _classify_dispatch_kind,
    build_dispatch_envelope,
    build_dispatch_receipt,
    dispatch_end_log_fields,
    dispatch_start_log_fields,
)

__all__ = [
    "DISPATCH_KIND_TO_SPECIALIST",
    "DispatchContractError",
    "DispatchEnvelope",
    "DispatchError",
    "DispatchErrorKind",
    "DispatchInternalError",
    "DispatchKind",
    "DispatchOutcome",
    "DispatchReceipt",
    "DispatchSpecialistUnavailableError",
    "DispatchTimeoutError",
    "DispatchValidationFailedError",
    "SpecialistId",
    "_classify_dispatch_kind",
    "build_dispatch_envelope",
    "build_dispatch_receipt",
    "dispatch_end_log_fields",
    "dispatch_start_log_fields",
]
