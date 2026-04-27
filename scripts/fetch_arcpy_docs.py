#!/usr/bin/env python3
"""Download ArcPy official docs as Markdown using the official sidebar order.

The script reads ArcGIS Pro's sidebar TOC JavaScript, preserves that hierarchy
as folders, downloads pages concurrently, extracts only the main article body,
and rewrites links that point to pages inside the downloaded dataset.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin
from urllib.request import Request, urlopen


DEFAULT_TOC_URL = "https://pro.arcgis.com/zh-cn/pro-app/3.6/arcpy/main/1520.js"
DEFAULT_ALLOWED_PREFIX = "https://pro.arcgis.com/zh-cn/pro-app/3.6/arcpy/"
DEFAULT_OUTPUT_DIR = Path("arcpy_docs_markdown")
USER_AGENT = "Mozilla/5.0 (compatible; ArcPyDocFetcher/1.0)"


@dataclass
class TocNode:
    node_id: str
    parent: str = ""
    label: str = ""
    url: str = ""
    linkuri: str = ""
    linkurl: str = ""
    children: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PageJob:
    url: str
    title: str
    output_path: Path
    toc_path: tuple[str, ...]
    order: int


@dataclass(frozen=True)
class PageResult:
    url: str
    title: str
    output_path: str
    source_path: tuple[str, ...]
    ok: bool
    error: str = ""


class MainContentExtractor(HTMLParser):
    HEADING_TAGS = {"h2": "##", "h3": "###", "h4": "####", "h5": "#####", "h6": "######"}
    BLOCK_TAGS = {
        "blockquote", "dd", "div", "dl", "dt", "figure", "figcaption",
        "hr", "ol", "p", "section", "table", "tbody", "thead", "tr", "ul",
    }
    SKIP_TAGS = {"script", "style", "noscript", "svg"}

    def __init__(self, page_url: str, link_map: dict[str, Path], output_path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.page_url = page_url
        self.link_map = link_map
        self.output_path = output_path
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self._capture_main = False
        self._main_depth = 0
        self._capture_h1 = False
        self._skip_depth = 0
        self._pre_depth = 0
        self._list_stack: list[str] = []
        self._link_stack: list[str | None] = []

    @property
    def title(self) -> str:
        return normalize_space(" ".join(self.title_parts))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs_dict = {name.lower(): value or "" for name, value in attrs}

        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
            return

        if tag == "h1" and not self._capture_main:
            self._capture_h1 = True
            return

        if tag == "main":
            self._capture_main = True
            self._main_depth = 1
            return

        if not self._capture_main or self._skip_depth:
            return

        self._main_depth += 1
        if tag in self.HEADING_TAGS:
            self._paragraph_break()
            self.parts.append(self.HEADING_TAGS[tag] + " ")
        elif tag == "a":
            href = attrs_dict.get("href")
            markdown_href = self._markdown_link(href) if href else None
            self._link_stack.append(markdown_href)
            if markdown_href:
                self.parts.append("[")
        elif tag in {"ul", "ol"}:
            self._list_stack.append(tag)
            self._paragraph_break()
        elif tag == "li":
            self._paragraph_break()
            indent = "  " * max(len(self._list_stack) - 1, 0)
            self.parts.append(f"{indent}- ")
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "pre":
            self._paragraph_break()
            self._pre_depth += 1
            self.parts.append("```\n")
        elif tag in {"code", "kbd"} and not self._pre_depth:
            self.parts.append("`")
        elif tag in {"th", "td"}:
            self.parts.append(" | ")
        elif tag in self.BLOCK_TAGS:
            self._paragraph_break()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if tag in self.SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return

        if tag == "h1":
            self._capture_h1 = False
            return

        if not self._capture_main or self._skip_depth:
            return

        if tag == "a":
            href = self._link_stack.pop() if self._link_stack else None
            if href:
                self.parts.append(f"]({href})")
        elif tag in self.HEADING_TAGS or tag in self.BLOCK_TAGS or tag == "li":
            self._paragraph_break()
        elif tag in {"ul", "ol"}:
            if self._list_stack:
                self._list_stack.pop()
            self._paragraph_break()
        elif tag == "pre":
            self._pre_depth = max(0, self._pre_depth - 1)
            self.parts.append("\n```\n")
        elif tag in {"code", "kbd"} and not self._pre_depth:
            self.parts.append("`")

        if tag == "main":
            self._capture_main = False
            self._main_depth = 0
        elif self._main_depth:
            self._main_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._capture_h1:
            self.title_parts.append(data)
            return
        if not self._capture_main:
            return
        if self._pre_depth:
            self.parts.append(data)
            return
        text = normalize_space(data)
        if text:
            self.parts.append(text + " ")

    def markdown(self, fallback_title: str) -> str:
        title = self.title or fallback_title
        body = "".join(self.parts)
        body = re.sub(r"[ \t]+\n", "\n", body)
        body = re.sub(r"\n{3,}", "\n\n", body)
        body = body.strip()
        if body:
            return f"# {title}\n\n{body}\n"
        return f"# {title}\n"

    def _paragraph_break(self) -> None:
        if not self.parts:
            return
        if self.parts[-1].endswith("\n\n"):
            return
        if len(self.parts) >= 2 and self.parts[-1] == "\n" and self.parts[-2].endswith("\n"):
            return
        self.parts.append("\n\n")

    def _markdown_link(self, href: str | None) -> str | None:
        if not href:
            return None
        absolute, fragment = urldefrag(urljoin(self.page_url, href))
        normalized = normalize_url(absolute)
        if normalized in self.link_map:
            target = self.link_map[normalized]
            rel = posixpath.relpath(target.as_posix(), self.output_path.parent.as_posix())
            return rel + (f"#{fragment}" if fragment else "")
        if href.startswith("#"):
            return href
        return href


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_url(url: str) -> str:
    clean_url, _fragment = urldefrag(url)
    return clean_url.rstrip("/")


def js_string(value: str) -> str:
    return json.loads(f'"{value}"')


def safe_name(value: str, fallback: str) -> str:
    value = normalize_space(value) or fallback
    value = re.sub(r"[\\/:*?\"<>|#]+", "-", value)
    value = re.sub(r"\s+", " ", value).strip(" .-_")
    return value[:120] or fallback


def fetch_bytes(url: str, timeout: int, retries: int) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(attempt * 1.5, 6))
    assert last_error is not None
    raise last_error


def fetch_text(url: str, timeout: int, retries: int) -> str:
    return fetch_bytes(url, timeout, retries).decode("utf-8", errors="replace")


def parse_toc_js(text: str) -> dict[str, TocNode]:
    nodes: dict[str, TocNode] = {}
    for node_id, body in re.findall(r'treedata\.data\["([^"]+)"\]\s*=\s*\{(.*?)\}\s*(?:,|;)', text, re.S):
        node = TocNode(node_id=node_id)
        for field_name in ("parent", "label", "url", "linkuri", "linkurl"):
            match = re.search(rf'"{field_name}"\s*:\s*"((?:\\.|[^"])*)"', body)
            if match:
                setattr(node, field_name, js_string(match.group(1)))
        children_match = re.search(r'"children"\s*:\s*\[(.*?)\]', body, re.S)
        if children_match:
            node.children = [js_string(item) for item in re.findall(r'"((?:\\.|[^"])*)"', children_match.group(1))]
        nodes[node_id] = node
    return nodes


def discover_toc(root_toc_url: str, timeout: int, retries: int) -> dict[str, TocNode]:
    queue: deque[str] = deque([root_toc_url])
    seen = {root_toc_url}
    all_nodes: dict[str, TocNode] = {}

    while queue:
        toc_url = queue.popleft()
        log(f"[toc] {toc_url}")
        text = fetch_text(toc_url, timeout, retries)
        for node_id, node in parse_toc_js(text).items():
            all_nodes[node_id] = node
            if node.linkurl:
                child_url = normalize_url(urljoin(toc_url, node.linkurl))
                if child_url not in seen:
                    seen.add(child_url)
                    queue.append(child_url)

    return all_nodes


def build_page_jobs(nodes: dict[str, TocNode], output_dir: Path, allowed_prefix: str) -> list[PageJob]:
    jobs: list[PageJob] = []
    seen_urls: set[str] = set()

    def walk_children(child_ids: Iterable[str], current_dir: Path, toc_path: tuple[str, ...]) -> None:
        used_names: dict[str, int] = {}
        for index, child_id in enumerate(child_ids, start=1):
            node = nodes.get(child_id)
            if not node:
                continue
            base = safe_name(node.label, child_id)
            name = f"{index:02d}-{base}"
            count = used_names.get(name, 0) + 1
            used_names[name] = count
            if count > 1:
                name = f"{name}-{count}"

            if node.url:
                url = normalize_url(urljoin(allowed_prefix, node.url))
                if not url.startswith(allowed_prefix) or url in seen_urls:
                    continue
                seen_urls.add(url)
                jobs.append(
                    PageJob(
                        url=url,
                        title=node.label or base,
                        output_path=current_dir / f"{name}.md",
                        toc_path=toc_path + (node.label or base,),
                        order=len(jobs) + 1,
                    )
                )
            elif node.linkuri and f"root_{node.linkuri}" in nodes:
                folder = current_dir / name
                walk_children(nodes[f"root_{node.linkuri}"].children, folder, toc_path + (node.label or base,))
            elif node.children:
                folder = current_dir / name
                walk_children(node.children, folder, toc_path + (node.label or base,))

    root = nodes.get("root") or nodes.get("root_1520")
    if not root:
        raise RuntimeError("Cannot find ArcPy TOC root node.")
    walk_children(root.children, output_dir, ())
    return jobs


def download_page(job: PageJob, link_map: dict[str, Path], timeout: int, retries: int) -> PageResult:
    try:
        html_bytes = fetch_bytes(job.url, timeout, retries)
        parser = MainContentExtractor(job.url, link_map, job.output_path)
        parser.feed(html_bytes.decode("utf-8", errors="replace"))
        markdown = parser.markdown(job.title)
        job.output_path.parent.mkdir(parents=True, exist_ok=True)
        job.output_path.write_text(markdown, encoding="utf-8")
        log(f"[page {job.order}] {job.url}")
        return PageResult(
            url=job.url,
            title=parser.title or job.title,
            output_path=str(job.output_path),
            source_path=job.toc_path,
            ok=True,
        )
    except Exception as exc:  # noqa: BLE001
        log(f"[failed {job.order}] {job.url}: {type(exc).__name__}: {exc}")
        return PageResult(
            url=job.url,
            title=job.title,
            output_path=str(job.output_path),
            source_path=job.toc_path,
            ok=False,
            error=f"{type(exc).__name__}: {exc}",
        )


def write_indexes(output_dir: Path, jobs: list[PageJob], results: list[PageResult]) -> None:
    result_by_url = {result.url: result for result in results}
    lines = ["# ArcPy 官方文档", "", "按 ArcGIS Pro 官方侧边栏顺序保存。", ""]
    for job in jobs:
        result = result_by_url.get(job.url)
        if not result or not result.ok:
            continue
        depth = max(len(job.output_path.relative_to(output_dir).parents) - 1, 0)
        indent = "  " * depth
        rel = job.output_path.relative_to(output_dir).as_posix()
        lines.append(f"{indent}- [{result.title}]({rel})")
    (output_dir / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = {
        "page_count": sum(1 for r in results if r.ok),
        "failed_count": sum(1 for r in results if not r.ok),
        "pages": [
            {
                "url": r.url,
                "title": r.title,
                "path": str(Path(r.output_path).relative_to(output_dir)),
                "toc_path": list(r.source_path),
            }
            for r in results
            if r.ok
        ],
        "failed": [
            {"url": r.url, "title": r.title, "error": r.error}
            for r in results
            if not r.ok
        ],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def log(message: str) -> None:
    print(message, flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toc-url", default=DEFAULT_TOC_URL)
    parser.add_argument("--allowed-prefix", default=DEFAULT_ALLOWED_PREFIX)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--max-pages", type=int, default=None, help="Optional limit for testing.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    allowed_prefix = normalize_url(args.allowed_prefix) + "/"
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes = discover_toc(args.toc_url, args.timeout, args.retries)
    jobs = build_page_jobs(nodes, output_dir, allowed_prefix)
    if args.max_pages is not None:
        jobs = jobs[: args.max_pages]
    link_map = {job.url: job.output_path for job in jobs}
    log(f"Discovered {len(jobs)} pages. Downloading with {args.workers} workers.")

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_to_job = {executor.submit(download_page, job, link_map, args.timeout, args.retries): job for job in jobs}
        pairs = [(future_to_job[future], future.result()) for future in as_completed(future_to_job)]
        pairs.sort(key=lambda pair: pair[0].order)
        results = [result for _job, result in pairs]

    write_indexes(output_dir, jobs, results)
    ok_count = sum(1 for r in results if r.ok)
    failed_count = len(results) - ok_count
    log(f"Done. Saved {ok_count} pages to {output_dir}. Failed: {failed_count}")


if __name__ == "__main__":
    main()
