# Host recipe — **dsh** (DeepSeek Harness)

适用前提：dsh 里**没有**能指定任意旗舰模型的子 Agent 工具（只有一档轻量 provider），
所以主持人不派子 Agent，而是用 shell 工具驱动两个 CLI 进程。这就是 reference 里的
**Pattern C（CLI ephemeral）变体**。

## 1. 安装

```powershell
Copy-Item -Recurse .\skills\dual-flagship-debate "$env:USERPROFILE\.agents\skills\"
```

dsh 的技能根：`~/.agents/skills`（用户级）与 `<project>/.agents/skills`（项目级）。
frontmatter 只需 `name` + `description`，本 skill 已符合；目录名与 `name` 保持一致。

重启或等技能目录热刷新后，用消息点名即可加载：

```
用 dual-flagship-debate 做一个方案：<决策问题>
```

## 2. 为什么不能让 dsh 自己派辩手

若宿主内置的 provider 只有 `flash` / `mini` 级模型，或子 Agent 工具不允许指定 model，
则按 skill 的 Tier 3 铁律**必须报缺口停止**——不要用轻量模型凑一场辩论，也不要在主控上下文里
精分两方。正确做法：主控当主持人，起外部 CLI。

## 3. 派发

```powershell
# 两个 CLI 各起一个隔离只读会话，并行
powershell -ExecutionPolicy Bypass -File hosts\windows-cli\run-debate.ps1 `
  -TopicFile .\topic.md -Mode cross-vendor -Rounds 2
```

- `-Mode cross-vendor`：辩手 A = Codex CLI，辩手 B = Claude Code（跨厂商）
- `-Mode dual-codex` / `dual-claude`：同旗舰双隔离，裁决首行须标 `模式：同旗舰双隔离`
- dsh 的 shell 工具是同步阻塞的：用后台任务（`run_in_background`）或脚本内 `Start-Process` 并行，
  再等退出。**不要轮询**，等完成事件或阻塞等待。

## 4. 只读

- Codex：`-s read-only`（硬开关，必带）
- Claude Code：无硬只读，需 `--permission-mode plan` 或限制工具白名单 + 事后 `git status` 复核
- 主控在采信任何结论前，自己再看一次工作区 diff

## 5. 事实核验归主持人

辩手引用的文件路径、配置项、指标、外部规则，主持人都要用自己的只读工具验一遍；核不动的标
「未核实前提」，验伪的当场纠偏并写进裁决第 ② 栏。
