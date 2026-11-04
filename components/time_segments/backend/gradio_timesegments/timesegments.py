from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from gradio.components.base import Component, FormComponent
from gradio.events import Events

if TYPE_CHECKING:
    from gradio.components import Timer

Segment = tuple[int, "int | None"]


def to_seconds(value: Any) -> int | None:
    """
    Seconds from a number or an "HH:MM:SS" / "MM:SS" / "SS" string.
    None for an empty value; ValueError for anything else.
    """
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ValueError(f"invalid time {value!r}")
    if isinstance(value, (int, float)):
        if value < 0:
            raise ValueError(f"negative time {value!r}")
        return int(value)
    parts = str(value).strip().split(":")
    if not 1 <= len(parts) <= 3 or not all(p.strip().isdigit() for p in parts):
        raise ValueError(f"invalid time {value!r}")
    seconds = 0
    for p in parts:
        seconds = seconds * 60 + int(p)
    return seconds


def format_hms(seconds: int | None) -> str:
    if seconds is None:
        return "end"
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


class TimeSegments(FormComponent):
    """
    List of (start, end) time segments, each time typed in a segmented hh:mm:ss field
    (click on a part, type digits). An empty end means "until the end of the video".
    """

    EVENTS = [
        Events.change,
        Events.input,
    ]

    def __init__(
        self,
        value: Sequence[Sequence[Any]] | Callable | None = None,
        *,
        max_segments: int | None = None,
        maximum: float | None = None,
        label: str | None = None,
        info: str | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | None = None,
    ):
        """
        Parameters:
            value: default segments as (start, end) pairs, in seconds or "HH:MM:SS". Default: one segment from 0 to the end.
            max_segments: maximum number of segments (1 hides the add/remove buttons). None for no limit.
            maximum: duration of the media in seconds: times are capped to it and it is displayed. None if unknown.
            label: the label for this component.
            info: additional component description.
            every: see gradio components.
            inputs: see gradio components.
            show_label: if True, will display label.
            scale: relative size compared to adjacent Components.
            min_width: minimum pixel width.
            interactive: if True, segments can be edited.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM.
            render: If False, component will not render be rendered in the Blocks context.
            key: if assigned, will be used to assume identity across a re-render.
        """
        if max_segments is not None and max_segments < 1:
            raise ValueError("max_segments must be >= 1")
        self.max_segments = max_segments
        self.maximum = maximum
        super().__init__(
            label=label,
            info=info,
            every=every,
            inputs=inputs,
            show_label=show_label,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            value=[(0, None)] if value is None else value,
            render=render,
            key=key,
        )

    @staticmethod
    def _segment(item: Any) -> Segment:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"a segment is a (start, end) pair, got {item!r}")
        start = to_seconds(item[0]) or 0
        end = to_seconds(item[1]) or None  # 0 / empty: until the end of the video
        return start, end

    def preprocess(self, payload: list[list[Any]] | None) -> list[Segment]:
        """
        Parameters:
            payload: list of [start, end] in seconds sent by the browser.
        Returns:
            Passes the segments as a list of (start, end) tuples of ints; end is None for "until the end".
        """
        return [self._segment(item) for item in payload or []]

    def postprocess(self, value: Sequence[Sequence[Any]] | None) -> list[list[int | None]]:
        """
        Parameters:
            value: segments as (start, end) pairs, in seconds or "HH:MM:SS"; end None for "until the end".
        Returns:
            The segments as [start, end] lists of seconds.
        """
        return [list(self._segment(item)) for item in value or []]

    def api_info(self) -> dict[str, Any]:
        return {
            "type": "array",
            "items": {"type": "array", "items": {"type": "integer"}},
            "description": "list of [start, end] in seconds; end 0 or null means until the end",
        }

    def example_payload(self) -> Any:
        return [[0, 5], [10, None]]

    def example_value(self) -> Any:
        return [(0, 5), ("00:00:10", None)]
