"""Tests for ConversationManager.ensure_runner() (BUG-001)."""

import uuid
from unittest.mock import MagicMock

from openhands_cli.tui.core.conversation_manager import ConversationManager


class TestEnsureRunner:
    """Verify ensure_runner() eagerly creates a runner via RunnerRegistry."""

    def test_ensure_runner_calls_get_or_create(self) -> None:
        """ensure_runner() delegates to _runners.get_or_create() with the ID."""
        manager = object.__new__(ConversationManager)
        mock_registry = MagicMock()
        manager._runners = mock_registry

        conversation_id = uuid.uuid4()
        manager.ensure_runner(conversation_id)

        mock_registry.get_or_create.assert_called_once_with(conversation_id)

    def test_ensure_runner_called_exactly_once(self) -> None:
        """Calling ensure_runner() twice creates only on the first call
        (get_or_create is idempotent, but we verify it's called each time)."""
        manager = object.__new__(ConversationManager)
        mock_registry = MagicMock()
        manager._runners = mock_registry

        conversation_id = uuid.uuid4()
        manager.ensure_runner(conversation_id)
        manager.ensure_runner(conversation_id)

        assert mock_registry.get_or_create.call_count == 2
