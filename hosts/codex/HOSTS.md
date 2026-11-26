# Host recipe — **Codex CLI**

适用前提：Codex CLI ≥ 0.170，技能根 `~/.codex/skills`，`codex exec` 支持 `-s` / `--ephemeral` / `-o`。

## 1. 安装

```bash
git clone https://github.com/superj0107/dual-flagship-debate.git
cp -r dual-flagship-debate/skills/dual-flagship-debate ~/.codex/skills/
```

触发：在消息里点名 `用 dual-flagship-debate skill：…`。

## 2. 检查可用旗舰

Codex 侧通常只接了一个 provider，也就只有一个旗舰模型。此时按 **Tier 2**：

- 开两个完全隔离的只读会话，派正交视角（一个 Steelman 方案，一个 Pre-Mortem 红队）
- 裁决首行写 `模式：同旗舰双隔离`

要跨厂商，就在 shell 里另起另一个厂商的 CLI（例如 `claude -p`），不要让 Codex 假装是别的模型。

## 3. 派发

```powershell
# R1：两个隔离只读会话，并行
$p1 = Start-Process cmd.exe -PassThru -ArgumentList '/c',
  'codex exec --skip-git-repo-check -s read-only --ephemeral -C . -o r1-A.out.md < p-A.md > a.log 2>&1'
$p2 = Start-Process cmd.exe -PassThru -ArgumentList '/c',
  'codex exec --skip-git-repo-check -s read-only --ephemeral -C . -o r1-B.out.md < p-B.md > b.log 2>&1'
$p1.WaitForExit(); $p2.WaitForExit()
```

- `--ephemeral`：不污染本机会话历史
- `-o <file>`：只落最终答复，干净可读
- `< prompt.md`：走 stdin，避开命令行引号与编码问题

## 4. 只读（必须显式）

`~/.codex/config.toml` 里 `sandbox_mode` 若是 `danger-full-access`（或 `approval_policy = "never"`），
**每一条 `codex exec` 都必须自己加 `-s read-only`**。漏了就是全权限落盘，没有任何提示。

## 5. 第二轮

`--ephemeral` 没有续发原语：R2 新起两个进程，注入
`[Step 0 基线 + 本方 R1 原文 + 对手 R1 原文]`。

## 6. 常见坑

| 现象 | 原因 / 处理 |
|---|---|
| `Not inside a trusted directory` | 加 `--skip-git-repo-check`，或在受信目录里跑 |
| 开头一堆 MCP 报错噪音 | 只看 `-o` 落下的文件内容，忽略 stderr 噪音 |
| 中文乱码 | prompt 文件用 UTF-8 写入，走 stdin 传入 |
| 超时 | 复杂议题给 ≥ 600s；实测简单题单次 10–30s |
