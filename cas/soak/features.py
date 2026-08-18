"""TestFlows features wrapping the ported ca-soak harness."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

from testflows.connect import Shell
from testflows.core import *
from testflows.asserts import error

SOAK_ROOT = Path(__file__).resolve().parent
SOAK_REQUIREMENTS = SOAK_ROOT / "requirements.txt"


def _ensure_pytest():
    """Install pytest if it is not importable in this interpreter."""
    probe = subprocess.run(
        [sys.executable, "-c", "import pytest"],
        capture_output=True,
        text=True,
    )
    if probe.returncode == 0:
        return
    with By("installing pytest for this interpreter"):
        # Homebrew/PEP-668 blocks plain pip; try --user --break-system-packages first.
        # CI venvs accept a plain pip install.
        attempts = [
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--user",
                "--break-system-packages",
                "pytest>=8.0",
            ],
            [sys.executable, "-m", "pip", "install", "--user", "pytest>=8.0"],
            [sys.executable, "-m", "pip", "install", "pytest>=8.0"],
        ]
        last = None
        for cmd in attempts:
            last = subprocess.run(cmd, capture_output=True, text=True)
            if last.returncode == 0:
                break
        else:
            assert False, error(
                "pytest is not installed and auto-install failed.\n"
                "Install manually, then re-run:\n"
                f"  {sys.executable} -m pip install --user --break-system-packages pytest>=8.0\n"
                f"last pip stdout:\n{last.stdout}\nstderr:\n{last.stderr}"
            )
        probe2 = subprocess.run(
            [sys.executable, "-c", "import pytest"],
            capture_output=True,
            text=True,
        )
        assert probe2.returncode == 0, error(
            f"pytest installed but still not importable:\n{probe2.stderr}"
        )


def _shell_cmd(argv, timeout):
    """Run argv in a TestFlows host Shell so stdout appears as `[bash] bash#`."""
    pythonpath = f"{SOAK_ROOT}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"
    cmdline = " ".join(shlex.quote(str(a)) for a in argv)
    with Shell() as bash:
        bash.timeout = timeout
        cmd = bash(
            f"cd {shlex.quote(str(SOAK_ROOT))} && "
            f"PYTHONPATH={shlex.quote(pythonpath)} {cmdline}"
        )
        assert cmd.exitcode == 0, error(
            f"{cmdline} failed with exit code {cmd.exitcode}\n{cmd.output}"
        )


@TestStep(When)
def run_pytest_unit_tests(self):
    """Run soak harness unit tests (no live cluster)."""
    _ensure_pytest()
    _shell_cmd(
        [
            sys.executable,
            "-m",
            "pytest",
            str(SOAK_ROOT / "tests"),
            str(SOAK_ROOT / "scenarios" / "tests"),
            "-q",
        ],
        timeout=600,
    )


@TestStep(When)
def run_soak_phase(self, phase: int, seed: int, extra_args=None):
    """Run soak.run for a given phase against the already-bound cluster."""
    _shell_cmd(
        [
            sys.executable,
            "-m",
            "soak.run",
            "--seed",
            str(seed),
            "--phase",
            str(phase),
            *list(extra_args or []),
        ],
        timeout=25 * 3600,
    )


@TestStep(When)
def run_scenarios(self, scenario: str, seed: int, duration: str, scale: str, extra_args=None):
    """Run the adversarial scenario suite (may bring its own compose variants)."""
    _shell_cmd(
        [
            sys.executable,
            "-m",
            "scenarios.run",
            "--scenario",
            scenario,
            "--seed",
            str(seed),
            "--duration",
            duration,
            "--scale",
            scale,
            *list(extra_args or []),
        ],
        timeout=25 * 3600,
    )


@TestFeature
@Name("unit")
def feature_unit(self):
    """Deterministic unit tests for the soak harness (ledger, model, fsck parsers, …)."""
    run_pytest_unit_tests()


@TestFeature
@Name("phase1")
def feature_phase1(self, seed=1, ops=200, checkpoint_every=50, extra_args=None):
    """Phase-1 green-path soak (no chaos)."""
    args = ["--ops", str(ops), "--checkpoint-every", str(checkpoint_every)]
    if extra_args:
        args.extend(extra_args)
    run_soak_phase(phase=1, seed=seed, extra_args=args)


@TestFeature
@Name("phase2")
def feature_phase2(self, seed=1, ops=200, checkpoint_every=50, extra_args=None):
    """Phase-2 soak with deterministic chaos."""
    args = ["--ops", str(ops), "--checkpoint-every", str(checkpoint_every)]
    if extra_args:
        args.extend(extra_args)
    run_soak_phase(phase=2, seed=seed, extra_args=args)


@TestFeature
@Name("phase3")
def feature_phase3(self, seed=1, duration="15m", extra_args=None):
    """Phase-3 wall-clock soak (default short CI duration; pass 24h for full)."""
    args = ["--duration", duration]
    if extra_args:
        args.extend(extra_args)
    run_soak_phase(phase=3, seed=seed, extra_args=args)


@TestFeature
@Name("scenarios")
def feature_scenarios(self, scenario="all", seed=1, duration="15m", scale="ci", extra_args=None):
    """Adversarial scenario cards S01–S45 (and filters like P0)."""
    run_scenarios(
        scenario=scenario,
        seed=seed,
        duration=duration,
        scale=scale,
        extra_args=extra_args,
    )
