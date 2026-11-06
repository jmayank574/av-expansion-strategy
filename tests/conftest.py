"""Test session setup.

Several tests regenerate the memo, deck and charts to check them. Those files are tracked in git, and a deck rebuild changes bytes
(timestamps) even when the content is identical, so a plain `pytest` would leave the working tree dirty. Snapshot them at the start of the
session and put them back at the end. Anyone who regenerates the outputs deliberately (make memo / make deck) does so before running tests,
so the snapshot already holds the new versions.
"""
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GENERATED = ["reports/memo.md", "reports/deck.pptx", "reports/charts/quadrant.png", "reports/charts/unit_economics.png"]


@pytest.fixture(scope="session", autouse=True)
def _leave_generated_reports_as_found():
    snap = {p: (ROOT / p).read_bytes() for p in GENERATED if (ROOT / p).exists()}
    yield
    for p, b in snap.items():
        (ROOT / p).write_bytes(b)
