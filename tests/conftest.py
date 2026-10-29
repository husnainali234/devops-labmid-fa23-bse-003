import pytest

from app.app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(storage_path=str(tmp_path / "submissions.json"))
    app.config["TESTING"] = True
    return app.test_client()
