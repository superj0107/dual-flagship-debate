# Host recipe — **Gemini CLI**

## 1. Load the protocol

Gemini CLI reads `GEMINI.md` (project and user level). Whether it also loads `SKILL.md` depends on
the version's skills/extensions support — check before assuming:

```bash
gemini --help | grep -i -E "skill|extension"
```

- **If skills are supported**: copy `skills/dual-flagship-debate/` into the skill root that
  `--help` / the docs name, then reference the skill by name.
- **If not**: paste the trigger block from [`../rules-snippets/README.md`](../rules-snippets/README.md)
  into `GEMINI.md`, and let the model read
  `skills/dual-flagship-debate/SKILL.md` from disk when the protocol is needed. That works because
  the protocol is plain instructions, not code.

## 2. Dispatch

Gemini CLI has no isolated read-only subagent primitive. Use the **CLI-ephemeral** pattern:

```bash
# Round 1 — two isolated runs, in parallel, read-only as far as your version allows
gemini -p "$(cat r1-A.prompt.md)" > r1-A.out.md 2> r1-A.log.txt &
gemini -p "$(cat r1-B.prompt.md)" > r1-B.out.md 2> r1-B.log.txt &
wait
```

Or register the pair in the portable runner (recommended, it handles Round 2 replay, timeouts and the
read-only guard):

```json
{ "debaters": {
    "A": { "name": "gemini-cli", "cmd": ["gemini", "-p"] },
    "B": { "name": "claude-cli", "cmd": ["claude", "-p", "--output-format", "text"] } } }
```

## 3. Read-only

Confirm the current flag before relying on it (`gemini --help`): approval/plan modes and sandbox
settings are renamed between releases. Whatever the flag, verify empirically with a throwaway prompt
that asks the model to create a file — if a file appears, your configuration is not read-only.

## 4. Round 2

One-shot: start two **fresh** runs and paste `[Step 0 baseline + own R1 + opponent R1]`.

## 5. Model pairing

If the CLI exposes only one flagship tier, run **Tier 2** (two isolated runs, orthogonal lenses) and
label the verdict `模式：同旗舰双隔离`. For a cross-vendor Tier 1 pair, set debater B to a different
vendor's CLI — the two transcripts do not care where they came from.
