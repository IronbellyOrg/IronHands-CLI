"""Tests for ConversationVisualizer.replay_events() rendering behavior."""

from unittest.mock import MagicMock, patch

import pytest
from textual.app import App
from textual.widgets import Static

from openhands.sdk import MessageEvent, TextContent
from openhands.sdk.event import ObservationEvent
from openhands_cli.tui.widgets.richlog_visualizer import ConversationVisualizer


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_container():
    """Create a mock container that supports mount and scroll_end."""
    container = MagicMock()
    container.is_vertical_scroll_end = False
    return container


@pytest.fixture
def visualizer(mock_container):
    """Create a ConversationVisualizer with mock app and mock container."""
    app = MagicMock(spec=App)
    vis = ConversationVisualizer.__new__(ConversationVisualizer)
    # Manually initialize required attributes to avoid full Textual init
    vis._container = mock_container
    vis._app = app
    vis._name = None
    vis._main_thread_id = 0  # Will not match, but replay_events doesn't check
    vis._cli_settings = None
    vis._pending_actions = {}
    return vis


def _make_user_message_event(text: str) -> MessageEvent:
    """Create a MessageEvent representing a user message."""
    event = MagicMock(spec=MessageEvent)
    event.llm_message = MagicMock()
    event.llm_message.role = "user"
    event.llm_message.content = [MagicMock(spec=TextContent, text=text)]
    event.sender = None
    # Ensure isinstance checks work
    event.__class__ = MessageEvent
    return event


def _make_observation_event(tool_call_id: str = "tc-1") -> ObservationEvent:
    """Create a mock ObservationEvent."""
    event = MagicMock(spec=ObservationEvent)
    event.tool_call_id = tool_call_id
    event.__class__ = ObservationEvent
    return event


# ============================================================================
# T-1: Single user message produces one Static widget
# ============================================================================


class TestReplayRendering:
    """Core rendering tests for replay_events()."""

    def test_single_user_message_produces_static_widget(self, visualizer, mock_container):
        """T-1: A single user message event produces one Static widget with
        CSS class 'user-message' and correct text content."""
        event = _make_user_message_event("Hello world")

        visualizer.replay_events([event])

        assert mock_container.mount.call_count == 1
        widget = mock_container.mount.call_args[0][0]
        assert isinstance(widget, Static)
        assert "user-message" in widget.classes
        assert "Hello world" in str(widget._Static__content)

    def test_observation_event_routes_through_handler(self, visualizer, mock_container):
        """T-2: Observation events route through _handle_observation_event.
        Widget order matches event order."""
        user_event = _make_user_message_event("test input")
        obs_event = _make_observation_event("tc-1")

        with patch.object(
            visualizer, "_handle_observation_event", return_value=True
        ) as mock_handler:
            visualizer.replay_events([user_event, obs_event])

        # User message should produce a mounted widget
        assert mock_container.mount.call_count == 1
        # Observation should have been routed to handler
        mock_handler.assert_called_once_with(obs_event)

    def test_multiple_pairs_render_in_order(self, visualizer, mock_container):
        """T-3: Multiple user/observation pairs render in correct order;
        widget count matches expected."""
        events = [
            _make_user_message_event("first message"),
            _make_observation_event("tc-1"),
            _make_user_message_event("second message"),
            _make_observation_event("tc-2"),
        ]

        with patch.object(
            visualizer, "_handle_observation_event", return_value=True
        ):
            visualizer.replay_events(events)

        # Two user messages should produce two mounted widgets
        assert mock_container.mount.call_count == 2
        # Verify ordering
        first_widget = mock_container.mount.call_args_list[0][0][0]
        second_widget = mock_container.mount.call_args_list[1][0][0]
        assert "first message" in str(first_widget._Static__content)
        assert "second message" in str(second_widget._Static__content)


# ============================================================================
# T-4: Scroll behavior — scroll_end called once after all events
# ============================================================================


class TestReplayScrollBehavior:
    """Scroll behavior tests for replay_events()."""

    def test_scroll_end_called_once_after_all_events(self, visualizer, mock_container):
        """T-4: scroll_end(animate=False) is called exactly once after all events
        are processed, not once per event."""
        events = [
            _make_user_message_event("msg 1"),
            _make_user_message_event("msg 2"),
            _make_user_message_event("msg 3"),
        ]

        visualizer.replay_events(events)

        # replay_events() calls scroll_end(animate=False) once after all events.
        # _add_widget_to_ui also calls scroll_end conditionally (guarded by
        # is_vertical_scroll_end), but with our mock set to False those are
        # suppressed.  So scroll_end should be called exactly once here.
        mock_container.scroll_end.assert_called_once_with(animate=False)


# ============================================================================
# T-5: Empty event list edge case
# ============================================================================


class TestReplayEdgeCases:
    """Edge case tests for replay_events()."""

    def test_empty_event_list_produces_no_widgets(self, visualizer, mock_container):
        """T-5: An empty event list produces no widgets and no exception."""
        visualizer.replay_events([])

        mock_container.mount.assert_not_called()
        # Per implementation: scroll_end is NOT called when events list is empty
        # (the `if events:` guard skips it)
        mock_container.scroll_end.assert_not_called()


# ============================================================================
# T-6, T-7, T-8: Side-effect omission regression guards
# ============================================================================


class TestReplaySideEffectOmissions:
    """Regression guards verifying that replay_events() intentionally omits
    certain side effects that on_event() performs.

    These are negative assertions — they document that the omissions are
    intentional design decisions, not bugs.
    """

    def test_critic_event_not_triggered_during_replay(self, visualizer, mock_container):
        """T-6: Critic handling is intentionally omitted during replay.

        Replay renders historical events for visual display only. Critic
        evaluation is a live-session concern — replaying events should
        never trigger critic analysis of already-completed work.
        """
        events = [_make_user_message_event("please review this")]

        with patch.object(
            visualizer, "_handle_observation_event", return_value=False
        ):
            visualizer.replay_events(events)

        # Verify no critic-related attributes or methods were invoked.
        # The replay code path has no critic references by design.
        # This test guards against future changes that accidentally add them.
        for call in mock_container.method_calls:
            assert "critic" not in str(call).lower(), (
                "Critic side effect detected during replay — intentionally omitted"
            )

    def test_telemetry_not_triggered_during_replay(self, visualizer, mock_container):
        """T-7: Telemetry calls are intentionally omitted during replay.

        Replaying historical events must not re-emit telemetry for events
        that were already tracked during the original session. This prevents
        double-counting and incorrect metrics.
        """
        events = [_make_user_message_event("tracked message")]

        with patch(
            "openhands_cli.tui.widgets.richlog_visualizer.posthog",
            create=True,
        ) as mock_posthog:
            visualizer.replay_events(events)

        # posthog should not be called during replay
        if hasattr(mock_posthog, "capture"):
            mock_posthog.capture.assert_not_called()

    def test_plan_panel_not_refreshed_during_replay(self, visualizer, mock_container):
        """T-8: Plan panel refresh is intentionally omitted during replay.

        During live sessions, certain events trigger plan panel updates.
        During replay, the plan panel state is reconstructed separately —
        replay_events() must not trigger incremental plan panel refreshes.
        """
        events = [_make_user_message_event("create a plan")]

        visualizer.replay_events(events)

        # Verify no plan-panel-related calls on the app or container
        for call in mock_container.method_calls:
            assert "plan" not in str(call).lower(), (
                "Plan panel side effect detected during replay — intentionally omitted"
            )
