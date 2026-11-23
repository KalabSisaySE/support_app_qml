import support_app.account_flow as account_flow
from support_app.account_flow import AccountFlow


class FakeSignal:
    def __init__(self):
        self.emitted = []

    def emit(self, *args):
        self.emitted.append(args)


class FakeHost:
    def __init__(self):
        self.logs = []
        self.started_workers = []
        self.websocket_codes = []
        self.showDialog = FakeSignal()
        self.is_change_account_btn_enabled = True
        self.is_user_lectoure = False
        self.access_code = "OLD"
        self.username = "Old name"
        self._rust_id = "Nenájdené"

    def add_log(self, message):
        self.logs.append(message)

    def _start_worker(self, **kwargs):
        self.started_workers.append(kwargs)

    def setup_websockets(self, code):
        self.websocket_codes.append(code)

    def on_account_auth_finished(self, result_data):
        pass


def test_start_launches_auth_worker():
    host = FakeHost()

    AccountFlow(host).start()

    assert host.is_change_account_btn_enabled is False
    assert host.started_workers[0]["task_name"] == "account_auth"
    assert host.started_workers[0]["start_method_name"] == "start_auth_flow"


def test_successful_login_updates_identity(monkeypatch):
    saved = []
    reported = []
    monkeypatch.setattr(account_flow, "save_login_info", saved.append)
    monkeypatch.setattr(
        account_flow.api, "get", lambda url, **kwargs: reported.append(url)
    )
    host = FakeHost()
    host._rust_id = "123456"

    AccountFlow(host).on_finished(
        {"access_code": "NEW", "is_lectoure": True, "full_name": "Janko"}
    )

    assert host.is_user_lectoure is True
    assert host.access_code == "NEW"
    assert host.username == "Janko"
    assert saved == ["NEW"]
    assert host.websocket_codes == ["NEW"]
    assert reported and "rustdesk=123456" in reported[0]
    assert host.showDialog.emitted[-1][2] is True
    assert host.is_change_account_btn_enabled is True


def test_successful_login_skips_rustdesk_report_without_id(monkeypatch):
    reported = []
    monkeypatch.setattr(
        account_flow.api, "get", lambda url, **kwargs: reported.append(url)
    )
    host = FakeHost()

    AccountFlow(host).on_finished({"access_code": "NEW", "is_lectoure": False})

    assert reported == []
    assert host.is_user_lectoure is False


def test_failed_login_restores_button(monkeypatch):
    saved = []
    monkeypatch.setattr(account_flow, "save_login_info", saved.append)
    host = FakeHost()

    AccountFlow(host).on_finished({})

    assert saved == []
    assert host.websocket_codes == []
    assert host.showDialog.emitted[-1][2] is False
    assert host.is_change_account_btn_enabled is True
