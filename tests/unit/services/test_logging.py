from datetime import datetime

from services.logging import timestamper


def test_timestamper_timestamp_debug_mode(monkeypatch, freezer):
    monkeypatch.setattr("services.logging.DEBUG", True)

    log = timestamper(None, None, {"event": "some logs"})
    assert log == {
        "event": "some logs",
        "timestamp": datetime.now().isoformat() + "Z",
    }


def test_timestamper_timestamp_production_mode(monkeypatch):
    monkeypatch.setattr("services.logging.DEBUG", False)

    assert timestamper(None, None, {"event": "some logs"}) == {"event": "some logs"}
