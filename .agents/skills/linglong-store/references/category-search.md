# 分类与搜索脚本

脚本路径：`scripts/linglong_category_search.py`

Python API 路径：`scripts/linglong_store_api.py`

该脚本对齐 GUI 商店的调用方式：

- 分类默认走 `/visit/getDisCategoryList`。
- 分类应用列表走 `/visit/getSearchAppList`。
- 默认带上 `repoName=stable`（与 GUI 默认一致）。

## 常用用法

### 列出分类（App 侧分类，默认）

```bash
python3 .agents/skills/linglong-store/scripts/linglong_category_search.py categories
```

### 列出分类（Web 侧分类）

```bash
python3 .agents/skills/linglong-store/scripts/linglong_category_search.py categories --web
```

### 按分类名查应用（默认使用 App 侧分类）

```bash
python3 .agents/skills/linglong-store/scripts/linglong_category_search.py category-apps \
  --category-name "游戏" --page-size 20
```

### 按分类 ID 查应用（Web 侧分类 + 手动指定）

```bash
python3 .agents/skills/linglong-store/scripts/linglong_category_search.py category-apps \
  --category-id "06" --use-web-categories --page-size 20
```

### 关键词搜索（可选限定分类）

```bash
python3 .agents/skills/linglong-store/scripts/linglong_category_search.py search \
  --name "WPS" --page-size 10
```

```bash
python3 .agents/skills/linglong-store/scripts/linglong_category_search.py search \
  --name "WPS" --category-name "办公" --page-size 10
```

## Python API 用法

```python
from linglong_store_api import LinglongStoreClient

client = LinglongStoreClient()
apps = client.search_apps_simple(name="我的世界", page_size=10)
for app in apps:
    print(app.app_id, app.name, app.version)
```

完整文档见 [references/python-api.md](python-api.md)。

## 关键参数

- `--repo-name`：仓库名，默认 `stable`。
- `--arch`：架构，默认 `x86_64`。
- `--lang`：语言字段，默认 `zh`（请求体中的 `lan`）。
- `--use-web-categories`：仅影响分类查询来源（Web 侧 `/web/categories`）。

## 排障提示

- 分类能列出但分类下无结果时，优先确认：
  - 分类来源是否与 GUI 一致（默认应使用 App 侧分类）。
  - 是否带上 `repoName`（默认 `stable`）。
