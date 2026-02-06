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
