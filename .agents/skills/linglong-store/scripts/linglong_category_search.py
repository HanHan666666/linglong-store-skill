#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linglong store category and search helper.

Features:
- List categories (web or app endpoint)
- List apps under a category
- Search apps with optional category filter

Uses curl to keep zero runtime dependencies.
"""

import argparse
import json
import subprocess
import sys
from typing import Any, Dict, List, Optional


BASE_URL = "https://storeapi.linyaps.org.cn"
DEFAULT_ARCH = "x86_64"
DEFAULT_LANG = "zh"
DEFAULT_REPO = "stable"


def run_curl(args: List[str], data: Optional[str] = None) -> Dict[str, Any]:
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


def get_categories(lang: str, arch: str, use_web: bool) -> List[Dict[str, Any]]:
    if use_web:
        url = f"{BASE_URL}/web/categories?lang={lang}&arch={arch}"
        data = run_curl(["-X", "GET", url])
        return data.get("data", []) or []
    url = f"{BASE_URL}/visit/getDisCategoryList"
    data = run_curl(["-X", "GET", url])
    return data.get("data", []) or []


def get_category_app_count(category_id: str) -> int:
    url = f"{BASE_URL}/web/getCategoryAppCount?categoryId={category_id}"
    result = subprocess.run(["curl", "-sS", "-X", "GET", url], capture_output=True, text=True, encoding="utf-8")
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


def search_apps(payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{BASE_URL}/visit/getSearchAppList"
    return run_curl(["-X", "POST", url], data=json.dumps(payload, ensure_ascii=False))


def build_search_payload(args: argparse.Namespace, category_id: Optional[str]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "pageNo": args.page_no,
        "pageSize": args.page_size,
        "arch": args.arch,
        "lan": args.lang,
    }
    if args.repo_name:
        payload["repoName"] = args.repo_name
    if args.name:
        payload["name"] = args.name
    if args.zh_name:
        payload["zhName"] = args.zh_name
    if category_id:
        payload["categoryId"] = category_id
    if args.module:
        payload["module"] = args.module
    if args.version:
        payload["version"] = args.version
    if args.sort:
        payload["sort"] = args.sort
    if args.order:
        payload["order"] = args.order
    return payload


def select_category_id(categories: List[Dict[str, Any]], category_name: Optional[str]) -> Optional[str]:
    if not category_name:
        return None
    matches = [c for c in categories if str(c.get("categoryName", "")).lower() == category_name.lower()]
    if len(matches) == 1:
        return matches[0].get("categoryId")
    if not matches:
        raise RuntimeError(f"category name not found: {category_name}")
    names = ", ".join(str(c.get("categoryName")) for c in matches)
    raise RuntimeError(f"category name ambiguous, matches: {names}")


def format_app_list(items: List[Dict[str, Any]], limit: Optional[int]) -> List[Dict[str, Any]]:
    rows = []
    for item in items[: limit or len(items)]:
        rows.append({
            "appId": item.get("appId"),
            "name": item.get("zhName") or item.get("name"),
            "version": item.get("version"),
            "arch": item.get("arch"),
            "description": item.get("description"),
            "repoName": item.get("repoName"),
        })
    return rows


def extract_app_items(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    data = response.get("data") or {}
    if isinstance(data, dict):
        if "list" in data and isinstance(data.get("list"), list):
            return data.get("list") or []
        if "records" in data and isinstance(data.get("records"), list):
            return data.get("records") or []
    if isinstance(data, list):
        return data
    return []


def cmd_categories(args: argparse.Namespace) -> int:
    categories = get_categories(args.lang, args.arch, args.web)
    if args.raw:
        print(json.dumps(categories, ensure_ascii=False, indent=2))
        return 0
    rows = []
    for item in categories:
        rows.append({
            "categoryId": item.get("categoryId"),
            "categoryName": item.get("categoryName"),
            "count": item.get("categoryCount") or item.get("count"),
        })
    if args.limit:
        rows = rows[: args.limit]
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def cmd_category_apps(args: argparse.Namespace) -> int:
    use_web = resolve_use_web_categories(args)
    categories = get_categories(args.lang, args.arch, use_web)
    category_id = args.category_id or select_category_id(categories, args.category_name)
    if not category_id:
        raise RuntimeError("categoryId is required")
    if args.show_count:
        count = get_category_app_count(category_id)
        print(json.dumps({"categoryId": category_id, "count": count}, ensure_ascii=False, indent=2))
    payload = build_search_payload(args, category_id)
    data = search_apps(payload)
    if args.raw:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    items = extract_app_items(data)
    rows = format_app_list(items, args.limit)
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    category_id = None
    if args.category_id or args.category_name:
        use_web = resolve_use_web_categories(args)
        categories = get_categories(args.lang, args.arch, use_web)
        category_id = args.category_id or select_category_id(categories, args.category_name)
    payload = build_search_payload(args, category_id)
    data = search_apps(payload)
    if args.raw:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    items = extract_app_items(data)
    rows = format_app_list(items, args.limit)
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Linglong store category/search helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--arch", default=DEFAULT_ARCH)
    common.add_argument("--lang", default=DEFAULT_LANG)
    common.add_argument("--repo-name", default=DEFAULT_REPO)
    common.add_argument("--page-no", type=int, default=1)
    common.add_argument("--page-size", type=int, default=20)
    common.add_argument("--limit", type=int, default=10)
    common.add_argument("--raw", action="store_true")

    p_categories = subparsers.add_parser("categories", parents=[common])
    p_categories.add_argument("--web", action="store_true", help="use /web/categories endpoint")
    p_categories.set_defaults(func=cmd_categories)

    p_category_apps = subparsers.add_parser("category-apps", parents=[common])
    p_category_apps.add_argument("--category-id")
    p_category_apps.add_argument("--category-name")
    p_category_apps.add_argument("--show-count", action="store_true")
    p_category_apps.add_argument("--use-web-categories", action="store_true", help="use /web/categories for category lookup")
    p_category_apps.add_argument("--use-app-categories", action="store_true", help="deprecated: app categories are default")
    p_category_apps.add_argument("--name")
    p_category_apps.add_argument("--zh-name")
    p_category_apps.add_argument("--module")
    p_category_apps.add_argument("--version")
    p_category_apps.add_argument("--sort")
    p_category_apps.add_argument("--order")
    p_category_apps.set_defaults(func=cmd_category_apps)

    p_search = subparsers.add_parser("search", parents=[common])
    p_search.add_argument("--name")
    p_search.add_argument("--zh-name")
    p_search.add_argument("--category-id")
    p_search.add_argument("--category-name")
    p_search.add_argument("--use-web-categories", action="store_true", help="use /web/categories for category lookup")
    p_search.add_argument("--use-app-categories", action="store_true", help="deprecated: app categories are default")
    p_search.add_argument("--module")
    p_search.add_argument("--version")
    p_search.add_argument("--sort")
    p_search.add_argument("--order")
    p_search.set_defaults(func=cmd_search)

    return parser


def resolve_use_web_categories(args: argparse.Namespace) -> bool:
    if getattr(args, "use_web_categories", False) and getattr(args, "use_app_categories", False):
        raise RuntimeError("choose only one of --use-web-categories or --use-app-categories")
    if getattr(args, "use_web_categories", False):
        return True
    return False


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
