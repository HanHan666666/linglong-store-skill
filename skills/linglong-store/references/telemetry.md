# 统计上报与反馈接口

Base URL: https://storeapi.linyaps.org.cn/

## 安装/卸载统计上报

- POST /app/saveInstalledRecord
- 说明：安装与卸载完成后都要调用

执行要点：

- 安装/卸载都必须上报；
- 调用失败时保留请求体与响应体，允许重试。

字段映射

SaveInstalledRecordVO:

- visitorId: 设备指纹
- clientIp: 客户端公网 IP，通过外部服务查询（失败时允许为空）。
- addedItems: 安装记录列表。
- removedItems: 卸载记录列表。

InstalledRecordItem:

- appId: 应用 ID。
- name: 应用名称。
- version: 版本号（安装时可使用用户选择的版本或应用当前版本）。
- arch: 架构。
- module: 模块名称（如有）。
- channel: 通道（如有）。

字段来源建议：

- appId/name/version/arch/module/channel: 来自搜索结果或安装队列中的应用信息。
- visitorId/clientIp: 来自启动时初始化的匿名统计信息。

装配规则：

- 安装完成: addedItems 填 1 个记录，removedItems 为空数组。
- 卸载完成: removedItems 填 1 个记录，addedItems 为空数组。
- 未知字段不传，避免空字符串。

curl 模板：

```bash
curl -sS -X POST "https://storeapi.linyaps.org.cn/app/saveInstalledRecord" \
	-H "Content-Type: application/json" \
	-d '{"visitorId":"<visitorId>","clientIp":"<clientIp>","addedItems":[{"appId":"cn.wps.wps-office","name":"WPS Office","version":"11.1.0.10161","arch":"x86_64"}],"removedItems":[]}'
```

## 访问记录（可选）

- POST /app/saveVisitRecord
- 说明：查看详情或打开商店时上报

## 意见反馈

- POST /web/suggest
- 可选：POST /visit/suggest

curl 模板：

```bash
curl -sS -X POST "https://storeapi.linyaps.org.cn/web/suggest" \
	-H "Content-Type: application/json" \
	-d '{"content":"商店首页加载很慢"}'
```
