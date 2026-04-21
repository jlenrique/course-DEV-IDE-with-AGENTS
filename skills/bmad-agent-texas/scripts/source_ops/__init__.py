"""Source operations helpers for the Texas wrangler.

Sub-package for format-specific source normalization utilities invoked
after the runner dispatches a fetch. Each module here is pure (no
network, no side effects other than optional file IO) and may be used
either as a library (from ``source_wrangler_operations``) or as a
standalone CLI (``python <path>``).

The package is intentionally import-lightweight — modules here are
typically loaded lazily via ``importlib.util.spec_from_file_location``
because the parent directory (``skills/bmad-agent-texas``) contains a
hyphen and cannot be imported with the standard ``from ... import``
syntax.
"""
