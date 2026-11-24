import json

from support_app.upload_queue import UploadQueue


def make_queue(tmp_path, send=lambda payload: None):
    return UploadQueue(str(tmp_path / "queue.json"), send=send)


def test_enqueue_persists_payloads(tmp_path):
    queue = make_queue(tmp_path)

    queue.enqueue({"class_id": 1})
    queue.enqueue({"class_id": 2})

    assert queue.pending() == [{"class_id": 1}, {"class_id": 2}]
    assert json.loads((tmp_path / "queue.json").read_text(encoding="utf-8")) == [
        {"class_id": 1},
        {"class_id": 2},
    ]


def test_flush_removes_sent_items(tmp_path):
    sent = []
    queue = make_queue(tmp_path, send=sent.append)
    queue.enqueue({"class_id": 1})
    queue.enqueue({"class_id": 2})

    assert queue.flush() == (2, 0)
    assert sent == [{"class_id": 1}, {"class_id": 2}]
    assert queue.pending() == []


def test_flush_keeps_failed_items(tmp_path):
    def send(payload):
        if payload["class_id"] == 2:
            raise RuntimeError("offline")

    queue = make_queue(tmp_path, send=send)
    queue.enqueue({"class_id": 1})
    queue.enqueue({"class_id": 2})

    assert queue.flush() == (1, 1)
    assert queue.pending() == [{"class_id": 2}]


def test_corrupt_queue_is_empty(tmp_path):
    path = tmp_path / "queue.json"
    path.write_text("{not json", encoding="utf-8")
    queue = UploadQueue(str(path))

    assert queue.pending() == []


def test_malformed_entries_are_ignored(tmp_path):
    path = tmp_path / "queue.json"
    path.write_text(json.dumps([{"ok": 1}, "bad", 3]), encoding="utf-8")
    queue = UploadQueue(str(path))

    assert queue.pending() == [{"ok": 1}]
