"""Integration smoke tests for the experiment entry points in exp/.

These run the full shared pipeline (src.amm_simulator + src.reporting) end to
end on a reduced number of Monte Carlo paths, writing to a temporary results
directory so the real results/ artifacts are never touched by the test suite.
"""
import importlib
import json
import os

import pytest


@pytest.fixture
def isolated_results_dir(tmp_path, monkeypatch):
    for module_name in ("exp.exp1", "exp.exp2", "exp.exp3", "exp.exp4"):
        if module_name in importlib.sys.modules:
            del importlib.sys.modules[module_name]
    monkeypatch.setattr("src.config.MC_N_SIMULATIONS_RUN", 40, raising=True)
    yield tmp_path


def _patch_results_dir(module, tmp_path):
    module.RESULTS_DIR = str(tmp_path)


def test_exp1_runs_end_to_end(isolated_results_dir):
    import exp.exp1 as exp1
    _patch_results_dir(exp1, isolated_results_dir)
    exp1.main()
    assert os.path.exists(os.path.join(isolated_results_dir, "exp1_single_path.csv"))
    assert os.path.exists(os.path.join(isolated_results_dir, "exp1_single_path.png"))
    with open(os.path.join(isolated_results_dir, "exp1_summary.json")) as f:
        summary = json.load(f)
    assert summary["n_steps"] == 200


def test_exp2_runs_end_to_end(isolated_results_dir):
    import exp.exp2 as exp2
    _patch_results_dir(exp2, isolated_results_dir)
    exp2.main(full=False)
    assert os.path.exists(os.path.join(isolated_results_dir, "exp2_statistics.csv"))
    with open(os.path.join(isolated_results_dir, "exp2_summary.json")) as f:
        summary = json.load(f)
    assert summary["n_paths"] == 40
    assert summary["gamma"] == pytest.approx(0.1)


def test_exp3_runs_end_to_end(isolated_results_dir):
    import exp.exp3 as exp3
    _patch_results_dir(exp3, isolated_results_dir)
    exp3.main(full=False)
    with open(os.path.join(isolated_results_dir, "exp3_summary.json")) as f:
        summary = json.load(f)
    assert summary["gamma"] == pytest.approx(0.01)


def test_exp4_runs_end_to_end(isolated_results_dir):
    import exp.exp4 as exp4
    _patch_results_dir(exp4, isolated_results_dir)
    exp4.main(full=False)
    with open(os.path.join(isolated_results_dir, "exp4_summary.json")) as f:
        summary = json.load(f)
    assert summary["gamma"] == pytest.approx(0.5)
