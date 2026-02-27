---
name: 玲珑应用商店 Agent Skill
description: This skill should be used when the user asks to "搜索应用", "查找应用", "安装应用", "卸载应用", "检查更新", "升级应用", "查看应用详情", "反馈问题", "应用商店" or mentions "ll-cli" with app install/update tasks.
version: 0.1.0
---

# 玲珑应用商店 Agent Skill

## 目的与范围

提供面向玲珑应用商店的完整操作流程与约束，覆盖在线应用搜索、应用详情、安装与升级、更新检查、统计上报与意见反馈。依赖 Web API 获取在线数据，依赖 `ll-cli` 完成安装与升级。

## 使用时机

在用户提出以下需求时触发：

- 搜索、筛选、浏览应用或分类
- 查看应用详情、版本或架构
- 安装、卸载、升级应用
- 检查更新、批量升级
- 提交意见反馈

## 操作原则

- **优先使用 Python 脚本搜索应用**：搜索应用时必须优先调用 `scripts/linglong_store_api.py` 脚本，而非直接调用 curl 或其他方式。
- 默认 `arch` 为 `x86_64`，用户明确指定时再覆盖。
- 多版本、多架构、多模块存在时，先展示并要求用户确认。
- 安装或卸载完成后，调用统计上报接口。
- 安装失败时记录 `ll-cli` 输出摘要，并参考 GUI 商店实现的错误映射或提示逻辑（路径：`/home/han/linglong-store/rust-linglong-store`）。

## 集成实现要点

- 优先读取 GUI 商店对 `/app/saveInstalledRecord` 的字段定义并保持一致。
- 构造请求体时使用最小必要字段起步，再补齐 GUI 商店的扩展字段。
- 统一封装 `curl` 调用，确保输出可解析并保留 HTTP 状态码与响应体。
- `ll-cli` 命令输出需要截取关键失败摘要并保留原始日志用于排障。
- 交互流程中如需展示结果列表，固定输出 `appId` 供用户确认。

## 工作流

### 1) 搜索与发现

**优先使用 Python 脚本进行搜索（推荐）：**

```bash
# 基本搜索
python3 .agents/skills/linglong-store/scripts/linglong_store_api.py <应用名称>

# 指定每页数量
python3 .agents/skills/linglong-store/scripts/linglong_store_api.py <应用名称> --page-size 10

# 输出 JSON 格式（用于程序解析）
python3 .agents/skills/linglong-store/scripts/linglong_store_api.py <应用名称> --json

# 按分类筛选
python3 .agents/skills/linglong-store/scripts/linglong_store_api.py --category "网络应用"

# 指定架构
python3 .agents/skills/linglong-store/scripts/linglong_store_api.py <应用名称> --arch arm64
```

脚本会自动处理 `arch`、`repoName`、`lang` 等必需参数，默认值为 `x86_64`、`stable`、`zh`。

**搜索流程：**

1. 解析用户关键词、分类等条件。
2. 调用 Python 脚本执行搜索。
3. 返回候选列表后，展示：名称、`appId`、版本、架构、描述。
4. 若无结果，提示更换关键词或减少筛选条件。

参考：`references/api.md` 的 `/visit/getSearchAppList`。

### 2) 查看应用详情

- 用户给出 `appId` 或从搜索结果中选择。
- 调用详情接口（优先新版 `/app/getAppDetail`）。
- 返回关键字段：截图、标签、描述、版本、架构、运行时等。

参考：`references/api.md` 的 `/app/getAppDetail`。

### 3) 安装应用

- 先通过搜索接口确认 `appId`，若有多个候选先让用户选择。
- 组装安装命令：
  - 基本安装：`ll-cli install <appid>`
  - 指定版本：`ll-cli install <appid/version>`
  - 指定模块：`ll-cli install <appid> --module=<module>`
  - 指定仓库：`ll-cli install <appid> --repo=<repo>`
  - 强制指定版本：`ll-cli install <appid> --force`
  - 自动确认：`ll-cli install <appid> -y`
  - 文件安装：`ll-cli install <path>.uab` 或 `ll-cli install <path>.layer`
- 执行安装后读取结果摘要，给出成功或失败原因。
- 安装完成后调用安装统计上报。

参考：`references/cli.md` 与 `references/telemetry.md`。

### 4) 更新检查与升级

- 使用 `ll-cli list` 获取已安装应用列表。
- 优先运行脚本 `scripts/linglong_update_checker.py` 完整检查并生成报告。
- 若需自行调用接口，按 `references/api.md` 的 `/app/appCheckUpdate` 组织请求体。
- 列出可更新应用，询问用户升级全部或指定应用。
- 执行升级：`ll-cli upgrade` 或 `ll-cli upgrade <appid>`。

快速示例（仅输出可更新应用ID）：

```bash
python3 .agents/skills/linglong-store/scripts/linglong_update_checker.py --action ids
```

参考：`references/api.md`、`references/cli.md`、`references/update-checker.md`。

### 5) 卸载应用

- 使用 `ll-cli uninstall <appid>`（若需，先确认安装列表）。
- 卸载完成后调用统计上报，字段与 GUI 商店一致。

参考：`references/telemetry.md`。

### 6) 意见反馈

- 直接使用 Web 反馈接口提交用户内容。

参考：`references/telemetry.md`。

## 交互规范

- 明确告知正在执行的步骤（搜索、安装、检查更新）。
- 多选项时引导用户用序号选择，避免模糊确认。
- 失败时给出可执行的下一步（重试、切换架构、减少筛选）。

## 错误处理

- 搜索无结果：建议更换关键词或移除筛选条件。
- 多版本/多架构冲突：要求用户明确选择。
- 安装失败：返回 `ll-cli` 的错误摘要，并提示参考 GUI 商店错误映射逻辑。
- 更新检查失败：提示可直接执行 `ll-cli upgrade` 手动更新。
- 错误码与提示映射参考：`references/errors.md`。

## 自检清单

- 搜索应用时优先使用 `scripts/linglong_store_api.py` Python 脚本。
- 每次安装、卸载后都上报统计记录。
- 安装失败时输出错误摘要并给出替代方案。
- 更新检查接口失败时提供 `ll-cli upgrade` 退化方案。

## 工具脚本

- **`scripts/linglong_store_api.py`** - 应用搜索脚本（推荐优先使用）
  - 用法：`python3 scripts/linglong_store_api.py <应用名称> [--json] [--page-size N]`
  - 自动处理 `arch`、`repoName`、`lang` 等参数，零配置即可搜索
- `scripts/linglong_update_checker.py` - 更新检查脚本
- `scripts/linglong_category_search.py` - 分类搜索脚本

## 附加资源

- [references/api.md](references/api.md)
- [references/cli.md](references/cli.md)
- [references/category-search.md](references/category-search.md)
- [references/telemetry.md](references/telemetry.md)
- [references/update-checker.md](references/update-checker.md)
- [references/integration.md](references/integration.md)
- [references/errors.md](references/errors.md)
- [references/acceptance.md](references/acceptance.md)
