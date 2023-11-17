# Copyright (c) 2023, tinygears.org
# This code is licensed under MIT license (see LICENSE for details)

import json
import logging
import os.path

from typing import Optional, Any

from platformdirs import user_cache_dir

from aiohttp_client_cache.session import CachedSession
from aiohttp_client_cache.backends import SQLiteBackend

from octopin import __app__

_CACHE_DIR = user_cache_dir(__app__)
_REQUESTS_CACHE_FILE = os.path.join(_CACHE_DIR, "http-cache")

_GH_API_VERSION = "2022-11-28"
_GH_API_URL_ROOT = "https://api.github.com"

_GH_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": _GH_API_VERSION,
}

_GH_TOKEN = os.getenv("GH_TOKEN")
if _GH_TOKEN is not None:
    _GH_HEADERS["Authorization"] = f"Bearer {_GH_TOKEN}"


async def get_default_branch(owner: str, repo: str) -> Optional[str]:
    logging.debug(f"retrieving default branch for repo '{owner}/{repo}'")

    status, content = await async_request(
        "GET", f"{_GH_API_URL_ROOT}/repos/{owner}/{repo}", refresh=True, headers=_GH_HEADERS
    )
    if status == 200:
        return json.loads(content)["default_branch"]
    else:
        return None


async def get_tags(owner: str, repo: str) -> Optional[list[dict[str, Any]]]:
    logging.debug(f"retrieving tags for repo '{owner}/{repo}'")
    return await async_request_paged_json(
        "GET", f"{_GH_API_URL_ROOT}/repos/{owner}/{repo}/tags", refresh=True, headers=_GH_HEADERS
    )


async def get_branches(owner: str, repo: str) -> Optional[list[dict[str, Any]]]:
    logging.debug(f"retrieving tags for repo '{owner}/{repo}'")
    return await async_request_paged_json(
        "GET", f"{_GH_API_URL_ROOT}/repos/{owner}/{repo}/branches", refresh=True, headers=_GH_HEADERS
    )


async def get_content(owner: str, repo: str, ref: str, content_path: str) -> tuple[int, str]:
    url = f"http://raw.githubusercontent.com/{owner}/{repo}/{ref}/{content_path}"
    return await async_request("GET", url)


async def async_request_paged_json(
    method: str,
    url: str,
    refresh: bool = False,
    headers: Optional[dict[str, str]] = None,
    params: Optional[dict[str, str]] = None,
    data: Optional[dict[str, Any]] = None,
) -> list[dict[str, Any]]:
    result = []
    current_page = 1
    while current_page > 0:
        query_params = {"per_page": "100", "page": current_page}
        if params is not None:
            query_params.update(params)

        status, content = await async_request(method, url, refresh, headers, query_params, data)

        if status == 200:
            response: list[dict[str, Any]] = json.loads(content)
            if len(response) == 0:
                current_page = -1
            else:
                for item in response:
                    result.append(item)

                current_page += 1
        else:
            current_page = -1
            logging.error(f"received status '{status}' while accessing '{url}': {content}")

    return result


async def async_request(
    method: str,
    url: str,
    refresh: bool = False,
    headers: Optional[dict[str, str]] = None,
    params: Optional[dict[str, str]] = None,
    data: Optional[str] = None,
) -> tuple[int, str]:
    logging.debug(f"async '{method}' url = {url}, headers = {headers}, params = {params}, data = {data}")

    async with CachedSession(cache=SQLiteBackend(cache_name=_REQUESTS_CACHE_FILE, use_temp=False)) as session:
        async with session.request(
            method, url=url, headers=headers, params=params, data=data, refresh=refresh
        ) as response:
            text = await response.text()
            status = response.status
            logging.debug(f"async '{method}' result = ({status}, {text})")
            return status, text
