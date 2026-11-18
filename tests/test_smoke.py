"""Smoke tests that verify the project layout is importable."""

import support_app


def test_package_importable():
    assert support_app is not None
