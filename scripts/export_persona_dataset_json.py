#!/usr/bin/env python3
"""Export a grounded persona pool as one machine-readable JSON dataset.

The pool ships as 42 separate YAML files plus a manifest, which is right for
the repo and wrong for handing to someone who wants to load it in pandas or
feed it to a model. This flattens it into a single document that is
self-describing: every dimension carries its value AND its provenance, and the
catalog at the top says what each dimension id means and what values it admits.

The provenance is the point. A persona holds 1,291 values but only ~24 are
answers a person gave; the rest are sampled from the synthesis graph. Anyone
reading this file downstream must be able to tell those apart without knowing
the pipeline, so `assignmentType` travels with every single value and the
caveats that cannot be expressed per-value -- random pairing, generated
locality -- sit in `provenance.caveats` where they cannot be missed.

Usage:
    uv run python scripts/export_persona_dataset_json.py persona/datasets/vn-drivers
    uv run python scripts/export_persona_dataset_json.py persona/datasets/vn-drivers --no-catalog
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from export_vn_driver_profiles import (  # noqa: E402
    SCOREABLE,
    load_labels,
    load_personas,
    overlap_report,
)

SCHEMA = REPO_ROOT / "persona/schema/dimensions.json"

#: Shown first under each person, in this order, as a one-glance summary.
SUMMARY_KEYS = (
    "age_bracket", "gender_identity", "vn_locality", "region",
    "domain", "life_stage", "intent",
)

#: The schema's 43 categories, for the by-name layout. The English original is
#: kept in the file's `nhomChieu` legend, so nothing is lost by translating.
CATEGORY_VI = {
    "Demographic: Core": "Nhân khẩu: Cơ bản",
    "Demographic: Life Events": "Nhân khẩu: Biến cố cuộc đời",
    "Demographic: Cultural": "Nhân khẩu: Văn hoá",
    "Demographic: Family": "Nhân khẩu: Gia đình",
    "Linguistic: Language": "Ngôn ngữ: Thứ tiếng",
    "Linguistic: Communication": "Ngôn ngữ: Cách giao tiếp",
    "Learning: Academic": "Học tập: Kiến thức hàn lâm",
    "Learning: Style": "Học tập: Phong cách học",
    "Professional: Career": "Nghề nghiệp: Sự nghiệp",
    "Professional: Industry": "Nghề nghiệp: Ngành",
    "Expertise: Domains": "Chuyên môn: Lĩnh vực",
    "Expertise: Skills": "Chuyên môn: Kỹ năng",
    "Skills: Tools": "Kỹ năng: Công cụ",
    "Skills: Programming": "Kỹ năng: Lập trình",
    "Personality: Big Five": "Tính cách: Big Five",
    "Personality: Character": "Tính cách: Phẩm chất",
    "Personality: MBTI": "Tính cách: MBTI",
    "Personality: Relationships": "Tính cách: Quan hệ",
    "Worldview: Beliefs": "Thế giới quan: Niềm tin",
    "Values & Motivation": "Giá trị & Động lực",
    "Risk & Decision": "Rủi ro & Ra quyết định",
    "State: Emotional": "Trạng thái: Cảm xúc",
    "Behavior: Habits": "Hành vi: Thói quen",
    "Behavior: Preferences": "Hành vi: Sở thích",
    "Behavior: Time": "Hành vi: Thời gian",
    "Behavior: Work": "Hành vi: Công việc",
    "Interests: Media": "Sở thích: Truyền thông",
    "Interests: Topics": "Sở thích: Chủ đề",
    "Interests: Culture": "Sở thích: Văn hoá",
    "Interests: Hobbies": "Sở thích: Thú vui",
    "Interests: Sports": "Sở thích: Thể thao",
    "Interests: Food": "Sở thích: Ẩm thực",
    "Health: Physical": "Sức khoẻ: Thể chất",
    "Health: Fitness": "Sức khoẻ: Rèn luyện",
    "Health: Lifestyle": "Sức khoẻ: Lối sống",
    "Developer: AI Workflow Tasks": "Lập trình viên: Tác vụ AI",
    "Developer: Agent Adoption": "Lập trình viên: Dùng agent",
    "Developer: Code Maintenance": "Lập trình viên: Bảo trì mã",
    "Developer: AI Adoption": "Lập trình viên: Tiếp nhận AI",
    "Developer: Technology Evaluation": "Lập trình viên: Đánh giá công nghệ",
    "Developer: Open Source Behavior": "Lập trình viên: Mã nguồn mở",
    "Developer: Professional Context": "Lập trình viên: Bối cảnh nghề",
    "Developer: Community Behavior": "Lập trình viên: Cộng đồng",
}


def build_catalog(used: list[str]) -> dict:
    """Describe every dimension present, so the file explains itself."""
    dims = {d["id"]: d for d in json.loads(SCHEMA.read_text(encoding="utf-8"))["dimensions"]}
    dim_label_vi, val_label_vi = load_labels()
    catalog = {}
    for key in used:
        spec = dims.get(key) or {}
        entry = {
            "label": spec.get("label", key),
            "values": spec.get("values", []),
        }
        if spec.get("description"):
            entry["description"] = spec["description"]
        if dim_label_vi.get(key):
            entry["labelVi"] = dim_label_vi[key]
        vi_values = val_label_vi.get(key) or {}
        if vi_values:
            entry["valuesVi"] = {v: vi_values[v] for v in entry["values"] if v in vi_values}
        catalog[key] = entry
    return catalog


def build_by_name(pool: Path) -> dict:
    """Same data, keyed by person and grouped so it reads top-to-bottom.

    The flat layout is one dict of 1,291 ids per persona, which is fine for a
    program and unreadable for a person. Here each person gets a summary, then
    the dimensions they actually answered, then everything the graph generated
    grouped by subject area.
    """
    personas = load_personas(pool)
    if not personas:
        raise SystemExit("no persona_*.yaml under {}".format(pool))
    manifest_path = pool / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    rep = overlap_report(personas)
    flat = build(pool, catalog=False)

    spec = {d["id"]: d for d in json.loads(SCHEMA.read_text(encoding="utf-8"))["dimensions"]}
    dim_label_vi, val_label_vi = load_labels()

    def lab(key: str) -> str:
        return dim_label_vi.get(key) or (spec.get(key) or {}).get("label") or key

    def val(key: str, value) -> str:
        return (val_label_vi.get(key) or {}).get(str(value), value)

    def cat(key: str) -> str:
        raw = (spec.get(key) or {}).get("category") or "Other"
        return CATEGORY_VI.get(raw, raw)

    people: dict = {}
    for p in personas:
        obs_keys = sorted(
            k for k, v in p["grounding"].items() if v.get("assignment_type") in SCOREABLE
        )
        obs_set = set(obs_keys)

        # Two personas can share a generated name, so the key carries the id.
        # Keying on the name alone would silently drop one of them.
        person_key = "{} — {}".format(p["name"], p["id"])

        measured: dict = {}
        for k in obs_keys:
            if k not in p["dims"]:
                continue
            meta = p["grounding"].get(k) or {}
            measured[_unique(measured, lab(k), k)] = {
                "chieu": k,
                "giaTri": val(k, p["dims"][k]),
                "giaTriGoc": p["dims"][k],
                "nguon": meta.get("source_ref"),
                "bangChung": meta.get("evidence"),
            }

        generated: dict = {}
        for k in sorted(p["dims"]):
            if k in obs_set:
                continue
            group = generated.setdefault(cat(k), {})
            group[_unique(group, lab(k), k)] = val(k, p["dims"][k])

        people[person_key] = {
            "ma": p["id"],
            "ten": p["name"],
            "tomTat": {
                lab(k): val(k, p["dims"][k]) for k in SUMMARY_KEYS if p["dims"].get(k)
            },
            "soChieu": {
                "doDuoc": len(measured),
                "sinhRa": sum(len(g) for g in generated.values()),
                "tong": len(p["dims"]),
            },
            "doDuocTuNguoiThat": measured,
            "sinhRaTuDoThi": generated,
        }

    return {
        "formatVersion": "1.0-by-name",
        "datasetId": manifest.get("datasetId") or pool.name,
        "personaCount": len(personas),
        "dimensionCount": rep["dimension_count"],
        "cachDoc": {
            "nguoi": "Khoá là 'Tên — mã persona'. Hai người có thể trùng tên nên mã luôn đi kèm.",
            "tomTat": "Vài chiều chính, để nhìn phát biết ngay là ai.",
            "doDuocTuNguoiThat": "Các chiều là câu trả lời của người thật. Chỉ những chiều này là "
                                 "số liệu đo; mỗi chiều ghi rõ nguồn và bằng chứng.",
            "sinhRaTuDoThi": "Phần còn lại, lấy mẫu từ đồ thị tổng hợp có ghim các chiều đã đo. "
                             "Nhất quán với phần đo được, nhưng KHÔNG phải số liệu đo và không "
                             "bao giờ được tính điểm.",
            "giaTriGoc": "Giá trị tiếng Anh đúng như trong schema, dùng khi cần lọc/so khớp bằng máy.",
        },
        "provenance": flat["provenance"],
        "overlap": flat["overlap"],
        "nhomChieu": {vi: en for en, vi in CATEGORY_VI.items()},
        "nguoi": people,
    }


def _unique(bucket: dict, label: str, key: str) -> str:
    """Keep a readable label as the key without ever overwriting a sibling."""
    if label not in bucket:
        return label
    return "{} ({})".format(label, key)


def build(pool: Path, *, catalog: bool) -> dict:
    personas = load_personas(pool)
    if not personas:
        raise SystemExit("no persona_*.yaml under {}".format(pool))
    manifest_path = pool / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    rep = overlap_report(personas)

    keys = sorted(set().union(*[set(p["dims"]) for p in personas]))

    doc: dict = {
        "formatVersion": "1.0",
        "datasetId": manifest.get("datasetId") or pool.name,
        "personaCount": len(personas),
        "dimensionCount": len(keys),
        "provenance": {
            "sources": manifest.get("grounding", {}).get("sources", []),
            "primary": manifest.get("primary"),
            "secondary": manifest.get("secondary"),
            "droppedByFilter": manifest.get("droppedByFilter"),
            "pairing": manifest.get("pairing"),
            "byAssignmentType": manifest.get("grounding", {}).get("byAssignmentType"),
            "scoreableMean": manifest.get("grounding", {}).get("scoreableMean"),
            "assignmentTypes": {
                "observed": "answered by a real respondent; the only values that are measurement",
                "generated": "sampled from persona/synthesis/graph/full_dag.json with the observed "
                             "dimensions pinned; never scoreable",
            },
            "scoreableTypes": sorted(SCOREABLE),
            "caveats": [
                "The two source layers describe DIFFERENT PEOPLE and share no dimension, so pairing "
                "is random. Any demographic-to-driving correlation in this dataset is an artefact of "
                "that pairing, not a measurement. Only within-layer relationships are observed.",
                "vn_locality is generated, not observed: WVS Wave 7 recorded pre-merger province "
                "names and mapping them onto the 34 units effective 2025-07-01 needs the official "
                "merger table. Localities are a population-weighted draw -- draw no conclusions by "
                "province.",
                "Names are generated to be consistent with gender_identity. They identify no one.",
            ],
        },
        "overlap": {
            "note": "Share of dimensions holding an identical value, over all persona pairs.",
            "pairCount": rep["pair_count"],
            "allDimensions": rep["all"],
            "observedOnly": rep["observed"],
            "generatedOnly": rep["generated"],
            "exactDuplicatePersonas": rep["exact_dupes"],
            "dimensionsConstantAcrossPool": rep["constant"],
        },
        "observedDimensions": rep["observed_keys"],
    }

    if catalog:
        doc["dimensionCatalog"] = build_catalog(keys)

    doc["personas"] = [
        {
            "personaId": p["id"],
            "displayName": p["name"],
            "source": p["source"],
            "file": p["file"],
            "groundingSummary": p["summary"],
            "observedDimensions": sorted(
                k for k, v in p["grounding"].items()
                if v.get("assignment_type") in SCOREABLE
            ),
            "dimensions": {
                k: {
                    "value": p["dims"][k],
                    "assignmentType": (p["grounding"].get(k) or {}).get("assignment_type"),
                    "sourceRef": (p["grounding"].get(k) or {}).get("source_ref"),
                    "evidence": (p["grounding"].get(k) or {}).get("evidence"),
                }
                for k in sorted(p["dims"])
            },
        }
        for p in personas
    ]
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pool", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--no-catalog", action="store_true", help="omit the dimension catalog")
    ap.add_argument("--indent", type=int, default=2, help="0 for the most compact file")
    ap.add_argument(
        "--by-name",
        action="store_true",
        help="key by person and group each one's dimensions by subject area",
    )
    args = ap.parse_args()

    pool = args.pool if args.pool.is_absolute() else REPO_ROOT / args.pool
    if args.by_name:
        doc = build_by_name(pool)
        default_name = "{}-by-name.json".format(pool.name)
    else:
        doc = build(pool, catalog=not args.no_catalog)
        default_name = "{}-dataset.json".format(pool.name)
    out = args.out or (REPO_ROOT / "reports" / default_name)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(doc, ensure_ascii=False, indent=args.indent or None) + "\n",
        encoding="utf-8",
    )

    print("personas        {}".format(doc["personaCount"]))
    print("dimensions each {}".format(doc["dimensionCount"]))
    if args.by_name:
        print("layout          by person, grouped by subject area")
    else:
        print("observed dims   {}".format(len(doc["observedDimensions"])))
        print("catalog         {}".format("yes" if "dimensionCatalog" in doc else "no"))
    print("WROTE {}  ({:.1f} MB)".format(out, out.stat().st_size / 1e6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
