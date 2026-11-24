import support_app.rtmp_url_manager as rtmp
from support_app.rtmp_url_manager import RtmpUrlGenerator


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code

    def json(self):
        return {"status": self.status_code}


def make_generator():
    generator = object.__new__(RtmpUrlGenerator)
    generator.lectoure_data = {"class_type": "lecture", "class_id": 5, "room_id": 9}
    generator.video_data = {"uuid": "video-uuid"}
    generator.cloudflare_headers = {}
    return generator


def test_upload_success_is_not_queued(monkeypatch):
    queued = []
    monkeypatch.setattr(rtmp.api, "post", lambda *a, **kw: FakeResponse(200))
    monkeypatch.setattr(rtmp, "enqueue_upload", queued.append)

    assert make_generator().upload_recording_to_vimeo() is True
    assert queued == []


def test_http_failure_is_queued(monkeypatch):
    queued = []
    monkeypatch.setattr(rtmp.api, "post", lambda *a, **kw: FakeResponse(503))
    monkeypatch.setattr(rtmp, "enqueue_upload", queued.append)

    assert make_generator().upload_recording_to_vimeo() is False
    assert queued == [{"class_type": "lecture", "class_id": 5, "room_id": 9}]


def test_exception_is_queued(monkeypatch):
    queued = []

    def boom(*args, **kwargs):
        raise OSError("offline")

    monkeypatch.setattr(rtmp.api, "post", boom)
    monkeypatch.setattr(rtmp, "enqueue_upload", queued.append)

    assert make_generator().upload_recording_to_vimeo() is False
    assert queued == [{"class_type": "lecture", "class_id": 5, "room_id": 9}]


def test_missing_lecture_data_skips_upload(monkeypatch):
    queued = []
    monkeypatch.setattr(rtmp, "enqueue_upload", queued.append)
    generator = make_generator()
    generator.video_data = None

    assert generator.upload_recording_to_vimeo() is False
    assert queued == []
