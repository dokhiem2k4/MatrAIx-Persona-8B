#!/usr/bin/env python3
"""Crosswalk: World Values Survey Wave 7 Vietnam → observed 1291-dim fields.

The Vietnam country file (1,200 respondents, 423 variables, fieldwork
2019-12-15 to 2020-01-21, full probability sample of adults 18+) is downloaded
directly from the WVS Wave 7 Data Download page -- unlike the Philippines
crosswalk there is no cross-national file to filter, so no country guard is
needed beyond a sanity check.

    python persona/curation/existing_data/scripts/run_pipeline.py \\
      --source persona/curation/existing_data/raw/wvs_vn/wvs_vn.jsonl \\
      --dataset persona/curation/existing_data/scripts/crosswalks/wvs_vn.py \\
      --schema persona/schema/dimensions.json \\
      --out persona/curation/existing_data/raw/wvs_vn/extraction_v1/shard_00.jsonl.gz \\
      --observed-only

Differences from ``wvs_ph.py`` worth knowing:

* ``primary_language`` CAN be filled here. Tagalog is not a schema value, so the
  Philippines crosswalk had to leave it null; ``Vietnamese`` was added to the
  enum in schema 1291, so a Vietnamese-speaking respondent maps directly.
* ``Q240`` (political scale) is absent from the Vietnam file, so
  ``political_lean`` is not mapped at all rather than guessed.
* ``H_URBRURAL`` is binary Urban/Rural. The schema wants Dense urban /
  Suburban / Small town / Rural, so Urban stays null -- a two-way split cannot
  place someone on a four-way scale. Rural maps, because it is unambiguous.

Source fields accept decoded labels (``convert_categoricals=True``) or the raw
numeric WV7 codes.
"""

from __future__ import annotations

VN_TOKENS = {"vnm", "704", "vietnam", "viet nam"}


def _token(row, *keys):
    """First non-empty value among ``keys``, lowercased and stripped."""
    for key in keys:
        if key in row and row[key] is not None:
            value = str(row[key]).strip()
            if value and value.lower() not in {"nan", "none"}:
                return value.lower()
    return ""


def _is_vietnam(row):
    token = _token(row, "B_COUNTRY_ALPHA", "b_country_alpha", "B_COUNTRY", "b_country")
    # An unlabelled country column is not evidence of the wrong country; the
    # file is Vietnam-only by construction, so absence is not a rejection.
    return token in VN_TOKENS if token else True


def _int(row, *keys):
    token = _token(row, *keys)
    try:
        return int(float(token))
    except (TypeError, ValueError):
        return None


def _age_bracket(row):
    if not _is_vietnam(row):
        return None
    age = _int(row, "Q262", "q262", "X003", "x003", "age")
    # Negative codes are WVS missing markers (-1 don't know, -2 no answer...).
    if age is None or age < 0 or age > 120:
        return None
    for hi, label in (
        (4, "Under 5"), (12, "5-12"), (17, "13-17"), (24, "18-24"),
        (34, "25-34"), (44, "35-44"), (54, "45-54"), (64, "55-64"),
        (74, "65-74"), (84, "75-84"),
    ):
        if age <= hi:
            return label
    return "85+"


def _region(row):
    return "Southeast Asia" if _is_vietnam(row) else None


def _cult_vietnam(row):
    """Born and living in Vietnam is native cultural exposure."""
    if not _is_vietnam(row):
        return None
    born = _token(row, "Q263", "q263")
    if born.startswith("2") or "not born" in born or "immigrant" in born:
        return "Lived there"
    if born.startswith("1") or "born in this country" in born:
        return "Native"
    return "Native"


def _home_language(row):
    return _token(row, "Q272", "q272", "language", "home_language")


def _lang_vietnamese(row):
    lang = _home_language(row)
    if not lang:
        return None
    return "Native" if "viet" in lang else None


def _primary_language(row):
    """Only fill when Vietnamese is the language spoken at home.

    Muong and Thai respondents are left null rather than assigned Vietnamese --
    the schema enum has no entry for either, and overwriting a minority language
    with the majority one would erase exactly the variation worth keeping.
    """
    lang = _home_language(row)
    if not lang:
        return None
    return "Vietnamese" if "viet" in lang else None


def _urbanicity(row):
    """Settlement type, not the binary Urban/Rural flag.

    ``H_URBRURAL`` is two-way and cannot place anyone on the schema's four-way
    scale, so an earlier version of this crosswalk left urbanicity null for
    every urban respondent -- which is most of them. ``H_SETTLEMENT`` carries
    the five-way breakdown the schema actually wants.
    """
    token = _token(row, "H_SETTLEMENT", "h_settlement")
    for needle, label in (
        ("capital city", "Dense urban"),
        ("regional center", "Dense urban"),
        ("district center", "Small town"),
        ("another city", "Small town"),
        ("village", "Rural"),
    ):
        if needle in token:
            return label
    # Fall back to the binary flag: Rural is unambiguous, Urban is not.
    binary = _token(row, "H_URBRURAL", "h_urbrural", "urbrural")
    if binary.startswith("2") or "rural" in binary:
        return "Rural"
    return None


#: Provinces the schema names individually. The 4-bit attribute packing caps a
#: dimension at 16 values while the WVS sample covers 18 provinces, so the three
#: smallest -- Quang Nam, Dak Lak, Gia Lai -- resolve to "Other" rather than
#: being dropped. All five centrally-governed cities are kept: that is where
#: traffic, parking and journey length differ most for an in-car assistant.
_NAMED_LOCALITIES = (
    "ha noi", "ho chi minh", "hai phong", "da nang", "can tho",
    "thanh hoa", "an giang", "nghe an", "tien giang", "son la",
    "hoa binh", "dong nai", "hai duong", "thai binh", "binh duong",
)


def _locality(row):
    """Province as reported in 2020 -- NOT wired into CROSSWALK.

    Vietnam merged its 63 provinces into 34 units on 1 July 2025, so several
    provinces this survey names (Hai Duong, Binh Duong, Thai Binh) no longer
    exist. Mapping them onto current units needs the official merger table;
    guessing would put real respondents in the wrong place. Kept here because
    the raw values remain useful if that table is added later.
    """
    token = _token(row, "N_REGION_ISO", "n_region_iso", "N_TOWN", "n_town")
    if not token:
        return None
    # Labels read "VN-HN Ha Noi" or "VN: Ha Noi".
    name = token.split(" ", 1)[-1].strip() if " " in token else token
    name = name.replace("vn:", "").strip()
    for province in _NAMED_LOCALITIES:
        if province in name:
            return province.title()
    return "Other"


def _children(row):
    token = _token(row, "Q274", "q274")
    if not token:
        return None
    if "no children" in token:
        return "None"
    count = _int(row, "Q274", "q274")
    if count is None:
        # Labels read "2 children" / "1 child".
        head = token.split()[0]
        try:
            count = int(head)
        except ValueError:
            return None
    if count < 0:
        return None
    if count == 0:
        return "None"
    if count == 1:
        return "1 child"
    if count == 2:
        return "2 children"
    return "3+ children"


def _education(row):
    """ISCED level → schema education band. Coarse or missing → null."""
    token = _token(row, "Q275", "q275", "Q275A", "q275a")
    if not token:
        return None
    table = (
        ("doctoral", "Doctorate"),
        ("isced 8", "Doctorate"),
        ("master", "Master's"),
        ("isced 7", "Master's"),
        ("bachelor", "Bachelor's"),
        ("isced 6", "Bachelor's"),
        ("short-cycle tertiary", "Associate's"),
        ("isced 5", "Associate's"),
        ("post-secondary non-tertiary", "Vocational / cert"),
        ("isced 4", "Vocational / cert"),
        ("upper secondary", "Secondary"),
        ("isced 3", "Secondary"),
        # ISCED 2 is still secondary schooling; the schema has no finer band.
        ("lower secondary", "Secondary"),
        ("isced 2", "Secondary"),
        ("primary", "Primary"),
        ("isced 1", "Primary"),
        ("early childhood", "No formal"),
        ("no education", "No formal"),
        ("isced 0", "No formal"),
    )
    for needle, label in table:
        if needle in token:
            return label
    return None


#: Self-placed income decile → five-band schema scale. Steps 1-2 low, 3-4
#: lower-middle, 5-6 middle, 7-8 upper-middle, 9-10 high.
_INCOME_STEPS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eight": 8, "eighth": 8, "ninth": 9, "tenth": 10,
}


def _income_band(row):
    token = _token(row, "Q288", "q288")
    if not token:
        return None
    step = None
    for word, value in _INCOME_STEPS.items():
        if token.startswith(word):
            step = value
            break
    if step is None:
        step = _int(row, "Q288", "q288")
    if step is None or not 1 <= step <= 10:
        return None
    if step <= 2:
        return "Low income"
    if step <= 4:
        return "Lower-middle"
    if step <= 6:
        return "Middle"
    if step <= 8:
        return "Upper-middle"
    return "High income"


def _life_stage(row):
    """Only the unambiguous readings. Age alone does not settle life stage."""
    employment = _token(row, "Q279", "q279")
    if "student" in employment:
        return "Student"
    if "retired" in employment:
        return "Retirement"
    return None


def _religiosity(row):
    token = _token(row, "Q164", "q164")
    if not token:
        return None
    if "very important" in token:
        return "Devout"
    if "not at all important" in token:
        return "Secular"
    value = _int(row, "Q164", "q164")
    if value is None or not 1 <= value <= 10:
        return None
    # Q164 runs 1 = very important .. 10 = not at all important.
    if value <= 2:
        return "Devout"
    if value <= 4:
        return "Observant"
    if value <= 7:
        return "Spiritual"
    return "Secular"


def _trust_level(row):
    token = _token(row, "Q57", "q57")
    if not token:
        return None
    if "most people can be trusted" in token or token.startswith("1"):
        return "Trusting"
    if "need to be very careful" in token or token.startswith("2"):
        return "Skeptical"
    return None


CROSSWALK = {
    "age_bracket": {"compute": _age_bracket, "prov": "observed"},
    "gender_identity": {
        "src": "Q260",
        "map": {
            "1": "Man", "male": "Man", "man": "Man",
            "2": "Woman", "female": "Woman", "woman": "Woman",
        },
        "prov": "observed",
    },
    "region": {"compute": _region, "prov": "observed"},
    "cult_vietnam": {"compute": _cult_vietnam, "prov": "observed"},
    "lang_vietnamese": {"compute": _lang_vietnamese, "prov": "observed"},
    "primary_language": {"compute": _primary_language, "prov": "observed"},
    "urbanicity": {"compute": _urbanicity, "prov": "observed"},
    "demo_marital_status": {
        "src": "Q273",
        "map": {
            "1": "Married", "married": "Married",
            "2": "Domestic partnership",
            "living together as married": "Domestic partnership",
            "3": "Divorced", "divorced": "Divorced",
            "4": "Separated", "separated": "Separated",
            "5": "Widowed", "widowed": "Widowed",
            "6": "Single", "single": "Single",
        },
        "prov": "observed",
    },
    "demo_children_count": {"compute": _children, "prov": "observed"},
    "highest_education": {"compute": _education, "prov": "observed"},
    "socioeconomic_band": {"compute": _income_band, "prov": "observed"},
    "demo_employment_status": {
        "src": "Q279",
        "map": {
            "1": "Full-time",
            "full time (30 hours a week or more)": "Full-time",
            "2": "Part-time",
            "part time (less than 30 hours a week)": "Part-time",
            "3": "Self-employed", "self employed": "Self-employed",
            "4": "Retired", "retired/pensioned": "Retired", "retired": "Retired",
            "5": "Homemaker",
            "housewife not otherwise employed": "Homemaker",
            "homemaker not otherwise employed": "Homemaker",
            "6": "Student", "student": "Student",
            "7": "Unemployed", "unemployed": "Unemployed",
            "8": None, "other": None,
        },
        "prov": "observed",
    },
    "life_stage": {"compute": _life_stage, "prov": "observed"},
    "demo_religion_affiliation": {
        "src": "Q289",
        "map": {
            "0": "None", "do not belong to a denomination": "None",
            "buddhist": "Buddhist",
            # The schema groups all Christian denominations into one value.
            "catholic (roman/greek/etc)": "Christian",
            "roman catholic": "Christian",
            "protestant": "Christian",
            "orthodox (russian/greek/etc.)": "Christian",
            "other christian (jehova withness...)": "Christian",
            "muslim": "Muslim",
            "hindu": "Hindu",
            "jew": "Jewish",
            "other": None,
        },
        "prov": "observed",
    },
    "religiosity": {"compute": _religiosity, "prov": "observed"},
    "trust_level": {"compute": _trust_level, "prov": "observed"},
    "demo_citizenship_status": {
        "src": "Q269",
        "map": {
            "1": "Citizen by birth", "yes": "Citizen by birth",
            "2": None, "no": None,
        },
        "prov": "observed",
    },
}
