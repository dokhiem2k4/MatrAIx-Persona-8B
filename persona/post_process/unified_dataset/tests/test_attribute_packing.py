"""One byte per attribute: round trip, and dimensions wider than 16 values.

The previous layout packed two 4-bit codes per byte. It halved the blob but
capped every dimension at 16 values, which is why ``vn_locality`` could not
name Vietnam's provinces -- there are 34 units and the enum only had room for
15 plus an "Other" bucket. A byte holds 256.

The parity tests that used to live here are gone with the nibble packing: with
a whole byte per attribute an odd ATTRIBUTE_COUNT has nothing special about it.
"""

from __future__ import annotations

import pytest

from persona.post_process.unified_dataset import schema as schema_mod


def _codec(count: int, values_per_dim: int = 3) -> schema_mod.AttributeCodec:
    labels = ["v{}".format(i) for i in range(values_per_dim)]
    return schema_mod.AttributeCodec(
        field_ids=tuple("dim_{}".format(i) for i in range(count)),
        value_codes=tuple({v: i for i, v in enumerate(labels)} for _ in range(count)),
    )


def test_declared_width_is_one_byte_per_attribute():
    assert schema_mod.ATTRIBUTE_BYTES == schema_mod.ATTRIBUTE_COUNT
    assert schema_mod.ATTRIBUTE_VALUE_CEILING == 256


@pytest.mark.parametrize("count", [1291, 1292])
def test_round_trip_for_odd_and_even_counts(monkeypatch, count):
    monkeypatch.setattr(schema_mod, "ATTRIBUTE_COUNT", count)
    monkeypatch.setattr(schema_mod, "ATTRIBUTE_BYTES", count)
    codec = _codec(count)

    values = {"dim_{}".format(i): "v{}".format(i % 3) for i in range(count)}
    packed, nulls, overrides = codec.encode_mapping(values)

    assert overrides is None and nulls is None
    assert len(packed) == count
    decoded = codec.decode_row(packed, nulls)
    assert len(decoded) == count
    assert decoded["dim_0"] == "v0"
    assert decoded["dim_{}".format(count - 1)] == "v{}".format((count - 1) % 3)


def test_dimension_wider_than_sixteen_values_round_trips(monkeypatch):
    """The reason for the change: 4 bits could not hold a 34th province."""
    count = 8
    monkeypatch.setattr(schema_mod, "ATTRIBUTE_COUNT", count)
    monkeypatch.setattr(schema_mod, "ATTRIBUTE_BYTES", count)
    codec = _codec(count, values_per_dim=34)

    values = {"dim_{}".format(i): "v33" for i in range(count)}
    packed, nulls, overrides = codec.encode_mapping(values)

    assert overrides is None
    decoded = codec.decode_row(packed, nulls)
    # Under 4-bit packing code 33 wrapped and decoded as something else.
    assert set(decoded.values()) == {"v33"}


def test_null_dimensions_stay_absent(monkeypatch):
    count = 4
    monkeypatch.setattr(schema_mod, "ATTRIBUTE_COUNT", count)
    monkeypatch.setattr(schema_mod, "ATTRIBUTE_BYTES", count)
    codec = _codec(count)

    packed, nulls, _ = codec.encode_mapping({"dim_0": "v1"})

    decoded = codec.decode_row(packed, nulls)
    assert decoded == {"dim_0": "v1"}


def test_value_outside_the_enum_is_carried_as_an_override(monkeypatch):
    count = 2
    monkeypatch.setattr(schema_mod, "ATTRIBUTE_COUNT", count)
    monkeypatch.setattr(schema_mod, "ATTRIBUTE_BYTES", count)
    codec = _codec(count)

    packed, nulls, overrides = codec.encode_mapping({"dim_0": "not-in-enum"})

    assert overrides == [{"field_index": 0, "value": "not-in-enum"}]
    assert codec.decode_row(packed, nulls, overrides)["dim_0"] == "not-in-enum"
