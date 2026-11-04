"""Build the Gradio UI (without launching it) and check how events are wired."""
import inspect

import gradio as gr
import pytest
from gradio_timesegments import TimeSegments

from conftest import VIDEOS
from front_end.gradio_manager import GradioManager, segment_limits


@pytest.fixture(scope="module")
def handlers():
    gm = GradioManager()
    return list(gm.interface.fns.values())


def name(bf):
    return f"{bf.fn.__module__}.{bf.fn.__name__}"


def empty_value(component):
    """Value Gradio would send for an untouched component."""
    if isinstance(component, gr.Dataframe):
        return [[""]]
    if isinstance(component, gr.Checkbox):
        return False
    if isinstance(component, gr.Dropdown):
        return None
    if isinstance(component, TimeSegments):
        return []
    return ""


def test_ui_builds(handlers):
    assert handlers


def test_handlers_accept_their_inputs(handlers):
    for bf in handlers:
        try:
            inspect.signature(bf.fn).bind(*[None] * len(bf.inputs))
        except TypeError as e:
            pytest.fail(f"{name(bf)} cannot take {len(bf.inputs)} inputs: {e}")


def test_file_pickers_write_back_into_their_field(handlers):
    # 📂 buttons: the chosen path must go into the text field it reads, not into the button itself
    pickers = [bf for bf in handlers if bf.fn.__module__ == "toolbox.tkinter_getters"]
    assert pickers
    for bf in pickers:
        assert len(bf.inputs) == 1 and len(bf.outputs) == 1, name(bf)
        assert bf.outputs[0] is bf.inputs[0], f"{name(bf)} writes into a {type(bf.outputs[0]).__name__}"
        assert isinstance(bf.outputs[0], (gr.Textbox, gr.Dataframe)), name(bf)


def middle_end_handlers(handlers):
    middle = [bf for bf in handlers if bf.fn.__module__.startswith("middle_end")]
    assert middle
    return middle


def test_middle_end_handlers_stream_into_one_result(handlers):
    # with empty fields every handler streams text into its single Result field and never raises
    for bf in middle_end_handlers(handlers):
        assert len(bf.outputs) == 1 and isinstance(bf.outputs[0], gr.Textbox), name(bf)
        assert inspect.isgeneratorfunction(inspect.unwrap(bf.fn)), f"{name(bf)} is not a generator"
        values = list(bf.fn(*[empty_value(c) for c in bf.inputs], progress=None))
        assert values and all(isinstance(v, str) for v in values), f"{name(bf)} yielded {values!r}"


def test_middle_end_handlers_get_gradio_progress(handlers):
    for bf in middle_end_handlers(handlers):
        param = inspect.signature(bf.fn).parameters.get("progress")
        assert param is not None and isinstance(param.default, gr.Progress), name(bf)


def test_heavy_jobs_share_one_queue(handlers):
    for bf in middle_end_handlers(handlers):
        assert bf.concurrency_id == "ffmpeg" and bf.concurrency_limit == 1, name(bf)
    for bf in handlers:
        if not bf.fn.__module__.startswith("middle_end"):
            assert bf.concurrency_id != "ffmpeg", f"{name(bf)} should not wait behind ffmpeg jobs"


def test_no_media_preview_anymore(handlers):
    for bf in handlers:
        assert not any(isinstance(c, (gr.Video, gr.Audio)) for c in bf.outputs), name(bf)


def test_open_buttons_read_a_result_or_directory_field(handlers):
    openers = [bf for bf in handlers if bf.fn.__name__ in ("open_result_file", "open_result_folder", "open_directory")]
    results = {id(c) for bf in middle_end_handlers(handlers) for c in bf.outputs}
    path_inputs = {id(c) for bf in middle_end_handlers(handlers) for c in bf.inputs if isinstance(c, gr.Textbox)}
    assert len([bf for bf in openers if bf.fn.__name__ != "open_directory"]) >= 2 * 6  # 5 Single tabs + concat
    for bf in openers:
        assert len(bf.inputs) == 1 and not bf.outputs, name(bf)
        source = id(bf.inputs[0])
        if bf.fn.__name__ == "open_directory":
            assert source in path_inputs, name(bf)
        else:
            assert source in results, name(bf)


def handler(handlers, fn_name):
    found = [bf for bf in handlers if bf.fn.__name__ == fn_name]
    assert len(found) == 1, fn_name
    return found[0]


@pytest.mark.parametrize("fn_name, max_segments", [("cut_video", 1), ("cut_and_concate", None)])
def test_cut_tabs_use_time_segments(handlers, fn_name, max_segments):
    segments = [c for c in handler(handlers, fn_name).inputs if isinstance(c, TimeSegments)]
    assert len(segments) == 1
    assert segments[0].max_segments == max_segments
    assert not any(isinstance(c, gr.Textbox) and "time" in (c.label or "").lower()
                   for c in handler(handlers, fn_name).inputs)


def test_segment_fields_follow_the_video_duration(handlers):
    limits = [bf for bf in handlers if bf.fn is segment_limits]
    assert len(limits) == 2  # Cut Video + Cut and concatenate
    for bf in limits:
        assert isinstance(bf.inputs[0], gr.Textbox) and isinstance(bf.outputs[0], TimeSegments)
        assert bf.concurrency_id != "ffmpeg"  # instant, never waits behind an encode
    cuts = {id(c) for name in ("cut_video", "cut_and_concate") for c in handler(handlers, name).inputs}
    assert all(id(bf.inputs[0]) in cuts and id(bf.outputs[0]) in cuts for bf in limits)


@pytest.mark.ffmpeg
def test_segment_limits_on_a_real_video():
    update = segment_limits(f'"{VIDEOS / "1.mp4"}"')
    assert update["maximum"] == pytest.approx(10.04, abs=0.01)


@pytest.mark.parametrize("path", ["", "nope.mp4", None])
def test_segment_limits_ignores_invalid_paths(path):
    assert "maximum" not in segment_limits(path)
