#!/usr/bin/env python3
"""Turn a run's JSONL into one self-contained HTML page a person can read.

The JSONL holds everything -- transcript, tool calls, verdict, self-report --
and is unreadable: 127 objects on 127 lines, each a few thousand characters
wide. Nobody reviews a run that way, so the run's own findings go unread.

This writes one page with no dependencies: open the file, read the
conversations, filter to the failures. It is generated from the JSONL rather
than replacing it -- the JSONL stays the machine-readable copy.

Usage:
    uv run python scripts/build_vita_run_report.py data/vita-golden-2p-128
    uv run python scripts/build_vita_run_report.py <run-dir> -o /tmp/report.html
"""

from __future__ import annotations

import argparse
import html
import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

OUTCOME_LABEL = {
    "resolved": "Đạt",
    "unresolved": "Không đạt",
    "partially_resolved": "Chưa kết luận",
}
OUTCOME_CLASS = {
    "resolved": "ok",
    "unresolved": "bad",
    "partially_resolved": "warn",
}

# Rows the reader wants as a labelled table under each conversation. Anything
# not listed here stays in the JSONL; a page that shows all forty columns is
# as unreadable as the file it replaces.
DETAIL_ROWS = [
    ("expected_decision", "Quyết định kỳ vọng"),
    ("observed_decision", "Quyết định quan sát"),
    ("decision_source", "Nguồn quyết định"),
    ("observed_tools", "Công cụ đã chạy"),
    ("error_type", "Nhóm lỗi"),
    ("input_constraint", "Ràng buộc đầu vào"),
    ("case_integrity", "Toàn vẹn case"),
    ("assistant_mode", "Profile trợ lý"),
    ("vehicle_state", "Trạng thái xe"),
    ("response_latency_seconds", "Tổng thời gian chờ (giây)"),
    ("slowest_turn_seconds", "Lượt chờ lâu nhất (giây)"),
]

PROSE_BLOCKS = [
    ("expected_behavior", "Lẽ ra Vita phải làm gì"),
    ("outcome_reason", "Vì sao chấm như vậy"),
    ("tool_call_report", "Chi tiết công cụ đã gọi"),
    ("process_notes", "Ghi chú chấm"),
    ("feedback_reason", "Người lái nói gì"),
    ("clarifying_notes", "Ghi chú về việc hỏi lại"),
]

STYLE = """
:root {
  --bg: #f6f7f9; --panel: #fff; --line: #e3e6ea; --text: #1c1f23;
  --dim: #6b7280; --ok: #157f4a; --bad: #b3261e; --warn: #9a6700;
  --user: #eef4ff; --bot: #f3f4f6;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #16181c; --panel: #1e2126; --line: #2f343b; --text: #e6e8eb;
    --dim: #9aa3af; --ok: #4ac48a; --bad: #ef6a63; --warn: #d9a441;
    --user: #1d2735; --bot: #24282e;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font: 15px/1.6 -apple-system, "Segoe UI", Roboto, "Noto Sans", sans-serif; }
.wrap { max-width: 1040px; margin: 0 auto; padding: 24px 16px 80px; }
h1 { font-size: 22px; margin: 0 0 4px; }
.sub { color: var(--dim); font-size: 14px; margin-bottom: 20px; }
.legend { color: var(--dim); font-size: 13px; line-height: 1.7; margin: -12px 0 18px;
  border-left: 3px solid var(--line); padding-left: 12px; }
.legend b { color: var(--text); }
.stats { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 18px; }
.stat { background: var(--panel); border: 1px solid var(--line); border-radius: 10px;
  padding: 10px 14px; min-width: 110px; }
.stat b { display: block; font-size: 20px; }
.stat span { color: var(--dim); font-size: 12px; text-transform: uppercase;
  letter-spacing: .04em; }
.controls { position: sticky; top: 0; z-index: 5; background: var(--bg);
  padding: 10px 0; border-bottom: 1px solid var(--line); margin-bottom: 14px;
  display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
select, input { font: inherit; padding: 6px 9px; border-radius: 8px;
  border: 1px solid var(--line); background: var(--panel); color: var(--text); }
input { flex: 1 1 220px; min-width: 180px; }
.count { color: var(--dim); font-size: 13px; }
details.trial { background: var(--panel); border: 1px solid var(--line);
  border-radius: 12px; margin-bottom: 10px; overflow: hidden; }
details.trial > summary { cursor: pointer; padding: 12px 14px; display: flex;
  flex-wrap: wrap; gap: 10px; align-items: baseline; list-style: none; }
details.trial > summary::-webkit-details-marker { display: none; }
details.trial > summary::before { content: "▸"; color: var(--dim); }
details.trial[open] > summary::before { content: "▾"; }
.tag { font-size: 12px; padding: 2px 8px; border-radius: 999px;
  border: 1px solid var(--line); color: var(--dim); }
.tag.ok { color: var(--ok); border-color: currentColor; }
.tag.bad { color: var(--bad); border-color: currentColor; }
.tag.warn { color: var(--warn); border-color: currentColor; }
.who { font-weight: 600; }
.case { font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px; color: var(--dim); }
.gist { flex: 1 1 100%; color: var(--dim); font-size: 13px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.body { padding: 0 14px 16px; border-top: 1px solid var(--line); }
.turn { margin: 12px 0; }
.bub { padding: 10px 13px; border-radius: 12px; max-width: 82%;
  white-space: pre-wrap; overflow-wrap: anywhere; }
.turn.u .bub { background: var(--user); }
.turn.a .bub { background: var(--bot); margin-left: auto; }
.role { font-size: 11px; color: var(--dim); text-transform: uppercase;
  letter-spacing: .05em; margin-bottom: 3px; }
.turn.a .role { text-align: right; }
h3 { font-size: 13px; text-transform: uppercase; letter-spacing: .05em;
  color: var(--dim); margin: 20px 0 6px; }
pre.block { background: var(--bot); border: 1px solid var(--line);
  border-radius: 10px; padding: 11px 13px; margin: 0 0 10px;
  white-space: pre-wrap; overflow-wrap: anywhere; font: inherit; }
pre.block.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 13px; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
td { padding: 5px 0; border-bottom: 1px solid var(--line); vertical-align: top; }
td.k { color: var(--dim); width: 42%; }
.rating { font-size: 18px; font-weight: 600; }
.hidden { display: none; }
"""

SCRIPT = """
const rows = Array.from(document.querySelectorAll('details.trial'));
const outcome = document.getElementById('f-outcome');
const intent = document.getElementById('f-intent');
const persona = document.getElementById('f-persona');
const query = document.getElementById('f-q');
const count = document.getElementById('f-count');
function apply() {
  const q = query.value.trim().toLowerCase();
  let shown = 0;
  for (const row of rows) {
    const ok =
      (!outcome.value || row.dataset.outcome === outcome.value) &&
      (!intent.value || row.dataset.intent === intent.value) &&
      (!persona.value || row.dataset.persona === persona.value) &&
      (!q || row.dataset.search.includes(q));
    row.classList.toggle('hidden', !ok);
    if (ok) shown++;
  }
  count.textContent = shown + ' / ' + rows.length;
}
for (const el of [outcome, intent, persona]) el.addEventListener('change', apply);
query.addEventListener('input', apply);
apply();
"""


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def load_records(run_dir: Path) -> tuple[list[dict[str, Any]], str]:
    matches = sorted(run_dir.glob("*-results.jsonl"))
    if not matches:
        raise SystemExit("no *-results.jsonl in {}".format(run_dir))
    path = matches[0]
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return records, path.name


def turn_html(messages: list[dict[str, Any]]) -> str:
    parts = []
    for message in messages:
        # "customer" / "support" are the transport's words; a reader wants the
        # people they describe.
        is_user = str(message.get("role") or "") == "customer"
        parts.append(
            '<div class="turn {cls}"><div class="role">{who}</div>'
            '<div class="bub">{text}</div></div>'.format(
                cls="u" if is_user else "a",
                who="Người lái" if is_user else "Vita",
                text=esc(message.get("content")),
            )
        )
    return "".join(parts) or '<p class="case">Không có lượt hội thoại nào.</p>'


def detail_table(record: dict[str, Any]) -> str:
    rows = [
        '<tr><td class="k">{}</td><td>{}</td></tr>'.format(esc(label), esc(record[key]))
        for key, label in DETAIL_ROWS
        if record.get(key) not in (None, "")
    ]
    return "<table>{}</table>".format("".join(rows)) if rows else ""


def prose_html(record: dict[str, Any]) -> str:
    parts = []
    for key, label in PROSE_BLOCKS:
        value = str(record.get(key) or "").strip()
        if not value:
            continue
        mono = " mono" if key == "tool_call_report" else ""
        parts.append(
            "<h3>{}</h3><pre class=\"block{}\">{}</pre>".format(esc(label), mono, esc(value))
        )
    return "".join(parts)


def trial_html(record: dict[str, Any]) -> str:
    status = str(record.get("outcome_status") or "")
    rating = record.get("overall_rating")
    opening = str(record.get("opening_message") or "").strip()
    # Everything a reader might type into the filter box, lowercased once here
    # rather than on every keystroke.
    haystack = " ".join(
        str(record.get(key) or "")
        for key in (
            "case_id", "intent_code", "subintent_name", "persona_name", "error_type",
            "opening_message", "outcome_reason", "observed_tools", "feedback_reason",
        )
    ).lower()

    return """
<details class="trial" data-outcome="{outcome}" data-intent="{intent}"
         data-persona="{persona}" data-search="{search}">
  <summary>
    <span class="tag {cls}" title="Bộ chấm so với đáp án trong bộ dữ liệu">{status}</span>
    <span class="who">{persona_name}</span>
    <span class="case">{case_id}</span>
    <span class="tag">{subintent}</span>
    {rating_tag}
    <span class="gist">{gist}</span>
  </summary>
  <div class="body">
    <h3>Hội thoại</h3>
    {turns}
    {details}
    {prose}
  </div>
</details>
""".format(
        outcome=esc(status),
        intent=esc(record.get("intent_code")),
        persona=esc(record.get("persona_name")),
        search=esc(haystack),
        cls=OUTCOME_CLASS.get(status, ""),
        status=esc(OUTCOME_LABEL.get(status, status or "—")),
        persona_name=esc(record.get("persona_name") or record.get("persona_id")),
        case_id=esc(record.get("case_id") or record.get("trial_id")),
        subintent=esc(record.get("subintent_name") or record.get("intent_code")),
        rating_tag=(
            '<span class="tag" title="Persona tự chấm trải nghiệm">người lái {}/10</span>'.format(
                esc(rating)
            )
            if rating not in (None, "")
            else ""
        ),
        gist=esc(opening),
        turns=turn_html(record.get("messages") or []),
        details=detail_table(record),
        prose=prose_html(record),
    )


def options(values: list[str], placeholder: str, labels: dict[str, str] | None = None) -> str:
    """A filter dropdown. ``labels`` renames a code without changing the value
    the filter matches on, so the reader sees "Không đạt" and the script still
    compares against "unresolved"."""
    names = labels or {}
    items = "".join(
        '<option value="{}">{}</option>'.format(esc(value), esc(names.get(value, value)))
        for value in sorted({v for v in values if v})
    )
    return '<option value="">{}</option>{}'.format(esc(placeholder), items)


def rating_of(record: dict[str, Any]) -> int | None:
    value = record.get("overall_rating")
    return int(value) if str(value).strip().isdigit() else None


def disagreements(records: list[dict[str, Any]]) -> tuple[int, int]:
    """Where the two scales part ways.

    ``missed`` is the interesting one: Vita did the wrong thing and the driver
    rated the experience well anyway, which means the fault is invisible from
    inside the car. ``annoyed`` is the mirror -- correct by the dataset, still
    a bad drive.
    """
    missed = annoyed = 0
    for record in records:
        rating = rating_of(record)
        if rating is None:
            continue
        status = record.get("outcome_status")
        if status == "unresolved" and rating >= 7:
            missed += 1
        elif status == "resolved" and rating <= 5:
            annoyed += 1
    return missed, annoyed


def build_page(records: list[dict[str, Any]], run_name: str, source: str) -> str:
    tally = Counter(str(r.get("outcome_status") or "") for r in records)
    ratings = [value for value in map(rating_of, records) if value is not None]
    latencies = [
        float(r["response_latency_seconds"])
        for r in records
        if isinstance(r.get("response_latency_seconds"), (int, float))
    ]

    stats = [("Trial", len(records))]
    for key in ("resolved", "partially_resolved", "unresolved"):
        if tally[key]:
            stats.append((OUTCOME_LABEL[key], tally[key]))
    if ratings:
        stats.append(("Điểm trung bình", "{:.2f}".format(sum(ratings) / len(ratings))))
    if latencies:
        stats.append(("Chờ trung bình", "{:.1f}s".format(sum(latencies) / len(latencies))))
        stats.append(("Chờ lâu nhất", "{:.1f}s".format(max(latencies))))

    missed, annoyed = disagreements(records)
    if missed:
        stats.append(("Sai mà không bị phàn nàn", missed))
    if annoyed:
        stats.append(("Đúng mà vẫn bị chê", annoyed))

    stat_html = "".join(
        '<div class="stat"><b>{}</b><span>{}</span></div>'.format(esc(value), esc(label))
        for label, value in stats
    )

    return """<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{run} — báo cáo lượt chạy Vita</title>
<style>{style}</style></head>
<body><div class="wrap">
<h1>{run}</h1>
<p class="sub">Sinh từ {source}. Mỗi thẻ là một trial: một persona hỏi một case.</p>
<p class="legend">Hai thước đo khác nhau, đọc riêng: <b>Đạt / Không đạt</b> là bộ chấm
so việc Vita làm với đáp án trong bộ dữ liệu — đúng hay sai, không bàn cảm giác.
<b>Người lái x/10</b> là persona tự chấm trải nghiệm. Một case Vita làm đúng
sách vẫn có thể khiến tài xế bực, và ngược lại.</p>
<div class="stats">{stats}</div>
<div class="controls">
  <select id="f-outcome">{outcomes}</select>
  <select id="f-intent">{intents}</select>
  <select id="f-persona">{personas}</select>
  <input id="f-q" type="search" placeholder="Tìm trong câu hỏi, lý do, tên công cụ…">
  <span class="count" id="f-count"></span>
</div>
{trials}
</div><script>{script}</script></body></html>
""".format(
        run=esc(run_name),
        source=esc(source),
        style=STYLE,
        stats=stat_html,
        outcomes=options(list(tally), "Mọi kết quả", OUTCOME_LABEL),
        intents=options([str(r.get("intent_code") or "") for r in records], "Mọi intent"),
        personas=options([str(r.get("persona_name") or "") for r in records], "Mọi persona"),
        trials="".join(trial_html(record) for record in records),
        script=SCRIPT,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path, help="run folder under data/")
    parser.add_argument("-o", "--out", type=Path, help="default: <run-dir>/<run>-report.html")
    args = parser.parse_args()

    records, source = load_records(args.run_dir)
    run_name = args.run_dir.resolve().name
    out = args.out or args.run_dir / "{}-report.html".format(run_name)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_page(records, run_name, source), encoding="utf-8")
    print("wrote {} ({} trials, {:.1f} KB)".format(out, len(records), out.stat().st_size / 1024))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
