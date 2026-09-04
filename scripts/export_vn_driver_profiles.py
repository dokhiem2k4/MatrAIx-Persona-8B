#!/usr/bin/env python3
"""Export every persona in a grounded pool as one self-contained HTML dossier.

Two things the UI cannot show at a glance and this can:

* Provenance per dimension. A persona carries ~1,291 values but only ~24 of
  them are answers a person gave; the rest are sampled from the synthesis
  graph. The dossier keeps them in separate sections so a reader never has to
  guess which is which.
* How alike the personas are. A pool built by pinning ~24 measured dimensions
  and sampling the other ~1,266 from one shared graph can look diverse
  persona-by-persona while being repetitive in aggregate. The overlap section
  reports the pairwise agreement rate so that is visible rather than assumed.

Reads the Vietnamese label pack when present, so the dossier is readable by
the people who ran the survey.

Usage:
    uv run python scripts/export_vn_driver_profiles.py persona/datasets/vn-drivers
"""

from __future__ import annotations

import argparse
import collections
import glob
import html
import itertools
import json
import statistics
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LABELS_VI = REPO_ROOT / "persona/schema/labels/dimensions.labels.vi.json"
LOCALE_DIR = Path(__file__).resolve().parent / "locales"


def load_strings(locale: str) -> dict[str, str]:
    """Display strings for the report.

    They live in scripts/locales/ rather than in this file so the generator
    holds no localised text of its own -- the same split the web UI uses
    between code and its message packs.
    """
    path = LOCALE_DIR / "persona_profiles.{}.json".format(locale)
    if not path.is_file():
        raise SystemExit("no string pack for locale {!r} ({})".format(locale, path))
    return json.loads(path.read_text(encoding="utf-8"))

#: Shown at the top of each persona, in this order, when present.
CARD_KEYS = ("age_bracket", "gender_identity", "vn_locality", "domain", "life_stage", "intent")

SCOREABLE = {"observed", "direct", "forum_measured"}


def load_labels() -> tuple[dict, dict]:
    if not LABELS_VI.is_file():
        return {}, {}
    pack = json.loads(LABELS_VI.read_text(encoding="utf-8")).get("dimensions", {})
    dim = {k: v.get("label") for k, v in pack.items() if v.get("label")}
    val = {k: (v.get("values") or {}) for k, v in pack.items()}
    return dim, val


def load_personas(pool: Path) -> list[dict]:
    out = []
    for path in sorted(pool.glob("persona_*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        out.append(
            {
                "id": raw.get("persona_id") or path.stem,
                "name": raw.get("display_name") or "",
                "source": raw.get("source") or "",
                "sources": raw.get("sources") or {},
                "dims": raw.get("dimensions") or {},
                "grounding": raw.get("grounding") or {},
                "summary": raw.get("grounding_summary") or {},
                "file": path.name,
            }
        )
    return out


def overlap_report(personas: list[dict]) -> dict:
    keys = sorted(set().union(*[set(p["dims"]) for p in personas]))
    observed = sorted(
        set().union(
            *[
                {k for k, v in p["grounding"].items() if v.get("assignment_type") in SCOREABLE}
                for p in personas
            ]
        )
    )
    obs_set = set(observed)
    generated = [k for k in keys if k not in obs_set]

    def pairwise(ks: list[str]) -> tuple[list[float], list[tuple]]:
        rates, pairs = [], []
        for a, b in itertools.combinations(personas, 2):
            if not ks:
                continue
            same = sum(1 for k in ks if a["dims"].get(k) == b["dims"].get(k))
            rate = same / len(ks)
            rates.append(rate)
            pairs.append((rate, a["name"], b["name"]))
        return rates, pairs

    all_rates, all_pairs = pairwise(keys)
    obs_rates, _ = pairwise(observed)
    gen_rates, _ = pairwise(generated)

    constant = [k for k in keys if len({p["dims"].get(k) for p in personas}) == 1]
    signatures = collections.Counter(tuple(p["dims"].get(k) for k in keys) for p in personas)
    exact_dupes = sum(c - 1 for c in signatures.values() if c > 1)

    # Per-observed-dimension spread: a dimension where 40 of 42 share one value
    # adds little separation no matter how many personas carry it.
    spread = []
    for k in observed:
        counts = collections.Counter(p["dims"].get(k) for p in personas)
        top_value, top_count = counts.most_common(1)[0]
        spread.append((top_count / len(personas), k, top_value, len(counts)))
    spread.sort(reverse=True)

    def stats(rates: list[float]) -> dict:
        if not rates:
            return {"mean": 0.0, "min": 0.0, "max": 0.0}
        return {"mean": statistics.mean(rates), "min": min(rates), "max": max(rates)}

    return {
        "dimension_count": len(keys),
        "observed_keys": observed,
        "generated_count": len(generated),
        "all": stats(all_rates),
        "observed": stats(obs_rates),
        "generated": stats(gen_rates),
        "constant": constant,
        "exact_dupes": exact_dupes,
        "top_pairs": sorted(all_pairs, reverse=True)[:8],
        "spread": spread,
        "pair_count": len(all_rates),
    }


def esc(text) -> str:
    return html.escape(str(text if text is not None else ""))


def build_html(
    pool: Path, personas: list[dict], rep: dict, manifest: dict, locale: str = "vi"
) -> str:
    strings = load_strings(locale)
    dim_label, val_label = load_labels()

    def t(key: str, **kw) -> str:
        return strings[key].format(**kw) if kw else strings[key]

    def lab(key: str) -> str:
        return dim_label.get(key, key.replace("_", " "))

    def val(key: str, value) -> str:
        return (val_label.get(key) or {}).get(str(value), str(value))

    pct = lambda x: "{:.1f}%".format(x * 100)  # noqa: E731
    parts: list[str] = []
    a = parts.append

    a("<!doctype html><html lang='{}'><head><meta charset='utf-8'>".format(esc(locale)))
    a("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    a("<title>{}</title>".format(esc(t("pageTitle", pool=pool.name))))
    a("""<style>
:root{--bg:#fbfbfd;--fg:#16181d;--dim:#6b7280;--line:#e3e5ea;--card:#fff;
      --obs:#0f766e;--obsbg:#ecfdf5;--gen:#7c3aed;--genbg:#f5f3ff;--warn:#b45309;--warnbg:#fffbeb}
@media(prefers-color-scheme:dark){:root{--bg:#0f1115;--fg:#e8eaee;--dim:#9aa2af;--line:#262a33;
      --card:#161920;--obs:#5eead4;--obsbg:#0b201c;--gen:#c4b5fd;--genbg:#1a1430;--warn:#fbbf24;--warnbg:#241a06}}
*{box-sizing:border-box}
body{margin:0;padding:2rem 1.25rem 5rem;background:var(--bg);color:var(--fg);
     font:15px/1.6 ui-sans-serif,system-ui,"Segoe UI",Roboto,"Helvetica Neue",sans-serif}
.wrap{max-width:1080px;margin:0 auto}
h1{font-size:1.7rem;margin:0 0 .3rem} h2{font-size:1.2rem;margin:2.5rem 0 .8rem;
   padding-bottom:.4rem;border-bottom:1px solid var(--line)}
h3{font-size:1rem;margin:1.4rem 0 .5rem}
.sub{color:var(--dim);margin:0 0 1.5rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:1.1rem 1.25rem;margin:1rem 0}
table{width:100%;border-collapse:collapse;font-size:13.5px}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
th,td{text-align:left;padding:.42rem .6rem;border-bottom:1px solid var(--line);vertical-align:top}
th{font-weight:600;color:var(--dim);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.tag{display:inline-block;padding:.08rem .45rem;border-radius:99px;font-size:11.5px;font-weight:600}
.obs{background:var(--obsbg);color:var(--obs)} .gen{background:var(--genbg);color:var(--gen)}
.note{background:var(--warnbg);border-left:3px solid var(--warn);padding:.8rem 1rem;border-radius:0 8px 8px 0;margin:1rem 0}
.note b{color:var(--warn)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:.15rem .9rem;font-size:12.5px}
.grid div{padding:.16rem 0;border-bottom:1px solid var(--line);min-width:0}
.grid span{color:var(--dim)}
.kpi{display:flex;flex-wrap:wrap;gap:1.6rem;margin:.6rem 0}
.kpi div{min-width:110px} .kpi b{display:block;font-size:1.55rem;line-height:1.2}
.kpi span{color:var(--dim);font-size:12.5px}
details{margin-top:.7rem} summary{cursor:pointer;color:var(--dim);font-size:13px;padding:.3rem 0}
code{font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim)}
.person{scroll-margin-top:1rem}
.who{display:flex;flex-wrap:wrap;gap:.4rem .9rem;align-items:baseline;margin-bottom:.5rem}
.who h3{margin:0;font-size:1.15rem}
</style></head><body><div class='wrap'>""")

    a("<h1>{}</h1>".format(esc(t("heading", pool=pool.name))))
    a("<p class='sub'>{}</p>".format(esc(t(
        "subtitle",
        personas=len(personas),
        dimensions=rep["dimension_count"],
        sources=", ".join(manifest.get("grounding", {}).get("sources", [])),
    ))))

    # ---- what is measured vs invented -------------------------------------
    g = manifest.get("grounding", {})
    by = g.get("byAssignmentType", {})
    a("<div class='card'><div class='kpi'>")
    a("<div><b>{}</b><span>{}</span></div>".format(len(personas), esc(t("kpiPersonas"))))
    a("<div><b>{}</b><span>{}</span></div>".format(g.get("scoreableMean", "-"), esc(t("kpiMeasuredPer"))))
    a("<div><b>{}</b><span>{}</span></div>".format(by.get("observed", "-"), esc(t("kpiObservedValues"))))
    a("<div><b>{}</b><span>{}</span></div>".format(by.get("generated", "-"), esc(t("kpiGeneratedValues"))))
    a("</div>")
    a("<p class='sub' style='margin:0'>{}</p></div>".format(t(
        "measuredVsGenerated",
        dimensions=rep["dimension_count"],
        scoreable=g.get("scoreableMean", "~24"),
    )))

    pairing = manifest.get("pairing") or {}
    if pairing.get("caveat"):
        a("<div class='note'><b>{}</b> {} {}</div>".format(
            esc(t("pairingWarnTitle")), esc(pairing["caveat"]), t("pairingWarnBody")))
    a("<div class='note'><b>{}</b> {}</div>".format(
        esc(t("localityWarnTitle")), esc(t("localityWarnBody"))))

    # ---- overlap ----------------------------------------------------------
    a("<h2>{}</h2>".format(esc(t("overlapHeading"))))
    a("<p class='sub'>{}</p>".format(t("overlapIntro", pairs=rep["pair_count"])))
    a("<div class='scroll'><table><thead><tr><th>{}</th><th class='num'>{}</th>"
      "<th class='num'>{}</th><th class='num'>{}</th><th class='num'>{}</th></tr></thead><tbody>".format(
          esc(t("colScope")), esc(t("colDimensionCount")), esc(t("colMeanOverlap")),
          esc(t("colMin")), esc(t("colMax"))))
    for label, key, count in (
        (t("scopeAll"), "all", rep["dimension_count"]),
        (t("scopeObserved"), "observed", len(rep["observed_keys"])),
        (t("scopeGenerated"), "generated", rep["generated_count"]),
    ):
        st = rep[key]
        a("<tr><td>{}</td><td class='num'>{}</td><td class='num'><b>{}</b></td>"
          "<td class='num'>{}</td><td class='num'>{}</td></tr>".format(
              esc(label), count, pct(st["mean"]), pct(st["min"]), pct(st["max"])))
    a("</tbody></table></div>")

    a("<div class='kpi' style='margin-top:1rem'>")
    a("<div><b>{}</b><span>{}</span></div>".format(rep["exact_dupes"], esc(t("kpiExactDupes"))))
    a("<div><b>{}</b><span>{}</span></div>".format(
        len(rep["constant"]), esc(t("kpiConstantDims", personas=len(personas)))))
    a("</div>")

    a("<h3>{}</h3><div class='scroll'><table><thead><tr><th>{}</th>"
      "<th class='num'>{}</th></tr></thead><tbody>".format(
          esc(t("topPairsHeading")), esc(t("colPair")), esc(t("colOverlap"))))
    for rate, n1, n2 in rep["top_pairs"]:
        a("<tr><td>{} &nbsp;·&nbsp; {}</td><td class='num'>{}</td></tr>".format(esc(n1), esc(n2), pct(rate)))
    a("</tbody></table></div>")

    a("<h3>{}</h3>".format(esc(t("spreadHeading"))))
    a("<p class='sub'>{}</p>".format(esc(t("spreadIntro"))))
    a("<div class='scroll'><table><thead><tr><th>{}</th><th>{}</th>"
      "<th class='num'>{}</th><th class='num'>{}</th></tr></thead><tbody>".format(
          esc(t("colDimension")), esc(t("colDominantValue")),
          esc(t("colShare")), esc(t("colDistinctValues"))))
    for share, key, top, distinct in rep["spread"]:
        a("<tr><td>{}<br><code>{}</code></td><td>{}</td><td class='num'>{}</td>"
          "<td class='num'>{}</td></tr>".format(
              esc(lab(key)), esc(key), esc(val(key, top)), pct(share), distinct))
    a("</tbody></table></div>")

    if rep["constant"]:
        a("<details><summary>{}</summary><div class='grid'>".format(
            esc(t("constantDimsSummary", count=len(rep["constant"])))))
        for k in rep["constant"]:
            a("<div>{} <span>= {}</span></div>".format(esc(lab(k)), esc(val(k, personas[0]["dims"].get(k)))))
        a("</div></details>")

    # ---- roster -----------------------------------------------------------
    a("<h2>{}</h2><div class='scroll'><table><thead><tr>".format(
        esc(t("rosterHeading", personas=len(personas)))))
    a("<th>{}</th><th>{}</th><th>{}</th>".format(
        esc(t("colIndex")), esc(t("colName")), esc(t("colId"))))
    for k in CARD_KEYS:
        a("<th>{}</th>".format(esc(lab(k))))
    a("<th class='num'>{}</th></tr></thead><tbody>".format(esc(t("colMeasured"))))
    for i, p in enumerate(personas, 1):
        a("<tr><td class='num'>{}</td><td><a href='#{}'>{}</a></td><td><code>{}</code></td>".format(
            i, esc(p["id"]), esc(p["name"]), esc(p["id"])))
        for k in CARD_KEYS:
            a("<td>{}</td>".format(esc(val(k, p["dims"].get(k))) if p["dims"].get(k) else "-"))
        a("<td class='num'>{}</td></tr>".format(p["summary"].get("scoreable", "-")))
    a("</tbody></table></div>")

    # ---- per persona ------------------------------------------------------
    a("<h2>{}</h2>".format(esc(t("detailHeading"))))
    for p in personas:
        obs = {k: v for k, v in p["grounding"].items() if v.get("assignment_type") in SCOREABLE}
        a("<div class='card person' id='{}'>".format(esc(p["id"])))
        a("<div class='who'><h3>{}</h3><code>{}</code>".format(esc(p["name"]), esc(p["id"])))
        a("<span class='tag obs'>{}</span>".format(esc(t("tagMeasured", count=len(obs)))))
        a("<span class='tag gen'>{}</span></div>".format(
            esc(t("tagGenerated", count=rep["dimension_count"] - len(obs)))))

        bits = [
            "{}: <b>{}</b>".format(esc(lab(k)), esc(val(k, p["dims"][k])))
            for k in CARD_KEYS if p["dims"].get(k)
        ]
        a("<p class='sub' style='margin:.2rem 0 .8rem'>{}</p>".format(" &nbsp;·&nbsp; ".join(bits)))

        a("<h4 style='margin:.9rem 0 .4rem;font-size:.95rem'>{}</h4>".format(
            esc(t("measuredSectionHeading"))))
        a("<div class='scroll'><table><thead><tr><th>{}</th><th>{}</th><th>{}</th>"
          "<th>{}</th></tr></thead><tbody>".format(
              esc(t("colDimension")), esc(t("colValue")),
              esc(t("colSource")), esc(t("colEvidence"))))
        for k in sorted(obs):
            meta = obs[k]
            a("<tr><td>{}<br><code>{}</code></td><td><b>{}</b></td><td><code>{}</code></td>"
              "<td>{}</td></tr>".format(
                  esc(lab(k)), esc(k), esc(val(k, p["dims"].get(k))),
                  esc(meta.get("source_ref", "")), esc(meta.get("evidence", ""))))
        a("</tbody></table></div>")

        gen = [k for k in sorted(p["dims"]) if k not in obs]
        a("<details><summary>{}</summary><div class='grid'>".format(t("generatedSummary", count=len(gen))))
        for k in gen:
            a("<div>{} <span>= {}</span></div>".format(esc(lab(k)), esc(val(k, p["dims"][k]))))
        a("</div></details></div>")

    a("</div></body></html>")
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pool", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    pool = args.pool if args.pool.is_absolute() else REPO_ROOT / args.pool
    personas = load_personas(pool)
    if not personas:
        raise SystemExit("no persona_*.yaml under {}".format(pool))
    manifest_path = pool / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}

    rep = overlap_report(personas)
    out = args.out or (REPO_ROOT / "reports" / "{}-profiles.html".format(pool.name))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(pool, personas, rep, manifest), encoding="utf-8")

    print("personas           {}".format(len(personas)))
    print("dimensions each    {}".format(rep["dimension_count"]))
    print("pairwise overlap   all {:.1f}%  observed {:.1f}%  generated {:.1f}%".format(
        rep["all"]["mean"] * 100, rep["observed"]["mean"] * 100, rep["generated"]["mean"] * 100))
    print("exact duplicates   {}".format(rep["exact_dupes"]))
    print("constant dims      {}/{}".format(len(rep["constant"]), rep["dimension_count"]))
    print("WROTE {}  ({:.1f} MB)".format(out, out.stat().st_size / 1e6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
