# 玲珑应用商店 Agent Skill

基于 `ll-cli` 与玲珑应用商店 Web API 的 Agent Skill，面向自然语言应用管理场景，支持在线搜索、详情查看、安装/卸载、更新检查与升级、意见反馈。

本仓库用于发布一个可复用的技能定义，核心能力位于：`.agents/skills/linglong-store/`。

## 项目目标

让 AI 助手能够在 Linux 桌面环境中完成应用商店常见操作，并保持与 GUI 商店一致的关键行为：

- 在线数据统一走 Web API（不使用 `ll-cli search`）
- 安装/卸载通过 `ll-cli` 执行
- 安装/卸载后进行统计上报
- 更新检查优先使用后端接口
- 失败时提供可执行的退化方案

## 功能范围

- 搜索与发现
- 按关键词、分类、架构、语言、分页查询在线应用
- 查看应用详情、版本与架构
- 安装应用
- 按 `appId` 安装，支持版本/模块/仓库/架构参数
- 支持通过 `.uab` / `.layer` 本地文件安装
- 卸载应用
- 调用 `ll-cli uninstall` 并执行卸载统计上报
- 更新管理
- 基于已安装列表调用 `/app/appCheckUpdate` 检查更新
- 使用 `ll-cli upgrade` 升级单个或全部应用
- 反馈
- 提交用户意见到 `/web/suggest`（可选 `/visit/suggest`）

## 技术约束

- API Base URL：`https://storeapi.linyaps.org.cn/`
- API 无需认证
- 后端接口调用尽量使用 `curl`，保持 0 依赖
- 默认架构 `x86_64`，用户显式指定时覆盖
- 多版本/多架构冲突时，先展示候选并要求用户确认
- 安装失败时输出 `ll-cli` 错误摘要，并引导参考 GUI 商店错误映射逻辑

## 环境要求

- Linux 桌面环境
- `ll-cli` 可用
- `curl` 可用
- Python 3.6+（用于更新检查脚本）

## 使用方式

将 skill 目录复制到你的项目技能目录（示例）：

```bash
mkdir -p <your-project>/.agents/skills
cp -r .agents/skills/linglong-store <your-project>/.agents/skills/
```

然后在支持技能加载的 Agent 环境中，使用自然语言触发相关任务（如“搜索应用”“安装应用”“检查更新”）。

## 关键流程

### 1. 搜索与安装

1. 用户输入关键词
2. 调用 `/visit/getSearchAppList` 获取候选
3. 展示 `名称 + appId + 版本 + 架构 + 描述`
4. 用户确认后执行 `ll-cli install ...`
5. 安装完成后调用 `/app/saveInstalledRecord`

### 2. 检查更新与升级

1. 使用 `ll-cli list` 获取已安装应用
2. 调用 `/app/appCheckUpdate` 检查可更新应用
3. 用户选择升级范围
4. 执行 `ll-cli upgrade` 或 `ll-cli upgrade <appid>`

### 3. 卸载与上报

1. 执行 `ll-cli uninstall <appid>`
2. 调用 `/app/saveInstalledRecord` 上报 `removedItems`

### 4. 反馈

1. 收集反馈文本
2. 调用 `/web/suggest` 提交

## 目录结构

```text
.
├── README.md
├── 需求文档.md
└── .agents
    └── skills
        └── linglong-store
            ├── SKILL.md
            ├── scripts
            │   ├── linglong_category_search.py
            │   └── linglong_update_checker.py
            └── references
                ├── api.md
                ├── cli.md
                ├── category-search.md
                ├── integration.md
                ├── telemetry.md
                ├── errors.md
                ├── update-checker.md
                └── acceptance.md
```

## 快速开始

### 运行更新检查脚本

```bash
python3 .agents/skills/linglong-store/scripts/linglong_update_checker.py --action check
```

### 运行分类/搜索脚本

```bash
python3 .agents/skills/linglong-store/scripts/linglong_category_search.py categories
```

```bash
python3 .agents/skills/linglong-store/scripts/linglong_category_search.py category-apps \
  --category-name "游戏" --page-size 20
```

```bash
python3 .agents/skills/linglong-store/scripts/linglong_category_search.py search \
  --name "WPS" --page-size 10
```

可选动作：

- `--action list`：仅提取已安装应用
- `--action ids`：仅输出可更新应用 ID

### 典型命令

```bash
# 在线搜索（示例）
curl -sS -X POST "https://storeapi.linyaps.org.cn/visit/getSearchAppList" \
  -H "Content-Type: application/json" \
  -d '{"pageNo":1,"pageSize":10,"name":"WPS","arch":"x86_64","lan":"zh"}'

# 安装
ll-cli install cn.wps.wps-office

# 检查更新后升级全部
ll-cli upgrade
```

## 触发词（Skill Metadata）

该技能在以下用户请求下应被触发：

- 搜索应用 / 查找应用
- 安装应用 / 卸载应用
- 检查更新 / 升级应用
- 查看应用详情
- 反馈问题
- 应用商店
- 提及 `ll-cli` 且与安装/更新相关

## 验收标准（摘要）

- 在线搜索与列表始终使用 Web API
- 列表输出必须包含 `appId`
- 安装与卸载完成后都调用统计上报
- 更新检查失败时提供 `ll-cli upgrade` 退化方案
- 错误信息可定位并给出下一步操作建议

## 参考文档

- 需求说明：`需求文档.md`
- 技能定义：`.agents/skills/linglong-store/SKILL.md`
- API 参考：`.agents/skills/linglong-store/references/api.md`
- CLI 参考：`.agents/skills/linglong-store/references/cli.md`
- 集成要点：`.agents/skills/linglong-store/references/integration.md`
- 错误处理：`.agents/skills/linglong-store/references/errors.md`

## License

如需开源发布，请按你的实际选择补充许可证（例如 MIT/Apache-2.0）。
