---
name: 如何使用codex发起AI对话
description: This document provides a step-by-step guide on how to initiate an AI conversation using Codex. It covers the necessary setup, API usage, and best practices for effective communication with the AI model.
version: 0.1.0
---

# 如何使用 Codex 发起 AI 对话
✅ 方法一：直接把问题当参数（最简单）

如果你只想问一句话，不进交互界面：

codex "帮我分析这个项目的结构"


或：

codex "这个目录里有哪些潜在 bug？"


👉 这种方式会直接返回结果，不进入 TUI。

✅ 方法二：使用 exec（推荐，最稳定）

exec 就是官方提供的“非交互模式”：

codex exec "帮我写一个 Bash 脚本清理日志"


带上下文用：

codex exec "分析当前仓库的依赖问题"


在项目目录里跑，Codex 会自动读代码。

👉 这是最适合脚本/CI/自动化用法。

✅ 方法三：管道输入（stdin）

可以从管道喂给 codex：

echo "帮我解释这个 Makefile" | codex exec


或者：

cat main.c | codex exec "帮我审查这段代码"


👉 适合配合 grep / cat / find 用。

✅ 方法四：禁用全屏 TUI（半交互）

如果你只是讨厌“全屏模式”，想内联：

codex --no-alt-screen


或：

codex --no-alt-screen "帮我看看这个项目"


👉 还是交互，但不会切屏。


✅ 常见组合（实战推荐）
1️⃣ 一次性问问题（最常用）
codex exec "这个仓库的构建流程是啥？"


3️⃣ CI / 脚本自动分析
codex exec "给我生成测试用例" > report.txt

4️⃣ 带图片
codex exec -i error.png "分析这个报错"