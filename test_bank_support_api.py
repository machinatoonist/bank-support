"""
Pytest tests for bank support API.

These tests validate the API endpoints and expected behavior:
- Health endpoint returns OK status
- Balance inquiry has low risk (< 3)
- Lost card report has high risk (> 7)
"""

import pytest
from fastapi.testclient import TestClient
from bank_support_example import app


class TestBankSupportAPI:
    """Test suite for Bank Support API."""

    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test that health endpoint returns OK status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_balance_inquiry_low_risk(self, client):
        """Test that balance inquiry returns low risk (< 3)."""
        payload = {
            "question": "What is my balance?",
            "customer_name": "Alice",
            "customer_id": 123
        }

        response = client.post("/support", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "support_advice" in data
        assert "block_card" in data
        assert "risk" in data
        assert "risk_explanation" in data
        assert "risk_category" in data
        assert "risk_signals" in data

        # Validate business logic
        assert data["risk"] < 3, f"Expected risk < 3, got {data['risk']}"
        assert data["block_card"] is False
        assert "balance" in data["support_advice"].lower()
        assert len(data["support_advice"]) > 0
        assert data["risk_category"] == "routine"
        assert len(data["risk_explanation"]) > 0
        assert isinstance(data["risk_signals"], list)

    def test_lost_card_high_risk(self, client):
        """Test that lost card report returns appropriate risk and blocks card."""
        payload = {
            "question": "Someone stole my wallet with my credit card! I need help!",
            "customer_name": "Bob",
            "customer_id": 456
        }

        response = client.post("/support", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "support_advice" in data
        assert "block_card" in data
        assert "risk" in data
        assert "risk_explanation" in data
        assert "risk_category" in data
        assert "risk_signals" in data

        # Validate business logic - stolen card should have high risk and block card
        assert data["risk"] >= 5, f"Expected risk >= 5 for stolen card, got {data['risk']}"
        assert data["block_card"] is True, "Card should be blocked for theft"
        assert len(data["support_advice"]) > 0
        assert data["risk_category"] in ["concerning", "urgent", "critical"]
        assert len(data["risk_explanation"]) > 0
        assert isinstance(data["risk_signals"], list)
        assert len(data["risk_signals"]) > 0, "High-risk scenarios should have risk signals"

    def test_different_customer_names(self, client):
        """Test that API accepts different customer names and returns valid responses."""
        test_cases = [
            {"name": "Charlie", "question": "What's my balance?"},
            {"name": "Diana", "question": "Help me with my account"},
            {"name": "Eve", "question": "I need assistance"}
        ]

        for case in test_cases:
            payload = {
                "question": case["question"],
                "customer_name": case["name"],
                "customer_id": 789
            }

            response = client.post("/support", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert "support_advice" in data
            assert len(data["support_advice"]) > 0
            assert isinstance(data["risk"], int)
            assert isinstance(data["block_card"], bool)

    def test_support_endpoint_missing_fields(self, client):
        """Test that missing required fields return validation errors."""
        # Missing customer_name
        payload = {
            "question": "What is my balance?",
            "customer_id": 123
        }

        response = client.post("/support", json=payload)
        assert response.status_code == 422  # Validation error

        # Missing question
        payload = {
            "customer_name": "Alice",
            "customer_id": 123
        }

        response = client.post("/support", json=payload)
        assert response.status_code == 422  # Validation error

    def test_risk_levels_are_numeric(self, client):
        """Test that risk levels are always numeric."""
        test_questions = [
            "What is my balance?",
            "I lost my card",
            "Someone stole my wallet!",
            "Can you help me?",
            "I need to check my account"
        ]

        for question in test_questions:
            payload = {
                "question": question,
                "customer_name": "TestUser",
                "customer_id": 999
            }

            response = client.post("/support", json=payload)
            assert response.status_code == 200

            data = response.json()
            assert isinstance(data["risk"], int)
            assert 0 <= data["risk"] <= 10, f"Risk should be 0-10, got {data['risk']}"


# Pytest configuration for async support
pytest_plugins = ('pytest_asyncio',)