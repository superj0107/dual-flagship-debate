# Host recipe — **Claude Code**

适用前提：Claude Code ≥ 2.x，用户级技能根 `~/.claude/skills`。安装后技能会出现在
`/` 命令列表里（可用 `claude -p --output-format stream-json` 的 init 事件里 `slash_commands`
确认，比问模型"你有这个 skill 吗"可靠得多）。

## 1. 安装与触发

```bash
cp -r dual-flagship-debate/skills/dual-flagship-debate ~/.claude/skills/
```

```
/dual-flagship-debate <议题>
```

## 2. 选模

Claude Code 侧通常只有一个 Claude 旗舰可用 → **Tier 2 同旗舰双隔离**：

- 两个 `general-purpose` 隔离子会话（或两次独立 `claude -p`），派正交视角
- 裁决首行标 `模式：同旗舰双隔离`

要跨厂商，就在会话里用 shell 调另一个厂商的 CLI（例如 `codex exec -s read-only`）。

## 3. 派发

**A. 用原生子 Agent**（有 Task / Agent 工具时）

同回合并行起两个子会话，各给正交重心；R2 时把对手 R1 原文整段贴进**另一个新**子会话。
无状态子 Agent 不得在同一上下文里续命，也不得让主持人精分两方。

**B. 用 CLI（跨厂商时必用）**

```bash
claude -p --output-format text < p-A.md > r1-A.out.md
```

要附带额外系统提示（例如团队自己的评审口径）：`--append-system-prompt-file <file>`。
实测单次 30–60s。

## 4. 只读（重点）

Claude Code 常被配置成 `bypassPermissions`，此时**写文件不会有任何提示**。三层防线：

1. 派活单首行写死：「只读：禁止创建/修改/删除任何文件，禁止自动应用修复」
2. 硬开关优先：`--permission-mode plan`，或 `--allowedTools "Read,Grep,Glob"` 关掉 Write/Edit/Bash
3. 收工后主持人自己比对 `git status`（`hosts/windows-cli/run-debate.ps1` 已内置守卫）

## 5. 第二轮

`-p` 是 one-shot：R2 新起进程/新子会话，注入 `[Step 0 基线 + 本方 R1 原文 + 对手 R1 原文]`。

## 6. 常见坑

| 现象 | 原因 / 处理 |
|---|---|
| 问"你有 X skill 吗"得到 "没有" | 模型不查目录直接瞎答，不要当验证依据；看 init 事件 |
| 看不到过程 | `-p` 只回最终文本；要轨迹加 `--output-format stream-json --verbose` |
| 输出过长/跑偏 | 派活单里写死字数上限与四段结构，比事后裁剪有效 |
