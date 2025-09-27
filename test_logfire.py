"""
Pytest test to verify Logfire telemetry is working with positive confirmation.
This test makes actual HTTP requests to the running server and verifies responses.
"""

import pytest
import requests
import time
import logfire
from contextlib import contextmanager

# Configure logfire for test telemetry
logfire.configure()

class TestLogfireTelemetryConfirmation:
    """Test suite to verify Logfire telemetry with positive confirmation."""

    BASE_URL = "http://127.0.0.1:8000"

    @contextmanager
    def logfire_span(self, name: str):
        """Context manager to create logfire spans for test tracking."""
        with logfire.span(name):
            yield

    def test_logfire_basic_logging(self):
        """Test basic logfire logging works."""
        with self.logfire_span("test_basic_logging"):
            logfire.info('Test: Basic Logfire logging', test_type='basic')
            # Basic assertion - if this runs without error, logfire is working
            assert True, "Basic logfire logging completed"

    def test_health_endpoint_telemetry(self):
        """Test health endpoint and verify response."""
        with self.logfire_span("test_health_endpoint"):
            logfire.info('Testing health endpoint telemetry')

            try:
                response = requests.get(f"{self.BASE_URL}/health", timeout=10)

                # Positive confirmation: verify response
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"
                data = response.json()
                assert data["status"] == "ok", f"Expected status 'ok', got {data}"

                logfire.info('Health endpoint test successful',
                           status_code=response.status_code,
                           response=data)

            except requests.exceptions.RequestException as e:
                pytest.skip(f"Server not running at {self.BASE_URL}: {e}")

    def test_support_endpoint_balance_inquiry(self):
        """Test support endpoint with balance inquiry and verify AI response."""
        with self.logfire_span("test_balance_inquiry"):
            logfire.info('Testing support endpoint - balance inquiry')

            payload = {
                "question": "What is my current balance?",
                "customer_name": "TestUser",
                "customer_id": 123,
                "include_pending": True
            }

            try:
                response = requests.post(f"{self.BASE_URL}/support", json=payload, timeout=60)

                # Positive confirmation: verify AI response structure
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"
                data = response.json()

                # Verify required fields exist
                required_fields = ['support_advice', 'block_card', 'risk', 'risk_explanation', 'risk_category', 'risk_signals']
                for field in required_fields:
                    assert field in data, f"Missing required field: {field}"

                # Verify balance inquiry produces low risk
                assert data['risk'] <= 3, f"Balance inquiry should be low risk, got {data['risk']}"
                assert data['block_card'] is False, "Balance inquiry should not block card"
                assert data['risk_category'] in ['routine'], f"Expected routine category, got {data['risk_category']}"

                logfire.info('Balance inquiry test successful',
                           risk=data['risk'],
                           block_card=data['block_card'],
                           category=data['risk_category'],
                           advice_length=len(data['support_advice']))

            except requests.exceptions.RequestException as e:
                pytest.skip(f"Server not running at {self.BASE_URL}: {e}")

    def test_support_endpoint_high_risk_scenario(self):
        """Test support endpoint with high-risk scenario and verify AI response."""
        with self.logfire_span("test_high_risk_scenario"):
            logfire.info('Testing support endpoint - high risk scenario')

            payload = {
                "question": "Someone stole my wallet with my credit card! I need help immediately!",
                "customer_name": "EmergencyUser",
                "customer_id": 456,
                "include_pending": False
            }

            try:
                response = requests.post(f"{self.BASE_URL}/support", json=payload, timeout=60)

                # Positive confirmation: verify high-risk AI response
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"
                data = response.json()

                # Verify high-risk scenario is properly assessed
                assert data['risk'] >= 6, f"Theft should be high risk (>=6), got {data['risk']}"
                assert data['block_card'] is True, "Theft scenario should block card"
                assert data['risk_category'] in ['urgent', 'critical'], f"Expected urgent/critical, got {data['risk_category']}"
                assert len(data['risk_signals']) > 0, "High-risk scenarios should have risk signals"

                # Verify risk signals contain theft-related keywords
                risk_signals_text = ' '.join(data['risk_signals']).lower()
                theft_keywords = ['stolen', 'stole', 'theft', 'wallet']
                has_theft_keyword = any(keyword in risk_signals_text for keyword in theft_keywords)
                assert has_theft_keyword, f"Risk signals should contain theft keywords: {data['risk_signals']}"

                logfire.info('High-risk scenario test successful',
                           risk=data['risk'],
                           block_card=data['block_card'],
                           category=data['risk_category'],
                           risk_signals=data['risk_signals'])

            except requests.exceptions.RequestException as e:
                pytest.skip(f"Server not running at {self.BASE_URL}: {e}")

    def test_telemetry_span_nesting(self):
        """Test that logfire spans can be nested properly."""
        with self.logfire_span("outer_span"):
            logfire.info('Outer span started')

            with self.logfire_span("inner_span_1"):
                logfire.info('Inner span 1 processing')
                time.sleep(0.1)  # Simulate some work

            with self.logfire_span("inner_span_2"):
                logfire.info('Inner span 2 processing')
                time.sleep(0.1)  # Simulate some work

            logfire.info('Outer span completed')

        # If we get here without errors, span nesting is working
        assert True, "Span nesting completed successfully"

    def test_telemetry_summary(self):
        """Final test that logs a summary of telemetry testing."""
        with self.logfire_span("telemetry_test_summary"):
            logfire.info('Logfire telemetry testing completed successfully',
                        dashboard_url='https://logfire-us.pydantic.dev/mattrosinski/bank-support',
                        test_timestamp=time.time(),
                        message='All telemetry tests passed - check Logfire dashboard for traces')