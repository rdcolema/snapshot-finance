from unittest.mock import patch

from ai.services.client import get_client, is_available


class TestAIClient:
    def test_not_available_without_key(self):
        with patch("ai.services.client.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = ""
            assert is_available() is False

    def test_available_with_key(self):
        with patch("ai.services.client.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            assert is_available() is True

    def test_get_client_returns_none_without_key(self):
        with patch("ai.services.client.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = ""
            assert get_client() is None

    @patch("ai.services.client.Anthropic")
    def test_get_client_returns_client_with_key(self, mock_anthropic):
        with patch("ai.services.client.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            client = get_client()
            mock_anthropic.assert_called_once_with(api_key="test-key")
            assert client is not None
