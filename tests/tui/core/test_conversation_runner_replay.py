"""Tests for ConversationRunner.replay_historical_events()."""

from unittest.mock import MagicMock, patch

import pytest


class TestReplayHistoricalEvents:
    """Tests for the replay_historical_events method on ConversationRunner."""

    @pytest.fixture
    def runner(self):
        """Create a ConversationRunner with mocked dependencies."""
        with patch(
            "openhands_cli.tui.core.conversation_runner.setup_conversation"
        ) as mock_setup:
            mock_conversation = MagicMock()
            mock_conversation.state.events = iter([])
            mock_setup.return_value = mock_conversation

            import uuid

            from openhands_cli.tui.core.conversation_runner import ConversationRunner

            r = ConversationRunner(
                conversation_id=uuid.uuid4(),
                state=MagicMock(),
                message_pump=MagicMock(),
                notification_callback=MagicMock(),
                visualizer=MagicMock(),
            )
            # Replace the conversation mock so tests can set events independently
            r.conversation = mock_conversation
            return r

    def test_replays_all_events_in_order(self, runner):
        """replay_historical_events passes all events to visualizer."""
        events = [MagicMock(name="ev1"), MagicMock(name="ev2"), MagicMock(name="ev3")]
        runner.conversation.state.events = events

        count = runner.replay_historical_events()

        assert count == 3
        runner.visualizer.replay_events.assert_called_once_with(events)

    def test_empty_history_returns_zero(self, runner):
        """No-op for empty histories."""
        runner.conversation.state.events = []

        count = runner.replay_historical_events()

        assert count == 0
        runner.visualizer.replay_events.assert_not_called()

    def test_idempotent_second_call_returns_zero(self, runner):
        """Second call does not duplicate replay."""
        events = [MagicMock(name="ev1")]
        runner.conversation.state.events = events

        first = runner.replay_historical_events()
        assert first == 1

        # Second call should be a no-op
        second = runner.replay_historical_events()
        assert second == 0
        # replay_events should have been called exactly once
        assert runner.visualizer.replay_events.call_count == 1

    def test_flag_set_even_with_empty_events(self, runner):
        """The idempotence flag should be set even when there are no events."""
        runner.conversation.state.events = []

        runner.replay_historical_events()
        assert runner._historical_events_replayed is True

        # Even with events now available, the second call is a no-op
        runner.conversation.state.events = [MagicMock()]
        assert runner.replay_historical_events() == 0
