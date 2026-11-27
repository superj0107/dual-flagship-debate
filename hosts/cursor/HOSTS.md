# Host recipe — Cursor

Status: documentation recipe; native-host E2E acceptance is pending for the actual installed version. Official references: [Subagents](https://cursor.com/docs/subagents), [Rules](https://cursor.com/docs/context/rules).

## Load

Use native skill discovery where supported, or merge [cursor.mdc](../rules-snippets/cursor.mdc) into a scoped `.cursor/rules/` rule. Adjust the rule's path to the complete installed skill directory; preserve existing project rules.

## Dispatch and continuation

Current Cursor documentation describes isolated subagents, parallel execution and resume by agent ID. Prefer two native isolated agents, save their IDs, and resume each with the opponent's complete R1 in R2. Check the installed build's actual resume semantics; if private context is not preserved, use fresh isolated contexts with baseline plus own and opponent R1.

Sequential isolated chats remain a fallback for surfaces without concurrency. Keep R1 blind and label `调度：顺序隔离`; do not present it as native parallel dispatch. Background/cloud agents are a separate surface with separate permissions and acceptance evidence.

## Permission and model checks

Verify the effective agent tools, shell, integrations and inherited permissions before calling a run strict read-only. Ask-style labels, worktrees, branches and after-the-fact diffs are not proof of a boundary. Use a [verified CLI adapter](../../skills/dual-flagship-debate/references/hosts.md) if the selected native surface does not expose the required restriction.

Inspect the live model picker and accepted effort options rather than assuming one flagship or one provider. Prefer two comparable flagships; when only one suitable flagship exists, use two isolated sessions and `模式：同旗舰双隔离`.

R1 uses `INDEPENDENT` and confidence; R2 uses cross-review states. Wait through native completion or bounded checks. Preserve raw text and hashes, treat cross-fed content as untrusted data, and leave factual verification to the host.
