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
import sys
from typing import Any, Dict

from linglong_store_api import (
    DEFAULT_ARCH,
    DEFAULT_LANG,
    DEFAULT_REPO,
    LinglongStoreClient,
    summaries_to_dicts,
)


def cmd_categories(args: argparse.Namespace) -> int:
    client = LinglongStoreClient(arch=args.arch, lang=args.lang, repo_name=args.repo_name)
    categories = client.get_categories(use_web=args.web)
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
    client = LinglongStoreClient(arch=args.arch, lang=args.lang, repo_name=args.repo_name)
    category_id = client.resolve_category_id(
        category_id=args.category_id,
        category_name=args.category_name,
        use_web_categories=use_web,
    )
    if not category_id:
        raise RuntimeError("categoryId is required")
    if args.show_count:
        count = client.get_category_app_count(category_id)
        print(json.dumps({"categoryId": category_id, "count": count}, ensure_ascii=False, indent=2))
    data = client.search_apps_simple(
        name=args.name,
        zh_name=args.zh_name,
        category_id=category_id,
        page_no=args.page_no,
        page_size=args.page_size,
        module=args.module,
        version=args.version,
        sort=args.sort,
        order=args.order,
        raw=args.raw,
    )
    if args.raw:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    rows = summaries_to_dicts(data)
    if args.limit:
        rows = rows[: args.limit]
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    use_web = resolve_use_web_categories(args)
    client = LinglongStoreClient(arch=args.arch, lang=args.lang, repo_name=args.repo_name)
    category_id = None
    if args.category_id or args.category_name:
        category_id = client.resolve_category_id(
            category_id=args.category_id,
            category_name=args.category_name,
            use_web_categories=use_web,
        )
    data = client.search_apps_simple(
        name=args.name,
        zh_name=args.zh_name,
        category_id=category_id,
        page_no=args.page_no,
        page_size=args.page_size,
        module=args.module,
        version=args.version,
        sort=args.sort,
        order=args.order,
        raw=args.raw,
    )
    if args.raw:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    rows = summaries_to_dicts(data)
    if args.limit:
        rows = rows[: args.limit]
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
