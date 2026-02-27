# 错误处理与退化策略

## 搜索与列表

- 返回为空：建议更换关键词、减少筛选条件、尝试中文与英文名称。
- 多结果：要求用户选择序号并明确 `appId`。

## 详情

- 详情为空：回退到 `/visit/getAppDetails`。
- 详情字段缺失：提示用户可能是仓库或版本信息缺失，建议调整筛选。

## 安装

- `ll-cli` 失败：输出错误摘要并提供重试或更换版本/架构建议。
- 版本冲突：要求用户指定版本或使用 `--force`。
- 架构冲突：要求用户确认 `arch`。

## 更新检查

- 接口失败：提示用户直接使用 `ll-cli upgrade` 执行更新。
- 结果为空：明确无可更新应用。

## 统计上报

- 上报失败：记录请求与响应，允许重试，不影响主流程结果。

## 反馈

- 反馈失败：提示用户稍后重试或更换接口 `/visit/suggest`。

## GUI 商店错误映射参考表

来源：GUI 商店安装错误码映射。

错误码表：

| Code | Name | Message |
| --- | --- | --- |
| -2 | ProgressTimeout | 进度超时 |
| -1 | Failed | 通用失败 |
| 0 | Success | 成功 |
| 1 | Cancelled | 操作已取消 |
| 1000 | Unknown | 未知错误 |
| 1001 | AppNotFoundFromRemote | 远程仓库找不到应用 |
| 1002 | AppNotFoundFromLocal | 本地找不到应用 |
| 2001 | AppInstallFailed | 安装失败 |
| 2002 | AppInstallNotFoundFromRemote | 远程无该应用 |
| 2003 | AppInstallAlreadyInstalled | 已安装同版本 |
| 2004 | AppInstallNeedDowngrade | 需要降级安装 |
| 2005 | AppInstallModuleNoVersion | 安装模块时不允许指定版本 |
| 2006 | AppInstallModuleRequireAppFirst | 安装模块需先安装应用 |
| 2007 | AppInstallModuleAlreadyExists | 模块已存在 |
| 2008 | AppInstallArchNotMatch | 架构不匹配 |
| 2009 | AppInstallModuleNotFound | 远程无该模块 |
| 2010 | AppInstallErofsNotFound | 缺少 erofs 解压命令 |
| 2011 | AppInstallUnsupportedFileFormat | 不支持的文件格式 |
| 2101 | AppUninstallFailed | 卸载失败 |
| 2102 | AppUninstallNotFoundFromLocal | 本地无该应用 |
| 2103 | AppUninstallAppIsRunning | 应用正在运行 |
| 2104 | LayerCompatibilityError | 找不到兼容 layer |
| 2105 | AppUninstallMultipleVersions | 存在多版本 |
| 2106 | AppUninstallBaseOrRuntime | base/runtime 不允许卸载 |
| 2201 | AppUpgradeFailed | 升级失败 |
| 2202 | AppUpgradeLocalNotFound | 本地无可升级应用 |
| 3001 | NetworkError | 网络错误 |
| 4001 | InvalidFuzzyReference | 无效引用 |
| 4002 | UnknownArchitecture | 未知架构 |

## GUI 商店字符串分类映射

当无法获得错误码时，GUI 商店对错误消息进行关键词分类：

| Type | 关键词示例 | 提示 |
| --- | --- | --- |
| force_required | ll-cli install, --force | 该版本已安装，需要使用强制安装模式 |
| network | network, connection, timeout, fetch | 网络连接失败，请检查网络设置 |
| not_found | not found, no such, does not exist | 应用不存在或版本不可用 |
| permission | permission, access denied, privilege | 权限不足，请检查系统权限设置 |
| disk_space | disk, space, storage | 磁盘空间不足，请清理后重试 |
| dependency | dependency, runtime, require | 缺少依赖或运行时环境 |
| unknown | 其他 | 原始错误消息 |
