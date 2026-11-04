import pytest

from gradio_timesegments import TimeSegments
from gradio_timesegments.timesegments import to_seconds, format_hms


@pytest.mark.parametrize("raw, expected", [
    (0, 0), (150, 150), (12.9, 12), ("150", 150), ("02:30", 150), ("1:02:30", 3750), (" 00:00:07 ", 7),
    (None, None), ("", None),
])
def test_to_seconds(raw, expected):
    assert to_seconds(raw) == expected


@pytest.mark.parametrize("raw", ["abc", "1:2:3:4", "-5", -5, "1:-2", True])
def test_to_seconds_rejects(raw):
    with pytest.raises(ValueError):
        to_seconds(raw)


def test_format_hms():
    assert format_hms(3750) == "01:02:30"
    assert format_hms(None) == "end"


def test_default_value_is_one_segment_to_the_end():
    assert TimeSegments(render=False).value == [[0, None]]


@pytest.mark.parametrize("payload, expected", [
    ([[0, 5], [10, None]], [(0, 5), (10, None)]),
    ([[1.7, 3.2]], [(1, 3)]),  # floats from the browser become ints
    ([[5, 0]], [(5, None)]),  # end 0 = until the end
    ([[None, 4]], [(0, 4)]),  # empty start = 0
    ([], []),
    (None, []),
])
def test_preprocess(payload, expected):
    assert TimeSegments(render=False).preprocess(payload) == expected


def test_preprocess_rejects_malformed_segment():
    with pytest.raises(ValueError):
        TimeSegments(render=False).preprocess([[1, 2, 3]])


@pytest.mark.parametrize("value, expected", [
    ([("00:02:30", None)], [[150, None]]),
    ([(150, "00:03:00")], [[150, 180]]),
    ([[0, None]], [[0, None]]),
    (None, []),
])
def test_postprocess(value, expected):
    assert TimeSegments(render=False).postprocess(value) == expected


def test_api_and_examples_are_consistent():
    comp = TimeSegments(render=False)
    assert comp.api_info()["type"] == "array"
    assert comp.preprocess(comp.example_payload()) == [(0, 5), (10, None)]
    assert comp.postprocess(comp.example_value()) == [[0, 5], [10, None]]


def test_options_reach_the_browser():
    config = TimeSegments(max_segments=1, maximum=603.5, label="Segment", render=False).get_config()
    assert config["max_segments"] == 1
    assert config["maximum"] == 603.5
    assert config["label"] == "Segment"


def test_max_segments_must_be_positive():
    with pytest.raises(ValueError):
        TimeSegments(max_segments=0, render=False)


def test_built_frontend_is_shipped():
    # the compiled JS is committed: installing the app must not need Node
    from pathlib import Path
    import gradio_timesegments
    templates = Path(gradio_timesegments.__file__).parent / "templates"
    for part in ("component", "example"):
        assert (templates / part / "index.js").is_file(), f"run `gradio cc build` ({part} missing)"
