#!/usr/bin/env python3
"""Compatibility entry point; the installed skill contains the canonical runner."""
from pathlib import Path
import runpy

_runner = Path(__file__).resolve().parents[2] / 'skills' / 'dual-flagship-debate' / 'scripts' / 'run_debate.py'
if __name__ == '__main__':
    runpy.run_path(str(_runner), run_name='__main__')
else:
    globals().update({key: value for key, value in runpy.run_path(str(_runner)).items()
                      if not key.startswith('__')})
