# 错误处理与退化策略

## 搜索与列表

- 返回为空：建议更换关键词、减少筛选条件、尝试中文与英文名称。
- 多结果：要求用户选择序号并明确 `appId`。

## 详情

- 详情为空：回退到 `/visit/getAppDetails`。
- 详情字段缺失：提示用户可能是仓库或版本信息缺失，建议调整筛选。

## 安装

- `ll-cli` 不存在：先确认用户是否同意通过 `pkexec bash /home/han/linglong-installer/install-linyaps-env.sh` 安装玲珑环境。
- 环境安装脚本失败：优先根据脚本输出定位是 `pkexec` 授权失败、发行版不支持、仓库/网络异常、包安装失败，还是安装完成后 `ll-cli` 仍不可用。
- 环境安装后仍无 `ll-cli`：按“包未安装成功 / 命令未进入 PATH / 当前 shell 未刷新环境”三个方向给建议。
- `ll-cli` 失败：输出错误摘要并提供重试或更换版本/架构建议；不要提示用户额外加 `sudo`，`ll-cli` 自身会处理 `pkexec` 授权。
- 版本冲突：要求用户指定版本或使用 `--force`。
- 架构冲突：要求用户确认 `arch`。

## 更新检查

- 接口失败：提示用户直接使用 `ll-cli upgrade` 执行更新。
- 结果为空：明确无可更新应用。

## 统计上报

- 上报失败：记录请求与响应，允许重试，不影响主流程结果。

## 反馈

- 反馈失败：提示用户稍后重试或更换接口 `/visit/suggest`。

## 错误映射参考表


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

## 字符串分类映射

当无法获得错误码时，对错误消息进行关键词分类：

| Type | 关键词示例 | 提示 |
| --- | --- | --- |
| ll_cli_missing | command not found, ll-cli, not installed | 当前未检测到玲珑命令，需先安装运行环境 |
| installer_root | root, pkexec, 权限运行, authentication canceled | 安装脚本要求 root 权限，请通过 `pkexec` 重新执行并确认授权弹窗可正常拉起 |
| installer_unsupported_distro | 不支持的发行版, 不支持的 Ubuntu 版本, 不支持的 Debian 版本, 无法将 | 当前系统或版本不在脚本支持列表内，需要手动安装或更换源 |
| installer_nixos | NixOS 不支持自动安装 | 需要按脚本提示修改 NixOS 配置手动启用 linyaps |
| installer_repo | apt update, dnf update, zypper refresh, Release.key, gpg, repo | 仓库添加或刷新失败，优先检查网络、仓库地址和签名密钥 |
| installer_package | apt install, dnf install, pacman, zypper install | 包安装步骤失败，需检查仓库中是否有对应包以及包管理器状态 |
| installer_postcheck | 安装后未检测到 ll-cli 命令 | 安装过程结束但命令不可用，需要检查包是否真正安装成功以及 PATH |
| force_required | ll-cli install, --force | 该版本已安装，需要使用强制安装模式 |
| network | network, connection, timeout, fetch | 网络连接失败，请检查网络设置 |
| not_found | not found, no such, does not exist | 应用不存在或版本不可用 |
| permission | permission, access denied, privilege | 权限不足，请检查系统权限设置 |
| disk_space | disk, space, storage | 磁盘空间不足，请清理后重试 |
| dependency | dependency, runtime, require | 缺少依赖或运行时环境 |
| unknown | 其他 | 原始错误消息 |
