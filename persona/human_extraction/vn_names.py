"""Deterministic Vietnamese display names for grounded personas.

A persona whose name is "VN 704070211" reads as a record, and the simulated
conversation shows it: an in-car assistant addressed by a row id does not
sound like a person talking to their car. But a name is not data. Nobody
surveyed supplied one, and the consent text promised responses are stored
without names, so a generated name must never be mistaken for a measured
attribute -- it is recorded as ``generated`` and excluded from scoring.

Two rules, both learned from what the existing corpus got wrong. Names must
agree with ``gender_identity``: the repo currently holds personas named as
women carrying ``gender_identity: Man``, and Vietnamese address depends on
gender, so the model receives two contradictory signals in one prompt. And the
same persona id must always produce the same name, or a re-run silently
renames everybody and results stop lining up.
"""

from __future__ import annotations

import hashlib

#: Most common Vietnamese family names, roughly by frequency.
SURNAMES = (
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ",
    "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý",
)

#: Middle + given names. Vietnamese given names are strongly gendered, which is
#: the whole reason this file exists.
GIVEN_WOMAN = (
    "Thị Hương", "Thị Lan", "Thu Hà", "Thị Mai", "Ngọc Anh", "Thị Thanh",
    "Kim Chi", "Thị Hoa", "Minh Châu", "Thị Nhung", "Phương Thảo", "Thị Yến",
    "Hải Yến", "Thị Loan", "Bích Ngọc", "Thùy Linh", "Thị Hạnh", "Diệu Linh",
)
GIVEN_MAN = (
    "Văn Hùng", "Minh Tuấn", "Văn Nam", "Quốc Anh", "Văn Dũng", "Hữu Thắng",
    "Văn Long", "Đức Minh", "Văn Cường", "Thanh Sơn", "Văn Tùng", "Quang Huy",
    "Văn Hải", "Trung Kiên", "Xuân Bách", "Văn Thành", "Hoàng Nam", "Đình Phong",
)
#: Used when gender is absent or not stated: given names read as either.
GIVEN_NEUTRAL = (
    "An", "Bình", "Khánh Linh", "Hà My", "Nhật Minh", "Thanh Tâm",
    "Quỳnh Anh", "Hoài An", "Bảo Ngọc", "Tuệ Lâm",
)


def _index(seed: str, salt: str, size: int) -> int:
    """Stable index from a persona id -- same id, same name, every run."""
    digest = hashlib.sha256("{}|{}".format(seed, salt).encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % size


def vietnamese_name(persona_id: str, gender: str | None = None) -> str:
    """A Vietnamese name consistent with ``gender`` and stable for ``persona_id``."""
    normalized = (gender or "").strip().lower()
    if normalized in {"woman", "female", "nữ"}:
        given = GIVEN_WOMAN
    elif normalized in {"man", "male", "nam"}:
        given = GIVEN_MAN
    else:
        given = GIVEN_NEUTRAL
    surname = SURNAMES[_index(persona_id, "surname", len(SURNAMES))]
    return "{} {}".format(surname, given[_index(persona_id, "given", len(given))])
