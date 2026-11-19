from support_app.status import Status


def test_status_values_are_qml_strings():
    assert Status.ENABLED == "enabled"
    assert Status.DISABLED == "disabled"
    assert Status.CHECKING == "checking"
    assert str(Status.ENABLED) == "enabled"


def test_status_membership():
    assert Status("enabled") is Status.ENABLED
