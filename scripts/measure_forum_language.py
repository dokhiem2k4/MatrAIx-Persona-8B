#!/usr/bin/env python3
"""Measure two dimensions from what OTOFUN members actually wrote.

Both are measured deterministically -- counted, not judged by a model -- so a
reading can be traced back to the strings that produced it.

  self-positioning : which pronoun a member uses for themselves. Vietnamese
                     picks the pair from the speaker's standing relative to the
                     listener, so this is the half of the pair the writer
                     controls.
  verbosity        : median words per post.

Prints the population distributions. It deliberately does NOT emit anything
per-author: the personas are different people, so an individual member's
reading cannot transfer to one of them, only the population shape can.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import statistics
from pathlib import Path

# Vietnamese uses the same word for "you" and for "I" -- which one it is comes
# from the relation, not the token. On this board the convention is settled:
# members address each other as cụ/bác/mợ and name themselves as em/cháu/mình/
# tôi. So "cụ thấy" is second person and cannot be counted as self-reference;
# a first pass that did count it returned 0% neutral, which is what a broken
# measure looks like rather than a finding.
SELF_ONLY = {
    "deferential": ("em", "cháu"),   # casts self below the listener
    "neutral": ("mình", "tôi", "tớ"),  # claims no relative standing
}

# Counted only where the grammar makes the pronoun first person: immediately
# before a verb it governs, or after a noun it possesses ("xe em", "nhà mình").
VERBS = (
    r"(?:thấy|nghĩ|đang|đã|cũng|vừa|mới|xin|có|chưa|không|muốn|dùng|chạy|đi|mua"
    r"|bán|thích|đọc|hỏi|thử|cần|phải|sẽ|từng)"
)
POSSESSED = r"(?:xe|nhà|con|vợ|chồng|bà|ông|công ty|cơ quan|bác)"


def self_positioning(text: str) -> str | None:
    """How the writer names themselves, or None when nothing is marked."""
    counts: dict[str, int] = {}
    for label, pronouns in SELF_ONLY.items():
        total = 0
        for pro in pronouns:
            total += len(re.findall(r"\b{}\s+{}\b".format(pro, VERBS), text, re.I))
            total += len(re.findall(r"\b{}\s+{}\b".format(POSSESSED, pro), text, re.I))
        counts[label] = total
    if not any(counts.values()):
        return None
    return max(counts, key=counts.get)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("posts", type=Path)
    parser.add_argument("--min-posts", type=int, default=3)
    parser.add_argument("--min-chars", type=int, default=400)
    parser.add_argument("-o", "--out", type=Path, required=True)
    args = parser.parse_args()

    by_author: dict[str, list[str]] = collections.defaultdict(list)
    for line in args.posts.open(encoding="utf-8"):
        row = json.loads(line)
        by_author[row["author"]].append(row["text"])

    kept = {
        a: t
        for a, t in by_author.items()
        if len(t) >= args.min_posts and sum(map(len, t)) >= args.min_chars
    }

    positions: collections.Counter[str] = collections.Counter()
    verbosity: list[float] = []
    for texts in kept.values():
        label = self_positioning(" ".join(texts))
        if label:
            positions[label] += 1
        verbosity.append(statistics.median(len(t.split()) for t in texts))

    total_pos = sum(positions.values())
    print("authors crawled            : {}".format(len(by_author)))
    print("authors with enough writing: {}".format(len(kept)))
    print("posts used                 : {}".format(sum(len(t) for t in kept.values())))

    print("\nself-positioning (n={}):".format(total_pos))
    for label, n in positions.most_common():
        print("   {:16s} {:>4}  {:5.1f}%".format(label, n, 100 * n / total_pos))

    quantiles = statistics.quantiles(verbosity, n=5) if len(verbosity) >= 5 else []
    print("\nmedian words per post: min={} p20={} p40={} p60={} p80={} max={}".format(
        int(min(verbosity)), *[int(q) for q in quantiles], int(max(verbosity))
    ) if quantiles else "\nnot enough authors for quantiles")

    # Verbosity bands cut at the population's own quintiles, so the five schema
    # values describe this population rather than an imported yardstick.
    bands = ["Terse", "Concise", "Balanced", "Wordy", "Rambling"]
    counts = collections.Counter()
    for v in verbosity:
        idx = sum(1 for q in quantiles if v > q)
        counts[bands[idx]] += 1
    print("\ncog_verbosity distribution:")
    for b in bands:
        print("   {:10s} {:>4}  {:5.1f}%".format(b, counts[b], 100 * counts[b] / len(verbosity)))

    args.out.write_text(
        json.dumps(
            {
                "source": "otofun.net.vn",
                "authors_crawled": len(by_author),
                "authors_measured": len(kept),
                "posts_used": sum(len(t) for t in kept.values()),
                "self_positioning": dict(positions),
                "verbosity_quintile_cuts": [round(q, 1) for q in quantiles],
                "cog_verbosity": {b: counts[b] for b in bands},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("\nwrote {}".format(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
