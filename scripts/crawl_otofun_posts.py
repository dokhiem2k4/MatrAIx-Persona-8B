#!/usr/bin/env python3
"""Collect Vietnamese driver writing samples from OTOFUN.

Only what the persona work needs: the pseudonymous handle a post was written
under, and the post text. No profile pages, no signatures, no contact details,
no attachments -- and nothing under a path robots.txt disallows.

Output stays in the scratchpad. The forum's text belongs to the people who
wrote it; only aggregate measurements derived from it go anywhere near the
repo.

Usage:
    python crawl_otofun.py --out otofun_posts.jsonl
"""

from __future__ import annotations

import argparse
import html
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://www.otofun.net.vn"
UA = "Mozilla/5.0 (compatible; MatrAIx persona research; contact: info.khanhnguyenm@gmail.com)"

# Chosen for the dimensions being measured, not for volume: VinFast is the
# marque the assistant under test ships on, the EV room carries attitudes to
# electric cars, repairs carries trust in dealers, road-info carries journey
# language.
FORUMS = [
    ("vinfast", "/forums/vinfast-chevrolet.30/"),
    ("ev", "/forums/o-to-dien-tat-tat-nhung-gi-can-quan-tam.426/"),
    ("repair", "/forums/sua-chua.9/"),
    ("roads", "/forums/hoi-dap-thong-tin-duong-sa-cho-cac-chuyen-di.115/"),
]

# robots.txt Disallow list, honoured explicitly rather than by luck.
DISALLOWED = (
    "/account/", "/attachments/", "/goto/", "/go-to/", "/login/",
    "/lost-password/", "/misc/", "/online/", "/points/", "/register/",
    "/topic-center/", "/admin.php",
)

DELAY_SEC = 2.0


def allowed(path: str) -> bool:
    return not any(path.startswith(p) for p in DISALLOWED)


def fetch(path: str) -> str | None:
    if not allowed(path):
        return None
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None
    finally:
        time.sleep(DELAY_SEC)


THREAD_RE = re.compile(r'href="(/threads/[^"?]+?)"')
POST_SPLIT_RE = re.compile(r'data-content="post-\d+"')
AUTHOR_RE = re.compile(r'data-author="([^"]+)"')
BBWRAPPER_RE = re.compile(r'<div class="bbWrapper">')
QUOTE_RE = re.compile(r"<blockquote.*?</blockquote>", re.S)
TAG_RE = re.compile(r"<[^>]+>")

# Board announcements are staff writing about board policy, not a driver
# talking about driving; measuring them would put a moderator's register into
# the population.
SKIP_SLUG = ("noi-quy", "quy-dinh", "huong-dan", "thong-bao")


def thread_urls(forum_path: str, pages: int) -> list[str]:
    found: list[str] = []
    for page in range(1, pages + 1):
        path = forum_path if page == 1 else "{}page-{}".format(forum_path, page)
        body = fetch(path)
        if not body:
            continue
        for href in THREAD_RE.findall(body):
            href = href.split("page-")[0].rstrip("/") + "/"
            if any(slug in href for slug in SKIP_SLUG):
                continue
            if href not in found:
                found.append(href)
    return found


def posts_from(thread_path: str, pages: int) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for page in range(1, pages + 1):
        path = thread_path if page == 1 else "{}page-{}".format(thread_path, page)
        body = fetch(path)
        if not body:
            break
        found = 0
        for chunk in POST_SPLIT_RE.split(body)[1:]:
            author_match = AUTHOR_RE.search(chunk)
            if not author_match:
                continue
            # js-selectToQuoteEnd closes the post body. Everything after it is
            # the signature block and the reactions bar -- boilerplate the
            # member did not write for this conversation.
            head = chunk.split("js-selectToQuoteEnd", 1)[0]
            start = BBWRAPPER_RE.search(head)
            if not start:
                continue
            # Quoted text is someone else's writing; measuring it would put one
            # person's register on another person's record.
            text = QUOTE_RE.sub(" ", head[start.end():])
            # The cut at js-selectToQuoteEnd can land mid-tag; drop the stub so
            # it does not survive tag-stripping as literal '<div class="'.
            text = re.sub(r"<[^>]*$", "", text)
            text = html.unescape(TAG_RE.sub(" ", text))
            text = " ".join(text.split())
            if len(text) < 25:
                continue
            out.append((author_match.group(1), text))
            found += 1
        if not found:
            break
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--forum-pages", type=int, default=3)
    parser.add_argument("--thread-pages", type=int, default=3)
    parser.add_argument("--max-threads-per-forum", type=int, default=18)
    args = parser.parse_args()

    seen_threads: set[str] = set()
    written = 0
    with args.out.open("w", encoding="utf-8") as handle:
        for label, forum_path in FORUMS:
            threads = thread_urls(forum_path, args.forum_pages)
            threads = [t for t in threads if t not in seen_threads]
            seen_threads.update(threads)
            threads = threads[: args.max_threads_per_forum]
            print("{:8s} {} threads".format(label, len(threads)), flush=True)
            for i, thread in enumerate(threads, 1):
                rows = posts_from(thread, args.thread_pages)
                for author, text in rows:
                    handle.write(
                        json.dumps(
                            {
                                "forum": label,
                                "thread": thread,
                                "author": author,
                                "text": text,
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                written += len(rows)
                print(
                    "  [{:8s} {:>2}/{:<2}] {:>3} posts  total={}".format(
                        label, i, len(threads), len(rows), written
                    ),
                    flush=True,
                )
    print("wrote {} posts to {}".format(written, args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
