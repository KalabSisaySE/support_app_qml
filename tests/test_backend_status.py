from support_app.backend import MacrosoftBackend


class DummyBackend:
    permission_status = None


def update(result):
    backend = DummyBackend()
    MacrosoftBackend.update_permission_status(backend, result)
    return backend.permission_status


def test_permission_status_enabled_when_all_allowed():
    assert update({
        "is_microphone_allowed": True,
        "is_webcam_allowed": True,
        "is_browser_permissions_allowed": True,
    }) == "enabled"


def test_permission_status_checking_when_only_microphone_allowed():
    assert update({
        "is_microphone_allowed": True,
        "is_webcam_allowed": False,
        "is_browser_permissions_allowed": False,
    }) == "checking"


def test_permission_status_disabled_without_microphone():
    assert update({
        "is_microphone_allowed": False,
        "is_webcam_allowed": True,
        "is_browser_permissions_allowed": True,
    }) == "disabled"
