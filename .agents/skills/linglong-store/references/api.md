# 玲珑应用商店 Web API 参考

Base URL: https://storeapi.linyaps.org.cn/

## 分类与应用列表

### 获取分类列表（Web 侧）
- GET /web/categories
- Query: lang, arch
- 返回：categoryId, categoryName, icon, categoryCount

curl 模板：

```bash
curl -sS -X GET "https://storeapi.linyaps.org.cn/web/categories?lang=zh&arch=x86_64"
```

### 获取分类列表（App 侧）
- GET /visit/getDisCategoryList
- 返回：categoryId, categoryName, icon, count

### 获取分类下应用数量
- GET /web/getCategoryAppCount
- Query: categoryId

### 搜索/列表
- POST /visit/getSearchAppList
- Body: AppMainVO
- 关键字段：pageNo, pageSize, appId, name, zhName, categoryId, arch, module, version, sort, order, lan

curl 模板：

```bash
curl -sS -X POST "https://storeapi.linyaps.org.cn/visit/getSearchAppList" \
  -H "Content-Type: application/json" \
  -d '{"pageNo":1,"pageSize":20,"name":"WPS","arch":"x86_64","lan":"zh"}'
```

### 版本列表
- POST /visit/getSearchAppVersionList
- Body: AppMainVO（appId 过滤）

curl 模板：

```bash
curl -sS -X POST "https://storeapi.linyaps.org.cn/visit/getSearchAppVersionList" \
  -H "Content-Type: application/json" \
  -d '{"pageNo":1,"pageSize":20,"appId":"cn.wps.wps-office","arch":"x86_64"}'
```

## 应用详情

### 新版详情
- POST /app/getAppDetail
- Body: AppDetailSearchBO[]
- 关键字段：appId, arch, lang

curl 模板：

```bash
curl -sS -X POST "https://storeapi.linyaps.org.cn/app/getAppDetail" \
  -H "Content-Type: application/json" \
  -d '[{"appId":"cn.wps.wps-office","arch":"x86_64","lang":"zh"}]'
```

### 兼容详情
- POST /visit/getAppDetails
- Body: AppDetailsVO[]
- 关键字段：appId, version, channel, module, arch

## 更新检查

- POST /app/appCheckUpdate
- Body: AppCheckVersionBO[]
- 关键字段：appId, arch, version

curl 模板：

```bash
curl -sS -X POST "https://storeapi.linyaps.org.cn/app/appCheckUpdate" \
  -H "Content-Type: application/json" \
  -d '[{"appId":"org.deepin.calculator","arch":"x86_64","version":"5.7.21.3"}]'
```

## 响应解析要点

- 列表类接口提取 `appId`、`name`/`zhName`、`version`、`arch`、`description`、`repoName`。
- 详情接口优先解析 `appId`、`name`、`version`、`arch`、`module`、`runtime`、`screenshots`。
- 更新检查接口重点提取可更新版本号与变更版本。
