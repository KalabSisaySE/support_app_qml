from support_app.progress import ProgressAggregator


def test_empty_aggregator_is_zero():
    aggregator = ProgressAggregator()

    assert aggregator.average == 0.0
    assert aggregator.is_empty is True


def test_update_returns_average():
    aggregator = ProgressAggregator()

    assert aggregator.update("install", 20) == 20
    assert aggregator.update("permissions", 80) == 50
    assert aggregator.values == {"install": 20, "permissions": 80}
    assert aggregator.is_empty is False


def test_update_replaces_previous_value():
    aggregator = ProgressAggregator()
    aggregator.update("install", 20)
    aggregator.update("install", 100)

    assert aggregator.average == 100
    assert aggregator.values == {"install": 100}


def test_clear_resets_state():
    aggregator = ProgressAggregator()
    aggregator.update("install", 50)

    aggregator.clear()

    assert aggregator.average == 0.0
    assert aggregator.is_empty is True


def test_values_returns_a_snapshot():
    aggregator = ProgressAggregator()
    aggregator.update("install", 50)

    snapshot = aggregator.values
    snapshot["install"] = 0

    assert aggregator.average == 50
