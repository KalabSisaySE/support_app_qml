import subprocess

from support_app import installer_verification as verification


def completed(stdout="", returncode=0, stderr=""):
    return subprocess.CompletedProcess(
        args=["powershell"], returncode=returncode, stdout=stdout, stderr=stderr
    )


def test_missing_file_returns_none(tmp_path):
    assert verification.verify_authenticode(str(tmp_path / "missing.exe")) is None


def test_unsupported_platform_returns_none(tmp_path, monkeypatch):
    path = tmp_path / "setup.exe"
    path.write_bytes(b"x")
    monkeypatch.setattr(verification.sys, "platform", "linux")

    assert verification.verify_authenticode(str(path)) is None


def test_valid_signature(tmp_path, monkeypatch):
    path = tmp_path / "setup.exe"
    path.write_bytes(b"x")
    monkeypatch.setattr(verification.sys, "platform", "win32")
    monkeypatch.setattr(
        verification.subprocess, "run", lambda *a, **kw: completed("Valid\n")
    )

    result = verification.verify_authenticode(str(path))

    assert result is not None
    assert result.status == "Valid"
    assert result.is_valid is True


def test_invalid_signature(tmp_path, monkeypatch):
    path = tmp_path / "setup.exe"
    path.write_bytes(b"x")
    monkeypatch.setattr(verification.sys, "platform", "win32")
    monkeypatch.setattr(
        verification.subprocess, "run", lambda *a, **kw: completed("NotSigned\n")
    )

    result = verification.verify_authenticode(str(path))

    assert result is not None
    assert result.status == "NotSigned"
    assert result.is_valid is False


def test_failed_powershell_returns_none(tmp_path, monkeypatch):
    path = tmp_path / "setup.exe"
    path.write_bytes(b"x")
    monkeypatch.setattr(verification.sys, "platform", "win32")
    monkeypatch.setattr(
        verification.subprocess,
        "run",
        lambda *a, **kw: completed("", returncode=1, stderr="boom"),
    )

    assert verification.verify_authenticode(str(path)) is None


def test_powershell_exception_returns_none(tmp_path, monkeypatch):
    path = tmp_path / "setup.exe"
    path.write_bytes(b"x")
    monkeypatch.setattr(verification.sys, "platform", "win32")

    def boom(*args, **kwargs):
        raise OSError("powershell missing")

    monkeypatch.setattr(verification.subprocess, "run", boom)

    assert verification.verify_authenticode(str(path)) is None


def test_log_signature_result(caplog):
    with caplog.at_level("INFO"):
        verification.log_signature_result("ok.exe", verification.SignatureResult("Valid"))
        verification.log_signature_result("bad.exe", verification.SignatureResult("NotSigned"))
        verification.log_signature_result("unknown.exe", None)

    assert "Installer signature is valid: ok.exe" in caplog.text
    assert "status is NotSigned: bad.exe" in caplog.text
    assert "could not be verified: unknown.exe" in caplog.text
