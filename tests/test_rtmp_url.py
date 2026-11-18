import string

from support_app.rtmp_url_manager import RtmpUrlGenerator


def bare_generator():
    """Create a generator without running __init__ (which performs network I/O)."""
    return object.__new__(RtmpUrlGenerator)


def test_sanitize_pads_short_names():
    assert bare_generator()._sanitize_video_name("ab") == "ab_"
    assert bare_generator()._sanitize_video_name("a") == "a__"


def test_sanitize_truncates_long_names():
    assert bare_generator()._sanitize_video_name("x" * 30) == "x" * 20


def test_generate_random_name():
    name = bare_generator()._generate_random_name(16)
    assert len(name) == 16
    assert set(name) <= set(string.ascii_lowercase + string.digits)
