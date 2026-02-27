#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linglong store API helper (Python).

Provides a small Python wrapper around the store HTTP endpoints, using curl to
keep runtime dependencies at zero.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


BASE_URL = "https://storeapi.linyaps.org.cn"
DEFAULT_ARCH = "x86_64"
DEFAULT_LANG = "zh"
DEFAULT_REPO = "stable"


@dataclass
class AppSummary:
    app_id: Optional[str]
    name: Optional[str]
    version: Optional[str]
    arch: Optional[str]
    description: Optional[str]
    repo_name: Optional[str]
    icon: Optional[str] = None


@dataclass
class AppDetail:
    app_id: Optional[str]
    name: Optional[str]
    version: Optional[str]
    arch: Optional[str]
    description: Optional[str]
    repo_name: Optional[str]
    icon: Optional[str] = None
    screenshots: List[str] = None
    size: Optional[str] = None
    developer: Optional[str] = None
    category: Optional[str] = None

    def __post_init__(self):
        if self.screenshots is None:
            self.screenshots = []


def _run_curl(args: List[str], data: Optional[str] = None) -> Dict[str, Any]:
    cmd = ["curl", "-sS"] + args
    if data is not None:
        cmd.extend(["-H", "Content-Type: application/json", "-d", data])
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "curl failed")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("failed to parse response as JSON") from exc


def _extract_app_items(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    data = response.get("data") or {}
    if isinstance(data, dict):
        if "list" in data and isinstance(data.get("list"), list):
            return data.get("list") or []
        if "records" in data and isinstance(data.get("records"), list):
            return data.get("records") or []
    if isinstance(data, list):
        return data
    return []


def _format_app_list(items: Iterable[Dict[str, Any]]) -> List[AppSummary]:
    rows: List[AppSummary] = []
    for item in items:
        rows.append(
            AppSummary(
                app_id=item.get("appId"),
                name=item.get("zhName") or item.get("name"),
                version=item.get("version"),
                arch=item.get("arch"),
                description=item.get("description"),
                repo_name=item.get("repoName"),
                icon=item.get("icon"),
            )
        )
    return rows


def summaries_to_dicts(items: Iterable[AppSummary]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in items:
        rows.append(
            {
                "appId": item.app_id,
                "name": item.name,
                "version": item.version,
                "arch": item.arch,
                "description": item.description,
                "repoName": item.repo_name,
            }
        )
    return rows


class LinglongStoreClient:
    def __init__(
        self,
        base_url: str = BASE_URL,
        arch: str = DEFAULT_ARCH,
        lang: str = DEFAULT_LANG,
        repo_name: str = DEFAULT_REPO,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.arch = arch
        self.lang = lang
        self.repo_name = repo_name

    def get_categories(self, use_web: bool = False) -> List[Dict[str, Any]]:
        if use_web:
            url = f"{self.base_url}/web/categories?lang={self.lang}&arch={self.arch}"
            data = _run_curl(["-X", "GET", url])
            return data.get("data", []) or []
        url = f"{self.base_url}/visit/getDisCategoryList"
        data = _run_curl(["-X", "GET", url])
        return data.get("data", []) or []

    def get_category_app_count(self, category_id: str) -> int:
        url = f"{self.base_url}/web/getCategoryAppCount?categoryId={category_id}"
        result = subprocess.run(
            ["curl", "-sS", "-X", "GET", url],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "curl failed")
        try:
            data = json.loads(result.stdout)
            return int(data.get("data", 0) or 0)
        except json.JSONDecodeError:
            raw = result.stdout.strip()
            if raw.isdigit():
                return int(raw)
            raise RuntimeError("failed to parse category count response")

    def search_apps(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/visit/getSearchAppList"
        return _run_curl(["-X", "POST", url], data=json.dumps(payload, ensure_ascii=False))

    def build_search_payload(
        self,
        *,
        page_no: int = 1,
        page_size: int = 20,
        name: Optional[str] = None,
        zh_name: Optional[str] = None,
        category_id: Optional[str] = None,
        module: Optional[str] = None,
        version: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "pageNo": page_no,
            "pageSize": page_size,
            "arch": self.arch,
            "lan": self.lang,
            "repoName": self.repo_name,
        }
        if name:
            payload["name"] = name
        if zh_name:
            payload["zhName"] = zh_name
        if category_id:
            payload["categoryId"] = category_id
        if module:
            payload["module"] = module
        if version:
            payload["version"] = version
        if sort:
            payload["sort"] = sort
        if order:
            payload["order"] = order
        return payload

    def resolve_category_id(
        self,
        *,
        category_id: Optional[str] = None,
        category_name: Optional[str] = None,
        use_web_categories: bool = False,
    ) -> Optional[str]:
        if category_id:
            return category_id
        if not category_name:
            return None
        categories = self.get_categories(use_web=use_web_categories)
        matches = [
            c
            for c in categories
            if str(c.get("categoryName", "")).lower() == category_name.lower()
        ]
        if len(matches) == 1:
            return matches[0].get("categoryId")
        if not matches:
            raise RuntimeError(f"category name not found: {category_name}")
        names = ", ".join(str(c.get("categoryName")) for c in matches)
        raise RuntimeError(f"category name ambiguous, matches: {names}")

    def search_apps_simple(
        self,
        *,
        name: Optional[str] = None,
        zh_name: Optional[str] = None,
        category_id: Optional[str] = None,
        category_name: Optional[str] = None,
        use_web_categories: bool = False,
        page_no: int = 1,
        page_size: int = 20,
        module: Optional[str] = None,
        version: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        raw: bool = False,
    ) -> List[AppSummary] | Dict[str, Any]:
        resolved_category_id = self.resolve_category_id(
            category_id=category_id,
            category_name=category_name,
            use_web_categories=use_web_categories,
        )
        payload = self.build_search_payload(
            page_no=page_no,
            page_size=page_size,
            name=name,
            zh_name=zh_name,
            category_id=resolved_category_id,
            module=module,
            version=version,
            sort=sort,
            order=order,
        )
        data = self.search_apps(payload)
        if raw:
            return data
        items = _extract_app_items(data)
        return _format_app_list(items)

    def get_app_detail(self, app_id: str, raw: bool = False) -> AppDetail | Dict[str, Any]:
        """获取应用详情，包括截图列表"""
        url = f"{self.base_url}/app/getAppDetail"
        # 与 GUI 商店保持一致：不传 lang，避免服务端返回空截图列表。
        payload = [{"appId": app_id, "arch": self.arch}]
        response = _run_curl(["-X", "POST", url], data=json.dumps(payload, ensure_ascii=False))
        if raw:
            return response
        
        data = response.get("data", {})
        app_list = data.get(app_id, [])
        if not app_list:
            raise RuntimeError(f"未找到应用: {app_id}")
        
        app = app_list[0]
        screenshots = []
        for shot in (app.get("appScreenshotList") or []):
            if shot.get("screenshotKey"):
                screenshots.append(shot["screenshotKey"])
        
        return AppDetail(
            app_id=app.get("appId"),
            name=app.get("zhName") or app.get("name"),
            version=app.get("version"),
            arch=app.get("arch"),
            description=app.get("description"),
            repo_name=app.get("repoName"),
            icon=app.get("icon"),
            screenshots=screenshots,
            size=app.get("size"),
            developer=app.get("devName"),
            category=app.get("categoryName"),
        )


def get_app_detail_api(
    app_id: str,
    arch: str = DEFAULT_ARCH,
    lang: str = DEFAULT_LANG,
    raw: bool = False,
) -> AppDetail | Dict[str, Any]:
    """获取应用详情的便捷函数"""
    client = LinglongStoreClient(arch=arch, lang=lang)
    return client.get_app_detail(app_id, raw=raw)


def search_apps_api(
    *,
    name: Optional[str] = None,
    zh_name: Optional[str] = None,
    category_id: Optional[str] = None,
    category_name: Optional[str] = None,
    use_web_categories: bool = False,
    arch: str = DEFAULT_ARCH,
    lang: str = DEFAULT_LANG,
    repo_name: str = DEFAULT_REPO,
    page_no: int = 1,
    page_size: int = 20,
    module: Optional[str] = None,
    version: Optional[str] = None,
    sort: Optional[str] = None,
    order: Optional[str] = None,
    raw: bool = False,
) -> List[AppSummary] | Dict[str, Any]:
    client = LinglongStoreClient(
        arch=arch,
        lang=lang,
        repo_name=repo_name,
    )
    return client.search_apps_simple(
        name=name,
        zh_name=zh_name,
        category_id=category_id,
        category_name=category_name,
        use_web_categories=use_web_categories,
        page_no=page_no,
        page_size=page_size,
        module=module,
        version=version,
        sort=sort,
        order=order,
        raw=raw,
    )


def _main() -> None:
    """命令行入口：python linglong_store_api.py <应用名称> [--arch ARCH] [--repo REPO] [--page-size N] [--json]"""
    import argparse

    parser = argparse.ArgumentParser(
        description="玲珑应用商店搜索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python linglong_store_api.py clash
  python linglong_store_api.py WPS --page-size 10
  python linglong_store_api.py 微信 --json
  python linglong_store_api.py 浏览器 --arch arm64
  python linglong_store_api.py --detail cn.wps.wps-office
  python linglong_store_api.py --detail cn.wps.wps-office --screenshots
        """,
    )
    parser.add_argument("name", nargs="?", help="搜索关键词（应用名称）")
    parser.add_argument("--arch", default=DEFAULT_ARCH, help=f"架构 (默认: {DEFAULT_ARCH})")
    parser.add_argument("--repo", dest="repo_name", default=DEFAULT_REPO, help=f"仓库名 (默认: {DEFAULT_REPO})")
    parser.add_argument("--lang", default=DEFAULT_LANG, help=f"语言 (默认: {DEFAULT_LANG})")
    parser.add_argument("--page-size", type=int, default=20, help="每页数量 (默认: 20)")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON 格式")
    parser.add_argument("--category", dest="category_name", help="分类名称筛选")
    parser.add_argument("--detail", dest="detail_app_id", help="获取应用详情（appId）")
    parser.add_argument("--screenshots", action="store_true", help="仅输出应用截图链接（需配合 --detail 使用）")

    args = parser.parse_args()

    try:
        # 获取应用详情模式
        if args.detail_app_id:
            detail = get_app_detail_api(
                app_id=args.detail_app_id,
                arch=args.arch,
                lang=args.lang,
                raw=args.json,
            )
            
            if args.json:
                if isinstance(detail, dict):
                    print(json.dumps(detail, ensure_ascii=False, indent=2))
                else:
                    print(json.dumps({
                        "appId": detail.app_id,
                        "name": detail.name,
                        "version": detail.version,
                        "arch": detail.arch,
                        "description": detail.description,
                        "icon": detail.icon,
                        "screenshots": detail.screenshots,
                        "size": detail.size,
                        "developer": detail.developer,
                        "category": detail.category,
                    }, ensure_ascii=False, indent=2))
                return
            
            if args.screenshots:
                if detail.screenshots:
                    print(f"{detail.name} 的截图:")
                    for i, url in enumerate(detail.screenshots, 1):
                        print(f"  {i}. {url}")
                else:
                    print("该应用暂无截图")
                return
            
            # 输出完整详情
            print(f"应用ID: {detail.app_id}")
            print(f"名称: {detail.name}")
            print(f"版本: {detail.version}")
            print(f"架构: {detail.arch}")
            print(f"分类: {detail.category}")
            print(f"开发者: {detail.developer}")
            print(f"大小: {detail.size}")
            if detail.icon:
                print(f"图标: {detail.icon}")
            if detail.description:
                print(f"描述: {detail.description}")
            if detail.screenshots:
                print(f"\n截图 ({len(detail.screenshots)} 张):")
                for i, url in enumerate(detail.screenshots, 1):
                    print(f"  {i}. {url}")
            return

        # 搜索模式
        if not args.name and not args.category_name:
            parser.error("请提供搜索关键词或分类名称")

        result = search_apps_api(
            name=args.name,
            category_name=args.category_name,
            arch=args.arch,
            lang=args.lang,
            repo_name=args.repo_name,
            page_size=args.page_size,
            raw=args.json,
        )

        if args.json:
            print(json.dumps(summaries_to_dicts(result) if isinstance(result, list) else result, ensure_ascii=False, indent=2))
        else:
            items = result if isinstance(result, list) else []
            if not items:
                print("未找到匹配的应用")
                return
            print(f"共找到 {len(items)} 个应用:\n")
            for i, app in enumerate(items, 1):
                print(f"{i}. {app.app_id}")
                print(f"   名称: {app.name}")
                print(f"   版本: {app.version}")
                print(f"   架构: {app.arch}")
                if app.icon:
                    print(f"   图标: {app.icon}")
                if app.description:
                    desc = app.description[:80] + "..." if len(app.description) > 80 else app.description
                    print(f"   描述: {desc}")
                print()

    except Exception as e:
        print(f"错误: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
