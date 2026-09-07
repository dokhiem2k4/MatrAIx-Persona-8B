from playground.llm_usage import estimate_completion_cost_usd


class _Usage:
    """Stand-in for the OpenAI SDK usage object.

    ``cost`` is not part of the SDK schema, so pydantic parks OpenRouter's value
    in ``model_extra``; providers that do declare it expose a plain attribute.
    """

    def __init__(self, *, cost=None, model_extra=None):
        if cost is not None:
            self.cost = cost
        self.model_extra = model_extra


class _Completion:
    def __init__(self, usage):
        self.usage = usage


def test_openrouter_usage_cost_is_read_from_model_extra():
    completion = _Completion(_Usage(model_extra={"cost": 6.075e-05}))

    cost, source = estimate_completion_cost_usd(
        model="google/gemini-3.8-flash",
        n_input_tokens=1,
        n_output_tokens=16,
        completion=completion,
    )

    assert cost == 6.075e-05
    assert source == "provider"


def test_usage_cost_attribute_takes_precedence_over_litellm_lookup():
    completion = _Completion(_Usage(cost=0.25))

    cost, source = estimate_completion_cost_usd(
        model="openrouter/anthropic/claude-haiku-4.5",
        n_input_tokens=1000,
        n_output_tokens=500,
        completion=completion,
    )

    assert cost == 0.25
    assert source == "provider"


def test_hidden_params_response_cost_still_wins():
    """litellm-proxy gateways keep reporting through ``_hidden_params``."""
    completion = _Completion(_Usage(model_extra={"cost": 0.99}))
    completion._hidden_params = {"response_cost": 0.5}

    cost, source = estimate_completion_cost_usd(
        model="google/gemini-3.8-flash",
        n_input_tokens=1,
        n_output_tokens=16,
        completion=completion,
    )

    assert cost == 0.5
    assert source == "provider"


def test_zero_or_missing_usage_cost_does_not_invent_a_price():
    for usage in (_Usage(model_extra={"cost": 0.0}), _Usage(), None):
        cost, source = estimate_completion_cost_usd(
            model="model-with-no-pricing-table-entry",
            n_input_tokens=10,
            n_output_tokens=10,
            completion=_Completion(usage),
        )

        assert cost is None
        assert source is None
