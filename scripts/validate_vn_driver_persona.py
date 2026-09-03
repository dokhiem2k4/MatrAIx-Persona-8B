#!/usr/bin/env python3
"""Kiểm tra persona tài xế Việt Nam theo chuẩn vn_driver_persona.

Chuẩn: persona/human_extraction/standards/vn_driver_persona_v1.json

Bổ sung cho validate_extraction.py chứ không thay thế. Cái kia kiểm tra tính hợp
lệ với schema; cái này kiểm tra thêm ba thứ mà một bộ persona dùng để chấm trợ lý
trên xe bắt buộc phải có:

  1. Đủ Tier A       -- thiếu một chiều là persona đó không so sánh được với
                        persona khác trên chiều ấy.
  2. Đủ điều kiện    -- người không lái xe thì không chấm trợ lý trên xe.
  3. Độ phủ đồng đều -- trên 541 persona hiện có, độ phủ dao động 7-1290 chiều.
                        Chênh lệch đó biến thành biến gây nhiễu khi đọc điểm.

Dùng:
    uv run python scripts/validate_vn_driver_persona.py --input drivers.jsonl
    uv run python scripts/validate_vn_driver_persona.py --input 'persona/datasets/**/persona_*.yaml'
"""

from __future__ import annotations

import argparse
import glob
import gzip
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parent.parent
STANDARD = REPO_ROOT / "persona/human_extraction/standards/vn_driver_persona_v1.json"
SCHEMA = REPO_ROOT / "persona/schema/dimensions.json"


def load_records(pattern: str) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield (nhãn, dimensions) từ .jsonl(.gz) hoặc persona YAML."""
    paths = sorted(glob.glob(pattern, recursive=True))
    if not paths:
        raise SystemExit("không khớp file nào: {}".format(pattern))
    for path in paths:
        p = Path(path)
        if p.suffix in {".jsonl", ".gz"} or p.name.endswith(".jsonl.gz"):
            opener = gzip.open if p.name.endswith(".gz") else open
            with opener(p, "rt", encoding="utf-8") as handle:
                for i, line in enumerate(handle):
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    dims = rec.get("fields") or rec.get("dimensions") or rec.get("observed") or {}
                    if isinstance(dims, dict) and dims and isinstance(next(iter(dims.values())), dict):
                        # {dim: {"value": x, "provenance": y}}
                        dims = {k: v.get("value") for k, v in dims.items()}
                    yield "{}#{}".format(p.name, rec.get("user_id") or i), dims
        else:
            import yaml

            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            yield data.get("display_name") or p.stem, data.get("dimensions") or {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="glob tới jsonl(.gz) hoặc persona yaml")
    parser.add_argument("--standard", type=Path, default=STANDARD)
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--max-report", type=int, default=12)
    parser.add_argument(
        "--skip-eligibility",
        action="store_true",
        help="bỏ qua kiểm tra biết-lái-xe (dùng khi soi kho persona cũ)",
    )
    args = parser.parse_args()

    std = json.loads(args.standard.read_text(encoding="utf-8"))
    schema = {d["id"]: d for d in json.loads(args.schema.read_text(encoding="utf-8"))["dimensions"]}

    tier_a = [d["id"] for d in std["tierA"]["dimensions"]]
    forbidden = set(std["forbiddenValues"]["literalStrings"])
    elig = std["eligibility"]["rules"][0]

    missing_counts: dict[str, int] = {d: 0 for d in tier_a}
    bad_values: list[str] = []
    ineligible: list[str] = []
    grounded: list[int] = []
    n = 0

    for label, dims in load_records(args.input):
        n += 1
        filled = 0
        for dim_id, value in dims.items():
            spec = schema.get(dim_id)
            if spec is None:
                bad_values.append("{}: {} = khoá ngoài schema".format(label, dim_id))
                continue
            if value is None:
                continue
            text = str(value)
            # "None" chỉ là rác khi enum của chiều đó không nhận nó.
            if text in forbidden and text not in map(str, spec["values"]):
                bad_values.append("{}: {} = {!r} (chuỗi rác, phải là null)".format(label, dim_id, text))
                continue
            if text not in map(str, spec["values"]):
                bad_values.append("{}: {} = {!r} (ngoài enum)".format(label, dim_id, text))
                continue
            filled += 1
        grounded.append(filled)

        for dim_id in tier_a:
            v = dims.get(dim_id)
            if v is None or str(v) in forbidden and str(v) not in map(str, schema[dim_id]["values"]):
                missing_counts[dim_id] += 1

        if not args.skip_eligibility:
            status = str(dims.get(elig["dimension"]) or "")
            if status not in elig["mustBeOneOf"]:
                ineligible.append("{}: {} = {!r}".format(label, elig["dimension"], status or None))

    print("chuẩn      : {} v{}".format(std["standardId"], std["version"]))
    print("persona    : {}".format(n))
    if grounded:
        stdev = statistics.pstdev(grounded) if len(grounded) > 1 else 0.0
        print(
            "độ phủ     : TB {:.1f} | min {} | max {} | độ lệch {:.1f}".format(
                statistics.mean(grounded), min(grounded), max(grounded), stdev
            )
        )

    errors = 0

    incomplete = {d: c for d, c in missing_counts.items() if c}
    print("\n-- Tier A ({} chiều bắt buộc) --".format(len(tier_a)))
    if incomplete:
        errors += sum(incomplete.values())
        for dim_id, c in sorted(incomplete.items(), key=lambda kv: -kv[1])[: args.max_report]:
            print("   THIẾU  {:28s} {}/{} persona".format(dim_id, c, n))
        if len(incomplete) > args.max_report:
            print("   ... còn {} chiều nữa".format(len(incomplete) - args.max_report))
    else:
        print("   OK — đủ ở toàn bộ persona")

    print("\n-- Giá trị hợp lệ --")
    if bad_values:
        errors += len(bad_values)
        print("   {} giá trị không hợp lệ".format(len(bad_values)))
        for line in bad_values[: args.max_report]:
            print("   {}".format(line))
        if len(bad_values) > args.max_report:
            print("   ... còn {} lỗi nữa".format(len(bad_values) - args.max_report))
    else:
        print("   OK — mọi giá trị nằm trong enum")

    if not args.skip_eligibility:
        print("\n-- Đủ điều kiện lái xe --")
        if ineligible:
            errors += len(ineligible)
            print("   {}/{} persona không lái xe".format(len(ineligible), n))
            for line in ineligible[: args.max_report]:
                print("   {}".format(line))
        else:
            print("   OK — mọi persona đều lái xe")

    print("\n-- Độ phủ đồng đều --")
    limit = std["coverageParity"]["maxGroundedStdevInBatch"]
    if len(grounded) > 1:
        stdev = statistics.pstdev(grounded)
        if stdev > limit:
            errors += 1
            print(
                "   LỆCH  độ lệch chuẩn {:.1f} > ngưỡng {} — chênh lệch độ phủ sẽ lẫn vào điểm số".format(
                    stdev, limit
                )
            )
        else:
            print("   OK — độ lệch chuẩn {:.1f} <= {}".format(stdev, limit))
    else:
        print("   (bỏ qua, chỉ có 1 persona)")

    print("\n{}".format("ĐẠT" if errors == 0 else "KHÔNG ĐẠT — {} lỗi".format(errors)))
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
