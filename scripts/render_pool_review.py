#!/usr/bin/env python3
"""One page to review a whole pool, by field rather than by persona.

Reading 81 persona files is the wrong unit of work. A file answers "what is
this person like", and nobody has that question 81 times. The questions people
actually have are about the pool: is the accent distribution plausible, did the
sampler flatten a field real drivers cluster on, which fields is the prompt
even built from.

So the page is organised by field. Each row carries the tier that decides
whether the field reaches a prompt, whether its values were answered or drawn,
how much it varies, and -- for the fields the survey measures -- the pool's
distribution against the respondents' own. A field the sampler spread evenly
across values that real people cluster on shows up as two visibly different
bars, which is the failure no per-persona review can surface.

The prompts are on the same page, because a reviewer who spots an odd
distribution immediately wants to see what a persona holding it is told to say.

It replaces reports/vn-drivers-profiles.html, which is 3.7 MB of every
dimension from the 1,306-field era and cannot be read for anything.

    uv run python scripts/render_pool_review.py \\
        --pool persona/datasets/vn-drivers-rows \\
        --responses <export.csv> --out reports/vn-drivers-rows-review.html
"""

from __future__ import annotations

import argparse
import collections
import html
import json
import math
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "environment/agents"))
sys.path.insert(0, str(REPO_ROOT / "persona/curation/existing_data/scripts"))

import yaml  # noqa: E402

from matraix.agents.persona.loader import load_persona  # noqa: E402
from matraix.agents.persona.templating import (  # noqa: E402
    PERSONA_SYSTEM_TEMPLATE,
    render_persona_template,
    resolve_persona_template,
)
from matraix.persona_pool import persona_paths  # noqa: E402
from matraix.persona_speech import load_speech_directives  # noqa: E402
from matraix.persona_tiers import stamped_tiers  # noqa: E402

MEASURED_TYPES = {"observed", "direct", "forum_measured"}

#: Sections in the order the prompt renders them, then the tiers that never do.
GROUP_ORDER = [
    ("prompt", "speech", "Đổi văn phong", "Chỉ nhóm này đổi cách câu chữ hiện ra."),
    ("prompt", "stance", "Đổi nội dung",
     "Quyết định nhờ gì và chối gì, không đổi cách nói."),
    ("prompt", "situation", "Đổi hoàn cảnh",
     "Bối cảnh lúc nói: tay bận gì, đi với ai, đường nào."),
    ("prompt", "label", "Prompt, chưa có chỉ thị",
     "Vào prompt dưới dạng nhãn: model phải tự suy ra phải làm gì."),
    ("guard", None, "Guard — không render",
     "Không tới model. Ràng buộc lúc sinh và là thứ R1/R4/R6 đọc để kiểm."),
    ("archive", None, "Archive — không render",
     "Chỉ để truy nguồn. Cắt đi không đổi prompt, nhưng mất khả năng trả lời "
     "\"giá trị này ở đâu ra\"."),
]


def entropy(values: list[Any]) -> tuple[float, str, float]:
    counts = collections.Counter(values)
    n = len(values)
    if not n:
        return 0.0, "", 0.0
    h = -sum((c / n) * math.log2(c / n) for c in counts.values())
    top, top_n = counts.most_common(1)[0]
    return h, str(top), top_n / n


def respondent_table(path: Path) -> list[dict[str, Any]]:
    import csv

    from crosswalks.vn_drivers import CROSSWALK, screen_rows

    rows = screen_rows(list(csv.DictReader(path.open(encoding="utf-8-sig"))))
    out = []
    for row in rows:
        values: dict[str, Any] = {}
        for dim_id, spec in CROSSWALK.items():
            try:
                value = spec["compute"](row)
            except Exception:
                value = None
            if value is not None:
                values[dim_id] = value
        out.append(values)
    return out


def bars(counts: collections.Counter, total: int, palette: str) -> str:
    if not total:
        return '<span class="none">—</span>'
    out = []
    for value, count in counts.most_common():
        share = count / total
        out.append(
            '<div class="bar"><span class="lbl" title="{v}">{v}</span>'
            '<span class="track"><i class="{p}" style="width:{w:.1f}%"></i></span>'
            '<span class="pct">{s:.0f}%</span></div>'.format(
                v=html.escape(str(value)), p=palette, w=share * 100, s=share * 100
            )
        )
    return "".join(out)


def build(pool: Path, responses: Path | None) -> str:
    paths = persona_paths(pool)
    docs = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in paths]
    n = len(docs)
    pack = load_speech_directives()
    respondents = respondent_table(responses) if responses else []

    tiers = stamped_tiers(docs[0]) if docs else {}
    per_field: dict[str, list[Any]] = collections.defaultdict(list)
    measured: collections.Counter = collections.Counter()
    for doc in docs:
        grounding = doc.get("grounding") or {}
        for key, value in (doc.get("dimensions") or {}).items():
            if value is not None:
                per_field[key].append(value)
            entry = grounding.get(key) or {}
            if entry.get("assignment_type") in MEASURED_TYPES:
                measured[key] += 1

    def section_of(key: str) -> str | None:
        if tiers.get(key) != "prompt":
            return None
        return pack.section_of(key) if key in pack.directives else "label"

    rows_html: list[str] = []
    for tier, section, title, blurb in GROUP_ORDER:
        keys = [
            k for k in per_field
            if tiers.get(k) == tier and (section is None or section_of(k) == section)
        ]
        if not keys:
            continue
        keys.sort(key=lambda k: -entropy(per_field[k])[0])
        rows_html.append(
            '<h2>{t} <span class="count">{n} trường</span></h2>'
            '<p class="blurb">{b}</p>'.format(
                t=html.escape(title), n=len(keys), b=html.escape(blurb)
            )
        )
        rows_html.append('<table><thead><tr><th>Trường</th><th>Bằng chứng</th>'
                         '<th>Biến thiên</th><th>Phân bố trong pool</th>'
                         '<th>Người trả lời thật</th></tr></thead><tbody>')
        for key in keys:
            values = per_field[key]
            h, top, top_share = entropy(values)
            m = measured[key]
            ev = (
                f'<b class="ok">{m}</b>/{n} đo được' if m == n
                else (f'<b class="warn">{m}</b>/{n} đo được' if m
                      else '<b class="bad">0</b>/%d — sinh ra' % n)
            )
            real = [r[key] for r in respondents if r.get(key) is not None]
            real_cell = (
                bars(collections.Counter(real), len(real), "real")
                if real else '<span class="none">khảo sát không hỏi</span>'
            )
            flat = "flat" if h < 1.0 else ""
            rows_html.append(
                '<tr class="{flat}"><td><code>{k}</code></td><td>{ev}</td>'
                '<td class="num">H={h:.2f}<br><span class="sub">đỉnh {ts:.0f}%</span></td>'
                '<td>{pool}</td><td>{real}</td></tr>'.format(
                    flat=flat, k=html.escape(key), ev=ev, h=h, ts=top_share * 100,
                    pool=bars(collections.Counter(values), len(values), "pool"),
                    real=real_cell,
                )
            )
        rows_html.append("</tbody></table>")

    prompts: list[str] = []
    for path, doc in zip(paths, docs):
        persona = load_persona(path)
        text = render_persona_template(
            resolve_persona_template(persona, None, PERSONA_SYSTEM_TEMPLATE), persona
        )
        prompts.append(
            "<details><summary><b>{pid}</b> — {name}</summary><pre>{body}</pre>"
            "</details>".format(
                pid=html.escape(str(doc.get("persona_id"))),
                name=html.escape(str(doc.get("display_name"))),
                body=html.escape(text),
            )
        )

    tier_counts = collections.Counter(tiers.get(k) for k in per_field)
    return TEMPLATE.format(
        pool=html.escape(pool.name),
        n=n,
        fields=len(per_field),
        prompt_n=tier_counts.get("prompt", 0),
        guard_n=tier_counts.get("guard", 0),
        archive_n=tier_counts.get("archive", 0),
        respondents=len(respondents),
        body="\n".join(rows_html),
        prompts="\n".join(prompts),
    )


TEMPLATE = """<!doctype html><html lang="vi"><meta charset="utf-8">
<title>Review pool {pool}</title>
<style>
:root{{--fg:#1a1a1a;--mut:#6b7280;--line:#e5e7eb;--pool:#2563eb;--real:#059669;
--bad:#dc2626;--warn:#d97706;--ok:#059669;--flat:#fff7ed}}
body{{font:14px/1.5 ui-sans-serif,system-ui,sans-serif;color:var(--fg);
margin:0;padding:32px;max-width:1240px}}
h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:16px;margin:32px 0 2px}}
.count{{font-weight:400;color:var(--mut);font-size:13px}}
.blurb{{color:var(--mut);margin:0 0 10px;font-size:13px}}
.stats{{color:var(--mut);margin:0 0 8px}}
.stats b{{color:var(--fg)}}
table{{border-collapse:collapse;width:100%;margin-bottom:8px}}
th{{text-align:left;font-size:12px;color:var(--mut);font-weight:600;
border-bottom:1px solid var(--line);padding:6px 8px}}
td{{border-bottom:1px solid var(--line);padding:8px;vertical-align:top}}
td:nth-child(4),td:nth-child(5){{width:26%}}
tr.flat{{background:var(--flat)}}
code{{font:12px ui-monospace,monospace}}
.num{{font-size:12px;white-space:nowrap}} .sub{{color:var(--mut)}}
.bar{{display:flex;align-items:center;gap:6px;margin:1px 0}}
.lbl{{flex:0 0 44%;font-size:11px;overflow:hidden;text-overflow:ellipsis;
white-space:nowrap;color:var(--mut)}}
.track{{flex:1;height:8px;background:var(--line);border-radius:2px;overflow:hidden}}
.track i{{display:block;height:100%}}
i.pool{{background:var(--pool)}} i.real{{background:var(--real)}}
.pct{{flex:0 0 30px;text-align:right;font-size:11px;color:var(--mut)}}
.none{{color:var(--mut);font-size:12px;font-style:italic}}
.bad{{color:var(--bad)}} .warn{{color:var(--warn)}} .ok{{color:var(--ok)}}
details{{border-bottom:1px solid var(--line);padding:6px 0}}
summary{{cursor:pointer;font-size:13px}}
pre{{background:#f9fafb;padding:12px;border-radius:4px;font-size:12px;
white-space:pre-wrap;margin:8px 0 0}}
.legend{{font-size:12px;color:var(--mut);margin:6px 0 0}}
.legend i{{display:inline-block;width:10px;height:10px;border-radius:2px;
vertical-align:-1px;margin-right:3px}}
</style>
<h1>Review pool <code>{pool}</code></h1>
<p class="stats"><b>{n}</b> persona · <b>{fields}</b> trường mỗi persona
({prompt_n} prompt / {guard_n} guard / {archive_n} archive) ·
đối chiếu <b>{respondents}</b> người trả lời thật</p>
<p class="legend"><i class="pool" style="background:#2563eb"></i>pool
&nbsp;<i class="real" style="background:#059669"></i>người thật
&nbsp;· dòng nền cam = H &lt; 1 bit, gần như không phân biệt được persona</p>
{body}
<h2>Prompt thật model nhận được <span class="count">{n} persona</span></h2>
<p class="blurb">Đây là toàn bộ văn bản gửi tới model. Không có trường nào khác
tới được nó.</p>
{prompts}
</html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--responses", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(build(args.pool, args.responses), encoding="utf-8")
    size = args.out.stat().st_size
    print(f"wrote {args.out} ({size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
