import support_app.one_click as one_click
from support_app.one_click import OneClickFlow


class FakeSignal:
    def __init__(self):
        self.emitted = []

    def emit(self, *args):
        self.emitted.append(args)


class FakeHost:
    def __init__(self):
        self.logs = []
        self.started_workers = []
        self.installations = []
        self.permissions = []
        self.obs_finished = 0
        self.showDialog = FakeSignal()

        self.is_app_install_btn_enabled = True
        self.is_app_start_btn_enabled = True
        self.is_app_service_btn_enabled = True
        self.is_app_rust_id_btn_enabled = True
        self.is_enable_microphone_only_btn_enabled = True
        self.is_enable_microphone_and_camera_btn_enabled = True
        self.is_obs_install_btn_enabled = True
        self.is_user_lectoure = False

    def add_log(self, message):
        self.logs.append(message)

    def _start_worker(self, **kwargs):
        self.started_workers.append(kwargs)

    def on_installation_finished(self, result_data):
        self.installations.append(result_data)

    def update_permission_status(self, result_data):
        self.permissions.append(result_data)

    def on_obs_installation_finished(self):
        self.obs_finished += 1

    def _on_one_click_install_finished(self, result_data):
        pass

    def _on_one_click_permissions_finished(self, result_data):
        pass

    def _on_one_click_obs_finished(self):
        pass


def test_start_installs_when_missing(monkeypatch):
    monkeypatch.setattr(one_click, "check_installation", lambda: False)
    host = FakeHost()

    OneClickFlow(host).start()

    assert host.started_workers[0]["task_name"] == "one_click_install"
    assert host.is_app_install_btn_enabled is False
    assert host.is_obs_install_btn_enabled is False


def test_start_skips_install_when_present(monkeypatch):
    monkeypatch.setattr(one_click, "check_installation", lambda: True)
    host = FakeHost()

    OneClickFlow(host).start()

    assert host.started_workers[0]["task_name"] == "one_click_permissions"


def test_install_finished_chains_to_permissions(monkeypatch):
    monkeypatch.setattr(one_click, "check_installation", lambda: True)
    host = FakeHost()
    flow = OneClickFlow(host)

    flow.on_install_finished({"app_installed": True})

    assert host.installations == [{"app_installed": True}]
    assert host.started_workers[0]["task_name"] == "one_click_permissions"


def test_client_completes_after_permissions(monkeypatch):
    monkeypatch.setattr(one_click, "check_installation", lambda: True)
    host = FakeHost()
    host.is_user_lectoure = False

    OneClickFlow(host).on_permissions_finished({"is_microphone_allowed": True})

    assert host.permissions == [{"is_microphone_allowed": True}]
    assert host.started_workers == []
    assert host.is_app_install_btn_enabled is True
    assert host.showDialog.emitted[-1][2] is True


def test_lecturer_installs_obs_when_missing(monkeypatch):
    monkeypatch.setattr(one_click, "check_installation", lambda: True)
    monkeypatch.setattr(one_click, "is_obs_installed", lambda: False)
    host = FakeHost()
    host.is_user_lectoure = True

    OneClickFlow(host).on_permissions_finished({})

    assert host.started_workers[0]["task_name"] == "one_click_obs_install"


def test_lecturer_skips_installed_obs(monkeypatch):
    monkeypatch.setattr(one_click, "check_installation", lambda: True)
    monkeypatch.setattr(one_click, "is_obs_installed", lambda: True)
    host = FakeHost()
    host.is_user_lectoure = True

    OneClickFlow(host).on_permissions_finished({})

    assert host.started_workers == []
    assert any("preskakuje" in log for log in host.logs)
    assert host.showDialog.emitted


def test_obs_finished_completes(monkeypatch):
    monkeypatch.setattr(one_click, "check_installation", lambda: True)
    monkeypatch.setattr(one_click, "is_obs_installed", lambda: True)
    host = FakeHost()

    OneClickFlow(host).on_obs_finished()

    assert host.obs_finished == 1
    assert host.showDialog.emitted[-1][2] is True
