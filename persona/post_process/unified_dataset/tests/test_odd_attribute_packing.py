"""Packing must survive an odd ATTRIBUTE_COUNT.

Two 4-bit codes share a byte. At 1290 the halves were the same length, so
``codes[0::2] | (codes[1::2] << 4)`` happened to work; the first odd dimension
count (1291, when ``vn_address_register`` was added) broke it with a broadcast
error. Encode/decode has to round-trip either way.
"""

from __future__ import annotations

import numpy as np
import pytest

from persona.post_process.unified_dataset import schema as schema_mod


def _codec(count: int) -> schema_mod.AttributeCodec:
    """A codec over ``count`` dimensions, each with the same three values."""
    return schema_mod.AttributeCodec(
        field_ids=tuple("dim_{}".format(i) for i in range(count)),
        value_codes=tuple({"A": 0, "B": 1, "C": 2} for _ in range(count)),
    )


@pytest.mark.parametrize("count", [1290, 1291])
def test_pack_round_trips_for_even_and_odd_counts(monkeypatch, count):
    monkeypatch.setattr(schema_mod, "ATTRIBUTE_COUNT", count)
    monkeypatch.setattr(schema_mod, "ATTRIBUTE_BYTES", (count + 1) // 2)
    codec = _codec(count)

    values = {"dim_{}".format(i): "ABC"[i % 3] for i in range(count)}
    packed, nulls, overrides = codec.encode_mapping(values)

    assert overrides is None
    assert nulls is None
    assert len(packed) == (count + 1) // 2

    decoded = codec.decode_row(packed, nulls)
    assert len(decoded) == count
    assert decoded["dim_0"] == "A"
    assert decoded["dim_{}".format(count - 1)] == "ABC"[(count - 1) % 3]


def test_odd_count_last_dimension_survives(monkeypatch):
    """The dimension sitting in the unpaired final nibble is the one at risk."""
    count = 1291
    monkeypatch.setattr(schema_mod, "ATTRIBUTE_COUNT", count)
    monkeypatch.setattr(schema_mod, "ATTRIBUTE_BYTES", (count + 1) // 2)
    codec = _codec(count)

    values = {"dim_{}".format(i): "A" for i in range(count)}
    values["dim_1290"] = "C"

    packed, nulls, _ = codec.encode_mapping(values)

    assert codec.decode_row(packed, nulls)["dim_1290"] == "C"


def test_packed_width_matches_declared_bytes():
    assert schema_mod.ATTRIBUTE_BYTES == (schema_mod.ATTRIBUTE_COUNT + 1) // 2
    assert np.uint8(0).itemsize == 1
