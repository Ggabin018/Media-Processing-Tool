"""Build the Gradio UI (without launching it) and check how events are wired."""
import inspect

import gradio as gr
import pytest

from front_end.gradio_manager import GradioManager


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


def test_middle_end_handlers_match_gradio_outputs(handlers):
    # with empty fields every middle_end handler must answer with as many values as outputs, never raise
    middle = [bf for bf in handlers if bf.fn.__module__.startswith("middle_end")]
    assert middle
    for bf in middle:
        result = bf.fn(*[empty_value(c) for c in bf.inputs])
        n = len(bf.outputs)
        if n == 0:
            assert result is None, name(bf)
        elif n == 1:
            assert isinstance(result, str), f"{name(bf)} returned {result!r}"
        else:
            assert isinstance(result, tuple) and len(result) == n, f"{name(bf)} returned {result!r} for {n} outputs"
            assert isinstance(result[0], str), name(bf)
