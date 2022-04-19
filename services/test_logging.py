from . import logging


def test_timestamper_timestamp_debug_mode():
    event_dict = {"event": "some logging"}
    assert logging.timestamper(None, None, event_dict) == event_dict


def test_timestamper_timestamp_production_mode():
    event_dict = {"event": "some logging"}
    logging.DEBUG = True
    assert "timestamp" in logging.timestamper(None, None, event_dict)
