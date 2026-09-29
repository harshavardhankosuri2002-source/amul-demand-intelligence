"""
Automated unit tests for REST API integration, error handling,
timeouts, and mock live data streaming.
"""

from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
import requests
from src.api_client import DistributionApiClient


def test_api_client_mock_mode():
    client = DistributionApiClient(is_mock_mode=True)
    ok, msg = client.test_connection()
    assert ok is True
    assert "Mock" in msg
    
    df, telemetry = client.fetch_distribution_data()
    assert not df.empty
    assert telemetry["status"] == "SUCCESS"
    assert "MOCK_LIVE_API" in df["data_source_flag"].values


def test_api_client_handles_unauthorized_401():
    client = DistributionApiClient(base_url="https://api.my-corp-amul.internal/v1", is_mock_mode=False)
    
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    
    with patch("requests.get", return_value=mock_resp):
        df, telemetry = client.fetch_distribution_data()
        assert df.empty
        assert telemetry["status"] == "FAILED"
        assert "401" in telemetry["error"]


def test_api_client_handles_timeout():
    client = DistributionApiClient(base_url="https://api.my-corp-amul.internal/v1", timeout_seconds=1, is_mock_mode=False)
    
    with patch("requests.get", side_effect=requests.exceptions.Timeout("Connection timed out")):
        df, telemetry = client.fetch_distribution_data()
        assert df.empty
        assert telemetry["status"] == "FAILED"
        assert "timed out" in telemetry["error"].lower()


def test_api_client_handles_malformed_json():
    client = DistributionApiClient(base_url="https://api.my-corp-amul.internal/v1", is_mock_mode=False)
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = ["malformed", "not a dict with data"]
    
    with patch("requests.get", return_value=mock_resp):
        df, telemetry = client.fetch_distribution_data()
        assert df.empty
        assert telemetry["status"] == "FAILED"
        assert "Malformed" in telemetry["error"]
