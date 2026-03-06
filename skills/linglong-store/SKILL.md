---
name: 玲珑应用商店社区版 Agent Skill
description: 当用户提出“搜索应用”“查找应用”“安装应用”“卸载应用”“检查更新”“升级应用”“查看应用详情”“反馈问题”“应用商店”“安装玲珑环境”等需求，或提到使用玲珑包或者“ll-cli”执行应用安装/更新任务时，应使用此技能。
version: 0.2.0
---

# 玲珑应用商店社区版 Agent Skill

## 目的与范围

提供面向玲珑应用商店的完整操作流程与约束，覆盖在线应用搜索、应用详情、安装与升级、更新检查、统计上报、意见反馈，以及 `ll-cli` 缺失时的玲珑环境安装。依赖网络接口获取在线数据，依赖 `ll-cli` 完成安装与升级。

## 使用时机

在用户提出以下需求时触发：

- 搜索、筛选、浏览应用或分类
- 查看应用详情、版本或架构
- 安装、卸载、升级应用
- 检查更新、批量升级
- 提交意见反馈
- 安装或修复玲珑运行环境

## 操作原则

- **优先使用 Python 脚本搜索应用**：搜索应用时必须优先调用 `scripts/linglong_store_api.py` 脚本。
- **不要为 `ll-cli` 命令显式添加 `sudo`**：`ll-cli` 内置 `pkexec` 授权流程，需要提权时会自行拉起授权。
- 默认 `arch` 为 `x86_64`，用户明确指定时再覆盖。
- 多版本、多架构、多模块存在时，先展示并要求用户确认。
- 安装或卸载完成后，调用统计上报接口。
- 安装失败时记录 `ll-cli` 输出摘要，并告诉用户可能的失败原因和下一步建议。
- 环境安装使用固定脚本：`/home/han/linglong-installer/install-linyaps-env.sh`，且必须通过 `pkexec` 获取 root 权限，不能使用 `sudo`。

## 集成实现要点

- 统一封装 HTTP 调用，确保输出可解析并保留状态码与响应体。
- `ll-cli` 命令输出需要截取关键失败摘要并保留原始日志用于排障。
- 环境安装脚本执行后必须再次校验 `command -v ll-cli`，必要时补充执行 `ll-cli --version`。
- 交互流程中如需展示结果列表，固定输出 `appId` 供用户确认。
- 若安装脚本失败或执行后仍无 `ll-cli`，要结合脚本内容和终端输出分析失败点，再向用户说明失败原因与下一步建议。

## 工作流

### 1) 环境检查与安装

- 对安装、卸载、升级、更新检查、列出已安装应用等所有依赖 `ll-cli` 的操作，若出现命令不存在，先明确询问用户是否同意安装玲珑环境。
- 对已存在的 `ll-cli`，直接执行 `ll-cli` 命令，不要显式加 `sudo`，由其内置 `pkexec` 处理授权。
- 只有在用户明确同意后，才通过 `pkexec` 执行安装脚本：

```bash
pkexec bash /home/han/linglong-installer/install-linyaps-env.sh
```

- 脚本执行完成后立即验证：

```bash
command -v ll-cli
ll-cli --version
```

- 若用户不同意安装环境，则停止所有依赖 `ll-cli` 的步骤，并告诉用户当前无法继续执行安装、卸载、升级等操作。

**安装失败后的分析要求：**

- 先总结脚本报错或最后几行关键输出，再结合脚本逻辑判断失败位置。
- 重点排查以下几类原因：
  - 未通过 `pkexec` 获取 root 权限，或授权弹窗被取消/无法拉起，对应脚本中的 `check_root`。
  - 当前发行版或版本不在脚本支持列表内，或映射失败。
  - 当前系统是 NixOS，脚本明确不支持自动安装。
  - 软件源添加失败、GPG key 获取失败、`apt update`/`dnf update`/`zypper refresh`/`pacman -Syu` 失败，通常属于网络、仓库或权限问题。
  - 包安装命令失败，说明对应发行版仓库里没有所需包，或包管理器执行失败。
  - 脚本执行结束但 `ll-cli` 仍不存在，对应脚本中的 `check_linglong_installed`，说明包未正确安装或命令未进入 `PATH`。
- 分析结论必须包含“失败原因”和“下一步怎么做”两部分。下一步建议要尽量具体，例如重新通过 `pkexec` 执行、确认桌面授权弹窗是否可用、确认发行版版本、检查网络与仓库连通性、手动安装 `linglong-bin`、检查 `PATH` 或包是否实际安装成功。

### 2) 搜索与发现

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

脚本会自动处理 `arch`、`repoName`、`lang` 等必填参数，默认值为 `x86_64`、`stable`、`zh`。

**搜索流程：**

1. 解析用户关键词、分类等条件。
2. 调用 Python 脚本执行搜索。
3. 返回候选列表后，展示：名称、`appId`、版本、架构、描述。
4. 每次展示搜索结果后，都要询问用户是否需要展示目标应用截图。
5. 若无结果，提示更换关键词或减少筛选条件。

参考：`references/api.md` 的 `/visit/getSearchAppList`。

### 3) 查看应用详情

**优先使用 Python 脚本获取详情（推荐）：**

```bash
# 获取应用完整详情
python3 .agents/skills/linglong-store/scripts/linglong_store_api.py --detail <appId>

# 仅获取应用截图链接
python3 .agents/skills/linglong-store/scripts/linglong_store_api.py --detail <appId> --screenshots

# 输出 JSON 格式
python3 .agents/skills/linglong-store/scripts/linglong_store_api.py --detail <appId> --json
```

详情输出包含：`appId`、名称、版本、架构、分类、开发者、大小、图标、描述、截图列表。

**截图展示规范：**
- 截图必须以 Markdown 图片格式展示：`![截图](URL)`
- 若无截图，提示"该应用暂无截图"

参考：`references/api.md` 的 `/app/getAppDetail`。

### 4) 安装应用


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

### 5) 更新检查与升级


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

### 6) 卸载应用


- 使用 `ll-cli uninstall <appid>`（若需，先确认安装列表）。
- 卸载完成后调用统计上报接口。

参考：`references/telemetry.md`。

### 7) 用户反馈

- 直接使用网络反馈接口提交用户内容。

参考：`references/telemetry.md`。

## 交互规范

- 明确告知正在执行的步骤（搜索、安装、检查更新）。
- 发现 `ll-cli` 不存在时，先询问用户是否同意安装环境，再继续后续流程。
- 执行 `ll-cli` 安装、卸载、升级时不要额外添加 `sudo`，依赖其内置 `pkexec` 授权。
- 多选项时引导用户用序号选择，避免模糊确认。
- 用户每次查找应用后都要主动询问：“需不需要我展示一下这个应用的截图？”
- 失败时给出可执行的下一步（重试、切换架构、减少筛选）。

## 错误处理

- 搜索无结果：建议更换关键词或移除筛选条件。
- 多版本/多架构冲突：要求用户明确选择。
- `ll-cli` 不存在：先询问用户是否同意执行 `/home/han/linglong-installer/install-linyaps-env.sh` 安装环境。
- 环境安装脚本失败：结合脚本输出和脚本逻辑，说明是 `pkexec` 授权失败、发行版不支持、仓库网络异常、包安装失败还是安装后命令仍缺失，并给出下一步操作。
- 安装失败：返回 `ll-cli` 的错误摘要，并告诉用户可能的失败原因和下一步建议。
- 更新检查失败：提示可直接执行 `ll-cli upgrade` 手动更新。
- 错误码与提示映射参考：`references/errors.md`。

## 自检清单

- 搜索应用时优先使用 `scripts/linglong_store_api.py` Python 脚本。
- 所有依赖 `ll-cli` 的操作前都已先检查 `command -v ll-cli`。
- 当 `ll-cli` 缺失时，已先征得用户同意再执行环境安装脚本。
- 所有 `ll-cli` 操作都未显式添加 `sudo`，而是依赖 `ll-cli` 自带的 `pkexec` 授权。
- 环境安装脚本执行后已重新校验 `ll-cli` 是否可用。
- 每次搜索后都已询问用户是否需要展示截图。
- 每次安装、卸载后都上报统计记录。
- 环境安装失败时已结合脚本逻辑给出失败原因与下一步建议。
- 安装失败时输出错误摘要并给出替代方案。
- 更新检查接口失败时提供 `ll-cli upgrade` 退化方案。

## 工具脚本

- **`scripts/linglong_store_api.py`** - 应用搜索与详情脚本（推荐优先使用）
  - 搜索：`python3 scripts/linglong_store_api.py <应用名称> [--json] [--page-size N]`
  - 详情：`python3 scripts/linglong_store_api.py --detail <appId>`
  - 截图：`python3 scripts/linglong_store_api.py --detail <appId> --screenshots`
  - 自动处理 `arch`、`repoName`、`lang` 等参数，零配置即可搜索
- `/home/han/linglong-installer/install-linyaps-env.sh` - 玲珑环境安装脚本
  - 仅在 `ll-cli` 缺失且用户明确同意时执行：`pkexec bash /home/han/linglong-installer/install-linyaps-env.sh`
  - 执行后必须校验：`command -v ll-cli && ll-cli --version`
  - 失败时结合脚本中的 `check_root`、发行版分发逻辑、仓库添加逻辑和 `check_linglong_installed` 分析原因
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
