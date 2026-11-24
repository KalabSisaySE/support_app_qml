import zipfile

from support_app.diagnostics import build_summary, create_diagnostics_archive


def test_build_summary_preserves_order():
    summary = build_summary({"App version": "1.0.0", "Platform": "Windows"})

    assert summary == "App version: 1.0.0\nPlatform: Windows\n"


def test_archive_contains_summary_and_logs(tmp_path):
    log = tmp_path / "support_app.log"
    log.write_text("line one\n", encoding="utf-8")
    missing = tmp_path / "missing.log"

    archive_path = create_diagnostics_archive(
        str(tmp_path / "out"),
        build_summary({"App version": "1.0.0"}),
        log_files=[str(log), str(missing)],
    )

    assert archive_path.endswith(".zip")
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        assert "summary.txt" in names
        assert "support_app.log" in names
        assert "missing.log" not in names
        assert archive.read("summary.txt").decode() == "App version: 1.0.0\n"


def test_archive_without_logs(tmp_path):
    archive_path = create_diagnostics_archive(
        str(tmp_path / "out"), build_summary({"App version": "1.0.0"})
    )

    with zipfile.ZipFile(archive_path) as archive:
        assert archive.namelist() == ["summary.txt"]
