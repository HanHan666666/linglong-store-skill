# Python API - Linglong Store

This module wraps the store HTTP endpoints with a small Python client that uses
curl (no extra dependencies).

Module path: `scripts/linglong_store_api.py`

## Quick Start

```python
from linglong_store_api import LinglongStoreClient

client = LinglongStoreClient()
results = client.search_apps_simple(name="我的世界", page_size=10)
for item in results:
    print(item.app_id, item.name, item.version)
```

## API Overview

### LinglongStoreClient

```python
client = LinglongStoreClient(
    base_url="https://storeapi.linyaps.org.cn",
    arch="x86_64",
    lang="zh",
    repo_name="stable",
)
```

- `arch` and `repo_name` are required by the backend for search results.
- `lang` maps to the request field `lan`.

#### get_categories(use_web=False)

```python
categories = client.get_categories(use_web=False)
```

Returns a list of category dicts from:
- App endpoint: `/visit/getDisCategoryList` (default)
- Web endpoint: `/web/categories` when `use_web=True`

#### get_category_app_count(category_id)

```python
count = client.get_category_app_count("06")
```

Returns the number of apps in a category (Web endpoint).

#### resolve_category_id(category_id=None, category_name=None, use_web_categories=False)

```python
category_id = client.resolve_category_id(category_name="游戏")
```

Resolves `category_name` to a category id. Raises when ambiguous or not found.

#### search_apps(payload)

```python
payload = client.build_search_payload(page_no=1, page_size=20, name="WPS")
raw = client.search_apps(payload)
```

Sends a POST request to `/visit/getSearchAppList` and returns the raw JSON
response.

#### build_search_payload(...)

```python
payload = client.build_search_payload(
    page_no=1,
    page_size=20,
    name="Minecraft",
    category_id="06",
)
```

Builds a standard request payload with `arch`, `repo_name`, `lan` included.

#### search_apps_simple(...)

```python
apps = client.search_apps_simple(
    name="我的世界",
    category_name="游戏",
    page_size=10,
)
```

Returns a list of `AppSummary` (or raw JSON when `raw=True`).

### search_apps_api (Convenience Function)

```python
from linglong_store_api import search_apps_api

apps = search_apps_api(name="我的世界", page_size=10)
```

A one-shot helper that constructs a client with defaults.

## Data Types

### AppSummary

Fields:
- `app_id`
- `name`
- `version`
- `arch`
- `description`
- `repo_name`

## Error Handling

- Raises `RuntimeError` when curl fails or JSON parsing fails.
- Raises `RuntimeError` when `category_name` is ambiguous or not found.

## Notes

- Search without `arch` and `repo_name` returns empty results.
- For raw responses (paging, total counts), call `search_apps_simple(raw=True)`
  or use `search_apps(payload)` directly.
