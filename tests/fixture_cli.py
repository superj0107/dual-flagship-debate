"""Deterministic CLI fixture; never contacts a model service."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--out')
parser.add_argument('--behavior', default='answer')
parser.add_argument('--marker')
parser.add_argument('--touch')
parser.add_argument('--delay', type=float, default=0)
parser.add_argument('--barrier')
args = parser.parse_args()
prompt = sys.stdin.read()
side = re.search(r'^# Adversarial debate - task brief \(Debater ([AB])\)', prompt, re.M).group(1)
round_no = 2 if '## Your own Round 1 output - verbatim' in prompt else 1
if args.marker:
    with open(args.marker, 'a', encoding='utf-8') as stream:
        stream.write(f'{round_no}-{side}\n')
if args.touch and args.behavior != 'descendant':
    Path(args.touch).write_text(f'changed by {side}', encoding='utf-8')
if args.behavior == 'fail-r1' and round_no == 1:
    print('Synthetic child error', file=sys.stderr)
    raise SystemExit(7)
if args.behavior == 'descendant':
    code = 'import sys,time;from pathlib import Path;time.sleep(2);Path(sys.argv[1]).write_text("survived")'
    subprocess.Popen([sys.executable, '-c', code, args.touch or 'descendant.txt'],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(20)
if args.delay:
    time.sleep(args.delay)
if args.barrier:
    folder = Path(args.barrier)
    (folder / side).write_text('started', encoding='utf-8')
    limit = time.monotonic() + 3
    while not all((folder / role).exists() for role in 'AB'):
        if time.monotonic() >= limit:
            raise SystemExit(8)
        time.sleep(.02)
if args.behavior == 'missing':
    raise SystemExit(0)
if args.behavior == 'crlf':
    sys.stdout.buffer.write(b'INDEPENDENT: first line\r\nsecond line\r\n')
    raise SystemExit(0)
if args.behavior == 'bom':
    data = b'\xef\xbb\xbfINDEPENDENT: original BOM transcript\r\n'
    if args.out:
        Path(args.out).write_bytes(data)
    else:
        sys.stdout.buffer.write(data)
    raise SystemExit(0)
if args.behavior == 'empty':
    answer = '  \n'
elif args.behavior == 'oversized':
    answer = 'x' * 5000
else:
    answer = json.dumps({'side': side, 'round': round_no, 'cwd': os.getcwd(),
                         'prompt': prompt, 'evidence': 'synthetic observation'}, ensure_ascii=False)
if args.out:
    Path(args.out).write_text(answer, encoding='utf-8')
    print('STDOUT_PROGRESS_NOT_THE_ANSWER')
else:
    print(answer)
