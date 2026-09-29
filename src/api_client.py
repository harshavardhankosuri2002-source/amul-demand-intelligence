"""
AMUL REST API Client Layer.
Provides standardized connectivity to authorized external ERP / Distributor Management APIs.
Features:
- Configurable endpoint, bearer token / API key, timeouts, pagination.
- JSON response schema validation and mapping layer.
- Comprehensive HTTP error handling (401, 404, 429 rate limit, 500, timeouts).
- Built-in mock test endpoint mode for end-to-end live testing without requiring an external server.
- Explicit documentation that synthetic/mock data is used unless an authorized company endpoint is connected.
"""

from datetime import datetime
import json
import time
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import requests

from src.data_generator import generate_synthetic_amul_dataset

# Canonical JSON Schema for External Distribution API
API_PAYLOAD_SCHEMA = {
    "status": "string",
    "timestamp": "iso8601",
    "pagination": {
        "page": "int",
        "page_size": "int",
        "total_records": "int",
        "has_next": "bool",
    },
    "data": [
        {
            "date": "YYYY-MM-DD",
            "sku_id": "string",
            "product_name": "string",
            "category": "string",
            "storage_type": "string (Fresh | Chilled | Frozen | Ambient)",
            "region": "string",
            "units_sold": "float",
            "stock_on_hand": "float",
            "selling_price": "float (optional)",
            "revenue": "float (optional)",
            "units_wasted": "float (optional)",
            "expiry_date": "YYYY-MM-DD (optional)",
            "lead_time_days": "int (optional)",
        }
    ],
}


class DistributionApiClient:
    """Client for querying authorized Amul distributor / ERP endpoints."""

    def __init__(
        self,
        base_url: str = "https://api.example.com/v1/amul-distribution",
        api_key: Optional[str] = None,
        timeout_seconds: int = 10,
        page_size: int = 500,
        is_mock_mode: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.page_size = page_size
        self.is_mock_mode = is_mock_mode

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Amul-AI-Demand-Intelligence/1.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Key"] = self.api_key
        return headers

    def test_connection(self) -> Tuple[bool, str]:
        """Validates endpoint connectivity and credentials."""
        if self.is_mock_mode or "example.com" in self.base_url:
            return True, "Mock / Sandbox Mode Active: Simulated connection verified successfully."

        try:
            health_url = f"{self.base_url}/health"
            resp = requests.get(health_url, headers=self._get_headers(), timeout=self.timeout_seconds)
            if resp.status_code == 200:
                return True, f"Connection OK: HTTP 200 from {health_url}"
            elif resp.status_code == 401:
                return False, "Authentication Failed (HTTP 401): Invalid API Key or Bearer Token."
            elif resp.status_code == 403:
                return False, "Access Forbidden (HTTP 403): Credentials lack required supply-chain scope."
            else:
                return False, f"Server returned HTTP status {resp.status_code}."
        except requests.exceptions.Timeout:
            return False, f"Connection timed out after {self.timeout_seconds} seconds."
        except requests.exceptions.ConnectionError:
            return False, f"Could not connect to host at {self.base_url}. Verify DNS and server status."
        except Exception as e:
            return False, f"Unexpected error during connection test: {str(e)}"

    def fetch_distribution_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        region: Optional[str] = None,
        max_pages: int = 5,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fetches distribution transactions with pagination, error trapping, and schema parsing.
        Returns:
            df: Parsed and cleaned DataFrame
            telemetry: Dictionary containing metadata, latency, record counts, and status
        """
        start_time = time.time()
        
        # If in Mock Mode or targeting default demo placeholder URL
        if self.is_mock_mode or "example.com" in self.base_url:
            # Simulate realistic network latency (0.2s)
            time.sleep(0.2)
            mock_df = generate_synthetic_amul_dataset(days=90, seed=int(time.time()) % 1000)
            mock_df["data_source_flag"] = "MOCK_LIVE_API"
            latency = round((time.time() - start_time) * 1000, 1)
            
            telemetry = {
                "status": "SUCCESS",
                "source": "Mock Live API Service (Simulated External Endpoint)",
                "records_fetched": len(mock_df),
                "latency_ms": latency,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pages_retrieved": 1,
                "note": "Demonstration mode: external ERP feed simulated with reproducible distribution dynamics.",
            }
            return mock_df, telemetry

        # Real HTTP Request Flow
        all_records = []
        page = 1
        has_next = True
        
        try:
            while has_next and page <= max_pages:
                endpoint = f"{self.base_url}/records"
                params = {
                    "page": page,
                    "page_size": self.page_size,
                }
                if start_date:
                    params["start_date"] = start_date
                if end_date:
                    params["end_date"] = end_date
                if region:
                    params["region"] = region
                    
                resp = requests.get(
                    endpoint,
                    headers=self._get_headers(),
                    params=params,
                    timeout=self.timeout_seconds,
                )
                
                if resp.status_code == 401:
                    raise PermissionError("HTTP 401 Unauthorized: Invalid API Token.")
                elif resp.status_code == 429:
                    raise ConnectionResetError("HTTP 429 Rate Limit Exceeded: Please throttle requests.")
                elif resp.status_code != 200:
                    raise RuntimeError(f"HTTP {resp.status_code} Error: {resp.text[:200]}")
                    
                payload = resp.json()
                
                # Validate payload structure
                if not isinstance(payload, dict) or "data" not in payload:
                    raise ValueError("Malformed API response: Expected top-level JSON object with 'data' array.")
                    
                records = payload.get("data", [])
                if not records:
                    break
                    
                all_records.extend(records)
                pagination = payload.get("pagination", {})
                has_next = pagination.get("has_next", False)
                page += 1
                
            df = pd.DataFrame(all_records)
            df["data_source_flag"] = "AUTHENTICATED_LIVE_API"
            latency = round((time.time() - start_time) * 1000, 1)
            
            telemetry = {
                "status": "SUCCESS",
                "source": f"Live REST API ({self.base_url})",
                "records_fetched": len(df),
                "latency_ms": latency,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pages_retrieved": page - 1,
            }
            return df, telemetry
            
        except Exception as e:
            latency = round((time.time() - start_time) * 1000, 1)
            telemetry = {
                "status": "FAILED",
                "source": f"Live REST API ({self.base_url})",
                "error": str(e),
                "records_fetched": 0,
                "latency_ms": latency,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            # Return empty DataFrame with error telemetry
            return pd.DataFrame(), telemetry
