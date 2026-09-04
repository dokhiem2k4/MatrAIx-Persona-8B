"""Vietnam's current provinces and cities, with populations for weighting.

Vietnam merged its 63 provinces into 34 units on 1 July 2025, so a persona set
built for a 2026 benchmark should live in the current map, not the pre-merger
one. That also rules out reusing the province a WVS 2020 respondent reported:
their province may no longer exist, and mapping 2020 names onto 2025 units
needs the official merger table rather than a guess.

A locality drawn from here is therefore ``generated``, not ``observed``. It is
weighted by real population, so a sampled cohort concentrates in Ho Chi Minh
City and Hanoi the way drivers actually do -- a uniform draw would put as many
personas in Lai Chau (0.5M) as in Ho Chi Minh City (14M) and quietly overstate
how rural the test population is.

Populations are 2025 figures for the merged units.
Source: https://en.wikipedia.org/wiki/Provinces_of_Vietnam
"""

from __future__ import annotations

import hashlib

#: ``(canonical English name, Vietnamese name, population)``. English is the
#: canonical schema value; Vietnamese belongs in the display label pack.
LOCALITIES: tuple[tuple[str, str, int], ...] = (
    ("Ho Chi Minh City", "TP. Hồ Chí Minh", 14_002_598),
    ("Ha Noi", "Hà Nội", 8_807_523),
    ("An Giang", "An Giang", 4_952_238),
    ("Hai Phong", "Hải Phòng", 4_664_124),
    ("Dong Nai", "Đồng Nai", 4_491_408),
    ("Ninh Binh", "Ninh Bình", 4_412_464),
    ("Dong Thap", "Đồng Tháp", 4_370_046),
    ("Thanh Hoa", "Thanh Hóa", 4_324_783),
    ("Vinh Long", "Vĩnh Long", 4_257_581),
    ("Can Tho", "Cần Thơ", 4_199_824),
    ("Phu Tho", "Phú Thọ", 4_022_638),
    ("Lam Dong", "Lâm Đồng", 3_872_999),
    ("Nghe An", "Nghệ An", 3_831_694),
    ("Bac Ninh", "Bắc Ninh", 3_619_433),
    ("Gia Lai", "Gia Lai", 3_583_693),
    ("Hung Yen", "Hưng Yên", 3_567_943),
    ("Dak Lak", "Đắk Lắk", 3_346_853),
    ("Tay Ninh", "Tây Ninh", 3_254_170),
    ("Da Nang", "Đà Nẵng", 3_065_628),
    ("Ca Mau", "Cà Mau", 2_606_672),
    ("Khanh Hoa", "Khánh Hòa", 2_243_554),
    ("Quang Ngai", "Quảng Ngãi", 2_161_755),
    ("Quang Tri", "Quảng Trị", 1_870_845),
    ("Tuyen Quang", "Tuyên Quang", 1_865_270),
    ("Thai Nguyen", "Thái Nguyên", 1_799_489),
    ("Lao Cai", "Lào Cai", 1_778_785),
    ("Ha Tinh", "Hà Tĩnh", 1_622_901),
    ("Quang Ninh", "Quảng Ninh", 1_497_477),
    ("Hue", "Huế", 1_432_986),
    ("Son La", "Sơn La", 1_404_587),
    ("Lang Son", "Lạng Sơn", 881_384),
    ("Dien Bien", "Điện Biên", 673_091),
    ("Cao Bang", "Cao Bằng", 573_119),
    ("Lai Chau", "Lai Châu", 512_601),
)

NAMES: tuple[str, ...] = tuple(name for name, _, _ in LOCALITIES)
VIETNAMESE: dict[str, str] = {name: vi for name, vi, _ in LOCALITIES}
POPULATION: dict[str, int] = {name: pop for name, _, pop in LOCALITIES}


def weighted_locality(seed: str) -> str:
    """Pick a locality for ``seed``, weighted by population.

    Deterministic: the same persona id always lands in the same place, so a
    rebuild does not silently relocate everybody and break comparisons with an
    earlier run.
    """
    total = sum(POPULATION.values())
    digest = hashlib.sha256("locality|{}".format(seed).encode("utf-8")).digest()
    point = int.from_bytes(digest[:8], "big") % total
    running = 0
    for name, _, population in LOCALITIES:
        running += population
        if point < running:
            return name
    return LOCALITIES[-1][0]
