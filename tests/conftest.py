import pytest

from support_app import app_config


@pytest.fixture(autouse=True)
def _reset_identity():
    """Keep the lazily cached identity from leaking between tests."""
    app_config.reset_identity_cache()
    yield
    app_config.reset_identity_cache()
