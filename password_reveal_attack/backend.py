#!/usr/bin/env python3
"""
Unified backend abstraction for running attacks against:
  - The real Gandalf API       (--target api)
  - The local GPT-5.4 emulator (--target emulator)
  - The hardened V2 emulator   (--target emulator_v2)

Usage:
    from backend import get_backend
    backend = get_backend("emulator")   # or "api" or "emulator_v2"
    resp = backend.send_message("Hello")
    ok   = backend.guess_password("OCTOPODES")
"""

import argparse
import os
import sys

# ── Paths ─────────────────────────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_CLI_DIR = os.path.join(_HERE, "..", "cli")
_EMU_DIR = os.path.join(_HERE, "..", "test_emulator")


# ── Backend wrapper ───────────────────────────────────────────────────────────


class _APIBackend:
    """Wraps cli/gandalf.py for the real Gandalf API."""

    name = "api"

    def __init__(self):
        sys.path.insert(0, _CLI_DIR)
        import gandalf  # noqa: E402

        self._mod = gandalf
        self._cookies = gandalf.load_cookies()

    def send_message(self, prompt, **kw):
        return self._mod.send_message(prompt, cookies=self._cookies, **kw)

    def guess_password(self, password, **kw):
        return self._mod.guess_password(password, cookies=self._cookies, **kw)


class _EmulatorBackend:
    """Wraps test_emulator/emulator.py (V1) for the local GPT-5.4 emulator."""

    name = "emulator"

    def __init__(self):
        sys.path.insert(0, _EMU_DIR)
        import emulator  # noqa: E402

        self._mod = emulator

    def send_message(self, prompt, **kw):
        return self._mod.send_message(prompt, **kw)

    def guess_password(self, password, **kw):
        return self._mod.guess_password(password, **kw)


class _EmulatorV2Backend:
    """Wraps test_emulator/emulator_v2.py — hardened defense."""

    name = "emulator_v2"

    def __init__(self):
        sys.path.insert(0, _EMU_DIR)
        import emulator_v2  # noqa: E402

        self._mod = emulator_v2

    def send_message(self, prompt, **kw):
        return self._mod.send_message(prompt, **kw)

    def guess_password(self, password, **kw):
        return self._mod.guess_password(password, **kw)


_BACKENDS = {
    "api": _APIBackend,
    "emulator": _EmulatorBackend,
    "emulator_v2": _EmulatorV2Backend,
}


def get_backend(target="api"):
    """Return a backend instance for the given target name."""
    cls = _BACKENDS.get(target)
    if cls is None:
        raise ValueError(f"Unknown target '{target}'. Choose from: {list(_BACKENDS)}")
    return cls()


def add_target_arg(parser: argparse.ArgumentParser):
    """Add --target argument to an argparse parser."""
    parser.add_argument(
        "--target",
        choices=list(_BACKENDS),
        default="api",
        help="Attack target: 'api' for real Gandalf, 'emulator' for local V1, 'emulator_v2' for hardened V2 (default: api)",
    )
