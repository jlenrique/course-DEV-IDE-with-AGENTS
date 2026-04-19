"""Consumer-contract fixture package (Story 31-3 AC-T.6).

Fixtures in this package are imported (via ``importlib.util``) by
``tests/contracts/test_consumer_fixtures_load.py`` — they are NOT pytest-collected
(filenames start with ``fixture_``, not ``test_``). Each fixture exposes a
``demonstrate() -> None`` callable the loader invokes.
"""
