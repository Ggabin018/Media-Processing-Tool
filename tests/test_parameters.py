import pytest

from conftest import ROOT
from toolbox.parameters import Params


@pytest.fixture(autouse=True)
def in_tmp_dir(tmp_path, monkeypatch):
    """Never touch the real save.json of the repo."""
    monkeypatch.chdir(tmp_path)


def test_file_exists():
    assert (ROOT / "save.json").exists()


def test_params_create_from_file(tmp_path):
    filename = tmp_path / "save.json"
    filename.write_text('{\n\t"max_workers": "10"\n}')

    params = Params()
    params.load_params_from_json(str(filename))

    assert params.params_dict == {"max_workers": "10"}
    assert params.get_max_workers() == 10


def test_params_get_max_workers_default():
    params = Params()
    params.load_params_from_json("")

    assert params.get_max_workers() == 5
    assert params.params_dict == {}


def test_params_save_then_load(tmp_path):
    filename = str(tmp_path / "save.json")
    Params.save_params_to_json({"max_workers": "3", "vcodec": "libx264"}, filename)

    params = Params()
    params.load_params_from_json(filename)

    assert params.get_max_workers() == 3
    assert params.get_vcodec() == "libx264"


def test_params_is_singleton():
    assert Params() is Params()
