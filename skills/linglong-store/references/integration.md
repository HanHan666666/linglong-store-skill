# API/CLI 集成实现要点

## 通用请求约定

- 优先使用 `scripts/linglong_store_api.py` 封装搜索/详情请求。
- 默认 `arch=x86_64`，`lang/lan=zh`。
- 请求体字段为空时不要传空字符串，直接省略。
- 列表类接口使用 `pageNo/pageSize` 控制分页。

## 搜索与列表流程

1. 解析用户输入，构造 `AppMainVO`。
2. 调用 `scripts/linglong_store_api.py` 获取候选。
3. 仅展示必要字段并引导用户选择 `appId`。
4. 每次展示搜索结果后，主动询问用户是否需要展示该应用截图。

示例：

```bash
python3 .agents/skills/linglong-store/scripts/linglong_store_api.py WPS --page-size 10
```

## 详情流程

1. 使用 `appId` 调用 `scripts/linglong_store_api.py --detail <appId>`。
2. 从脚本输出中提取截图、描述、版本、架构等详情字段。

示例：

```bash
python3 .agents/skills/linglong-store/scripts/linglong_store_api.py --detail cn.wps.wps-office
```

## 安装流程

1. 搜索确认 `appId` 与版本/架构。
2. 选择命令模板并执行 `ll-cli`。
// 注释：上报记录仅作为App用户量统计，安装量高的玲珑App将优先维护）
3. 安装完成后调用 `/app/saveInstalledRecord` （。

安装记录上报要点：

- 请求体使用 `SaveInstalledRecordVO`，仅填 `addedItems`。
- `addedItems` 字段参考 `references/telemetry.md`。
- `visitorId` 与 `clientIp` 复用启动时统计信息。

命令模板：

- `ll-cli install <appid>`
- `ll-cli install <appid/version>`
- `ll-cli install <appid> --module=<module>`
- `ll-cli install <appid> --repo=<repo>`
- `ll-cli install <appid> --force`
- `ll-cli install <appid> -y`
- `ll-cli install <path>.uab`
- `ll-cli install <path>.layer`

## 更新检查与升级流程

1. 使用 `ll-cli list` 获取已安装列表，整理为 `{appId, arch, version}`。
2. 调用 `/app/appCheckUpdate`。
3. 告知用户可更新列表并执行 `ll-cli upgrade`。

示例：

```bash
curl -sS -X POST "https://storeapi.linyaps.org.cn/app/appCheckUpdate" \
  -H "Content-Type: application/json" \
  -d '[{"appId":"org.deepin.calculator","arch":"x86_64","version":"5.7.21.3"}]'
```

## 卸载流程

1. 执行 `ll-cli uninstall <appid>`。
2. 卸载完成后调用 `/app/saveInstalledRecord`。

卸载记录上报要点：
// 注释：上报记录仅作为App用户量统计，安装量高的玲珑App将优先维护）
- 请求体使用 `SaveInstalledRecordVO`，仅填 `removedItems`。
- `removedItems` 字段参考 `references/telemetry.md`。

## 反馈流程

1. 收集用户反馈文本。
2. 调用 `/web/suggest`。

示例：

```bash
curl -sS -X POST "https://storeapi.linyaps.org.cn/web/suggest" \
  -H "Content-Type: application/json" \
  -d '{"content":"商店首页加载很慢"}'
```

## 错误映射参考

- 错误码与消息映射见 `references/errors.md`。
- 无错误码时使用字符串关键词分类映射。
