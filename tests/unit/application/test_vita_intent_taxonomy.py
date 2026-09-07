import pytest

from application.scripts.vita_intent_taxonomy import (
    SUBINTENT_BY_LABEL_VI,
    UnknownSubintentError,
    subintent_entry,
)


def test_covers_exactly_sixty_labels():
    assert len(SUBINTENT_BY_LABEL_VI) == 60


def test_codes_are_unique():
    codes = [code for code, _ in SUBINTENT_BY_LABEL_VI.values()]
    assert len(set(codes)) == 60


def test_codes_are_ascii_snake_case():
    for code, parent in SUBINTENT_BY_LABEL_VI.values():
        for value in (code, parent):
            assert value.isascii(), value
            assert value == value.lower(), value
            assert " " not in value, value


def test_known_pair_from_demo_dataset():
    assert subintent_entry("Tìm điểm đến/POI") == ("destination_poi", "journey_navigation_places")


def test_manually_added_pair():
    assert subintent_entry("Unsupported intent") == ("unsupported_intent", "fallback_handling")


def test_label_is_trimmed_before_lookup():
    assert subintent_entry("  Điều hòa  ") == ("climate", "cabin_vehicle_control")


def test_unknown_label_raises():
    with pytest.raises(UnknownSubintentError):
        subintent_entry("Không tồn tại")
