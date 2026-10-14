# test_lwd_scenarios.py
"""Verify lwd_logger under the 4 VLLM_LWD_LOG_LEVEL scenarios.

Run inside the vllm docker container (vllm fully installed):

    python test_lwd_scenarios.py

Each scenario spawns a subprocess with a different VLLM_LWD_LOG_LEVEL so the
module-level singleton `lwd_logger` is re-initialized per scenario.
"""
import os
import subprocess
import sys

# The child code that imports the real interface and emits one message per
# severity, so we can observe the level filtering + [lwd] prefix.
CHILD = r'''
from vllm.lwd_logger import lwd_logger

lwd_logger.debug("DEBUG message")
lwd_logger.info("INFO message")
lwd_logger.warning("WARNING message")
lwd_logger.error("ERROR message")
lwd_logger.critical("CRITICAL message")
'''

SCENARIOS = [
    ("1. DISABLE (default / unset)", None,
     "expected: no [lwd] output at all"),
    ("2. DEBUG (show everything)", "DEBUG",
     "expected: DEBUG + INFO + WARNING + ERROR + CRITICAL"),
    ("3. INFO  (info and above)", "INFO",
     "expected: INFO + WARNING + ERROR + CRITICAL"),
    ("4. ERROR (error and above)", "ERROR",
     "expected: ERROR + CRITICAL"),
]


def run(level):
    env = os.environ.copy()
    if level is None:
        env.pop("VLLM_LWD_LOG_LEVEL", None)
    else:
        env["VLLM_LWD_LOG_LEVEL"] = level
    return subprocess.run(
        [sys.executable, "-c", CHILD],
        env=env,
        capture_output=True,
        text=True,
    )


def main():
    for title, level, expect in SCENARIOS:
        print("=" * 70)
        print(title)
        print(expect)
        print("-" * 70)
        proc = run(level)
        out = (proc.stdout + proc.stderr).strip()
        print(out if out else "(no output)")
        print()


if __name__ == "__main__":
    main()
