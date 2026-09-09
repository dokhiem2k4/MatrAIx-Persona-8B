#!/usr/bin/env python3
"""Crosswalk: Vietnamese driver questionnaire → observed 1291-dim fields.

The eight dimensions here are the ones no population survey carries. WVS Wave 7
Vietnam grounds demographics but never asks about cars, so the 1,200 personas it
produces fail every driving check; this layer is what makes them scoreable.

The map is keyed on the Vietnamese option labels a respondent actually clicks,
because that is what a Google Forms CSV export contains -- not the schema value.
Both sides are generated from the same questionnaire JSON
(``standards/vn_driver_questionnaire.json``), so a renamed option is a change in
one file rather than a silent mismatch here.

    python persona/curation/existing_data/scripts/run_pipeline.py \\
      --source vn_drivers.jsonl \\
      --dataset persona/curation/existing_data/scripts/crosswalks/vn_drivers.py \\
      --schema persona/schema/dimensions.json \\
      --out persona/curation/existing_data/raw/vn_drivers/extraction_v1/shard_00.jsonl.gz \\
      --observed-only

Each source row is one respondent: ``{user_id, "<question text>": "<label>", ...}``.
A partial row still converts, but a respondent who skipped a question
contributes nothing to the joint distribution for that pair -- which is the
whole reason for collecting this rather than stitching public datasets that
describe different people.
"""

from __future__ import annotations

# Column headers in a Google Forms CSV export are the question texts. Keys are
# matched on a normalised substring so a trailing "?" or added instruction line
# does not break the lookup.
Q_DRIVER_STATUS = "lái ô tô ở mức nào"
Q_COMMUTE = "phương tiện anh/chị dùng nhiều nhất"
Q_SKILL = "tự đánh giá tay lái"
Q_PATIENCE = "hiểu sai ý"
Q_SKEPTICISM = "kiểm chứng lại"
Q_TOPIC_CARS = "quan tâm của anh/chị tới ô tô"
Q_EV = "về xe điện"
Q_SELF_DRIVING = "xe tự lái"
Q_VERBOSITY = "anh/chị thường nói"
Q_ADDRESS = "xưng hô thế nào"


def _norm(text):
    return " ".join(str(text or "").strip().lower().split())


def _answer(row, needle):
    """Value of the column whose header contains ``needle``."""
    needle = _norm(needle)
    for key, value in row.items():
        if needle in _norm(key):
            answer = _norm(value)
            if answer and answer not in {"nan", "none", "null", "-"}:
                return answer
    return ""


def _pick(row, needle, table):
    """Map an answer through ``table``; unrecognised text stays unmapped.

    Substring matching, so an option label edited for tone still lands as long
    as its distinguishing phrase survives. Nothing is guessed: a label that
    matches no entry returns None and the dimension is left unsupported.
    """
    answer = _answer(row, needle)
    if not answer:
        return None
    for fragment, value in table:
        if fragment in answer:
            return value
    return None


def _driver_status(row):
    return _pick(row, Q_DRIVER_STATUS, (
        ("hằng ngày", "Daily driver"),
        ("hàng ngày", "Daily driver"),
        ("thỉnh thoảng", "Occasional driver"),
        ("hiếm khi", "Licensed, rarely drives"),
        ("không lái được", "Cannot drive"),
        ("không lái", "Non-driver"),
    ))


def _commute_mode(row):
    return _pick(row, Q_COMMUTE, (
        ("ô tô", "Car"),
        ("xe máy", "Bike"),
        ("xe đạp", "Bike"),
        ("công cộng", "Public transit"),
        ("xe công nghệ", "Rideshare"),
        ("grab", "Rideshare"),
        ("đi bộ", "Walk"),
        ("từ xa", "Remote"),
    ))


def _skill_driving(row):
    return _pick(row, Q_SKILL, (
        ("rất thành thạo", "Master"),
        ("thành thạo", "Advanced"),
        ("trung bình", "Intermediate"),
        ("mới lái", "Beginner"),
        ("không lái được", "None"),
    ))


def _patience(row):
    return _pick(row, Q_PATIENCE, (
        ("kiên trì", "Very high"),
        ("vài lần rồi mới thôi", "High"),
        ("một hai lần", "Moderate"),
        ("nhanh chán", "Low"),
        ("bỏ luôn", "None"),
    ))


def _skepticism(row):
    return _pick(row, Q_SKEPTICISM, (
        ("luôn kiểm chứng", "Very high"),
        ("thường kiểm chứng", "High"),
        ("thỉnh thoảng", "Moderate"),
        ("hiếm khi", "Low"),
        ("tin luôn", "None"),
    ))


def _topic_cars(row):
    return _pick(row, Q_TOPIC_CARS, (
        ("đam mê", "Passionate"),
        ("có quan tâm", "Interested"),
        ("bình thường", "Neutral"),
        ("không quan tâm", "Indifferent"),
        ("ngại", "Averse"),
    ))


_ATTITUDE = (
    ("rất ủng hộ", "Enthusiast"),
    ("tích cực", "Positive"),
    ("trung lập", "Neutral"),
    ("hoài nghi", "Skeptical"),
    ("phản đối", "Opposed"),
)


def _ev_attitude(row):
    return _pick(row, Q_EV, _ATTITUDE)


def _self_driving_attitude(row):
    return _pick(row, Q_SELF_DRIVING, _ATTITUDE)


def _verbosity(row):
    return _pick(row, Q_VERBOSITY, (
        ("rất ngắn", "Terse"),
        ("ngắn gọn", "Concise"),
        ("vừa phải", "Balanced"),
        ("khá dài", "Wordy"),
        ("lan man", "Rambling"),
    ))


def _address_register(row):
    return _pick(row, Q_ADDRESS, (
        ("anh – em", "anh/em"),
        ("anh - em", "anh/em"),
        ("chị – em", "chi/em"),
        ("chị - em", "chi/em"),
        ("em – anh", "em/anh-chi"),
        ("em - anh", "em/anh-chi"),
        ("cô-chú", "co-chu/con"),
        ("cô - chú", "co-chu/con"),
        ("bác", "bac/chau"),
        ("tôi", "toi/ban"),
        ("mình", "minh/ban"),
    ))


# --- questions added in the 2026 expansion -----------------------------------
# These six are structured (checkbox / 1-5 scale), so they cross-walk by lookup
# exactly like the eight above -- no free-text reading, no model in the loop.
Q_COMPANION = "thường có ai đi cùng"
Q_PRIVACY = "nói to với trợ lý khi trên xe có người khác"
Q_TASK_SCOPE = "hay nhờ trợ lý trên xe làm những việc gì"
Q_RETRY = "phải nhắc lại một câu lệnh vài lần"

#: Checkbox answers arrive joined by ", ". The single most demanding companion
#: wins, because that is the one that changes what a driver will say out loud.
_COMPANION_PRIORITY = (
    ("khách", "Paying passengers"),
    ("con nhỏ", "Young children"),
    ("con đã lớn", "Older children"),
    ("bố mẹ", "Parents or elders"),
    ("người lớn tuổi", "Parents or elders"),
    ("vợ", "Spouse or partner"),
    ("chồng", "Spouse or partner"),
    ("người yêu", "Spouse or partner"),
    ("bạn bè", "Friends or colleagues"),
    ("đồng nghiệp", "Friends or colleagues"),
    ("một mình", "Alone"),
)


def _companion(row):
    answer = _answer(row, Q_COMPANION)
    if not answer:
        return None
    for fragment, value in _COMPANION_PRIORITY:
        if fragment in answer:
            return value
    return None


def _scale5(row, needle, values):
    """A 1-5 Likert answer to its schema value; anything else stays unmapped."""
    answer = _answer(row, needle)
    if answer[:1].isdigit():
        index = int(answer[0])
        if 1 <= index <= 5:
            return values[index - 1]
    return None


def _voice_privacy_comfort(row):
    return _scale5(row, Q_PRIVACY, (
        "Very uncomfortable", "Uncomfortable", "Neutral", "Comfortable", "Very comfortable"))


def _retry_tolerance(row):
    return _scale5(row, Q_RETRY, (
        "Unbothered", "Mildly annoyed", "Annoyed", "Very annoyed", "Gives up immediately"))


def _assistant_task_scope(row):
    """Breadth of delegation, read from how many task families were ticked."""
    answer = _answer(row, Q_TASK_SCOPE)
    if not answer:
        return None
    if "không nhờ gì" in answer:
        return "None"
    if "điều hoà" in answer or "điều hòa" in answer:
        return "Everything including vehicle control"
    families = sum(
        1 for fragment in ("chỉ đường", "gọi điện", "mở nhạc", "tìm chỗ đỗ", "mức pin", "linh tinh")
        if fragment in answer
    )
    if families >= 4:
        return "Most non-driving tasks"
    if families >= 2:
        return "Navigation and media"
    return "Navigation only"


def _voice_assistant_attitude(row):
    """Stance toward the in-car assistant, from how much of it they actually use.

    Derived rather than asked: the form has no direct stance question, and how
    much someone hands over is a firmer signal than what they would claim.
    """
    scope = _assistant_task_scope(row)
    if scope is None:
        return None
    return {
        "None": "Opposed",
        "Navigation only": "Skeptical",
        "Navigation and media": "Neutral",
        "Most non-driving tasks": "Positive",
        "Everything including vehicle control": "Enthusiast",
    }[scope]


# --- 2026 expansion, second round --------------------------------------------
# Nine more closed questions, mapped the same way as the eight originals: by
# the Vietnamese label a respondent clicked. All are single-select or scale
# except cabin_context, where the most constraining answer wins -- a driver
# with both hands on the wheel is bound by that, whatever else they ticked.
Q_ACCENT = "giọng của anh/chị nghe rõ nhất"
Q_VEH_CLASS = "xe anh/chị hay lái nhất thuộc hạng nào"
Q_VEH_BUILTIN = "có sẵn trợ lý giọng nói của hãng"
Q_EXPOSURE = "mỗi tuần anh/chị lái khoảng bao nhiêu"
Q_TRIP_MIX = "phần lớn quãng đường anh/chị lái"
Q_USAGE_FREQ = "dùng trợ lý giọng nói khi lái xe thường xuyên"
Q_NEED_STATE = "mong chuyến đi mang lại cảm giác gì"
Q_CABIN_CTX = "tay và mắt đang bận gì"
Q_CABIN_NOISE = "thường ồn tới mức nào"


def _accent_region(row):
    return _pick(row, Q_ACCENT, (
        ("giọng bắc", "Northern"), ("giọng trung", "Central"),
        ("giọng nam", "Southern"), ("pha trộn", "Mixed")))


def _veh_class(row):
    return _pick(row, Q_VEH_CLASS, (
        ("hatchback", "Hatchback"), ("sedan", "Sedan"), ("suv", "SUV or crossover"),
        ("bán tải", "Pickup"), ("7 chỗ", "Seven seater or larger"),
        ("xe tải", "Truck or commercial"), ("không sở hữu", "Does not own")))


def _veh_assistant_builtin(row):
    return _pick(row, Q_VEH_BUILTIN, (
        ("có, và tôi dùng", "Built in and used"),
        ("có, nhưng tôi không dùng", "Built in but unused"),
        ("không có, tôi dùng trợ lý trên điện thoại", "None, uses phone assistant"),
        ("không có, và tôi không dùng", "None, uses no assistant")))


def _drv_exposure(row):
    return _pick(row, Q_EXPOSURE, (
        ("dưới 50", "Under 50 km"), ("50-150", "50-150 km"), ("150-300", "150-300 km"),
        ("300-600", "300-600 km"), ("trên 600", "Over 600 km")))


def _trip_mix(row):
    return _pick(row, Q_TRIP_MIX, (
        ("nội đô", "Mostly city"), ("cao tốc", "Mostly motorway"),
        ("đường tỉnh", "Mostly provincial roads"), ("hỗn hợp", "Mixed")))


def _assistant_usage_freq(row):
    return _pick(row, Q_USAGE_FREQ, (
        ("mỗi chuyến", "Almost every trip"), ("vài lần một tuần", "Several times a week"),
        ("vài lần một tháng", "Several times a month"), ("hiếm khi", "Rarely"),
        ("thôi hẳn", "Tried it and stopped")))


def _need_state(row):
    return _pick(row, Q_NEED_STATE, (
        ("yên tĩnh", "Quiet and undisturbed"), ("kiểm soát", "In control"),
        ("bầu bạn", "Accompanied"), ("đi nhanh", "Fast and done"),
        ("giải trí", "Entertained")))


def _cabin_context(row):
    """Most constraining tick wins: hands and eyes bind harder than talking."""
    answer = _answer(row, Q_CABIN_CTX)
    if not answer:
        return None
    for fragment, value in (
        ("hai tay", "Hands on wheel"), ("nhìn gương", "Watching the road"),
        ("tìm địa chỉ", "Searching on phone"), ("ăn uống", "Eating or drinking"),
        ("nói chuyện", "Talking to a passenger"), ("không bận", "Not occupied"),
    ):
        if fragment in answer:
            return value
    return None


def _cabin_noise(row):
    return _scale5(row, Q_CABIN_NOISE, (
        "Very quiet", "Quiet", "Moderate", "Loud", "Very loud"))


CROSSWALK = {
    "demo_driver_status": {"compute": _driver_status, "prov": "observed"},
    "lstyle_commute_mode": {"compute": _commute_mode, "prov": "observed"},
    "skill_driving": {"compute": _skill_driving, "prov": "observed"},
    "cog_patience": {"compute": _patience, "prov": "observed"},
    "cog_skepticism": {"compute": _skepticism, "prov": "observed"},
    "topic_cars": {"compute": _topic_cars, "prov": "observed"},
    "att_electric_vehicles": {"compute": _ev_attitude, "prov": "observed"},
    "att_self_driving_cars": {"compute": _self_driving_attitude, "prov": "observed"},
    # Optional block: skip these questions when the language layer comes from
    # measured forum text instead, which is more reliable than self-report.
    "cog_verbosity": {"compute": _verbosity, "prov": "observed"},
    "vn_address_register": {"compute": _address_register, "prov": "observed"},
    # 2026 expansion. att_voice_assistant is derived from the delegation
    # question rather than asked directly -- see _voice_assistant_attitude.
    "vn_usual_companion": {"compute": _companion, "prov": "observed"},
    "vn_voice_privacy_comfort": {"compute": _voice_privacy_comfort, "prov": "observed"},
    "vn_assistant_task_scope": {"compute": _assistant_task_scope, "prov": "observed"},
    "vn_retry_tolerance": {"compute": _retry_tolerance, "prov": "observed"},
    # "derived", not "observed": the form never asks this. Marking an inference
    # as measured would inflate the one number that says how much of a persona
    # rests on a real answer.
    "att_voice_assistant": {"compute": _voice_assistant_attitude, "prov": "derived"},
    # Second round of the 2026 expansion. All observed: each is a question the
    # respondent answered directly, unlike att_voice_assistant above.
    "accent_region": {"compute": _accent_region, "prov": "observed"},
    "veh_class": {"compute": _veh_class, "prov": "observed"},
    "veh_assistant_builtin": {"compute": _veh_assistant_builtin, "prov": "observed"},
    "drv_exposure": {"compute": _drv_exposure, "prov": "observed"},
    "trip_mix": {"compute": _trip_mix, "prov": "observed"},
    "assistant_usage_freq": {"compute": _assistant_usage_freq, "prov": "observed"},
    "need_state": {"compute": _need_state, "prov": "observed"},
    "cabin_context": {"compute": _cabin_context, "prov": "observed"},
    "cabin_noise": {"compute": _cabin_noise, "prov": "observed"},
}
