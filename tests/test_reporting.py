"""Unit tests for the shared Monte Carlo evaluation and plotting components."""
import os
import tempfile

import numpy as np
import pytest

from src.amm_simulator import simulate_monte_carlo, simulate_single_path
from src.reporting import (
    compute_mc_statistics,
    plot_final_inventory_histograms,
    plot_pnl_histograms,
    plot_single_path,
    profit_histogram_table,
)


@pytest.fixture(scope="module")
def small_mc_result():
    return simulate_monte_carlo(
        n_paths=200, s0=100.0, T=1.0, sigma=2.0, dt=0.005, q0=0,
        gamma=0.1, k=1.5, A=140.0, seed=99,
    )


def test_compute_mc_statistics_layout(small_mc_result):
    stats = compute_mc_statistics(small_mc_result)
    assert list(stats.index) == ["inventory", "symmetric"]
    assert set(stats.columns) == {"spread", "profit", "std_profit", "final_q", "std_final_q"}
    assert (stats["std_profit"] >= 0).all()
    assert (stats["std_final_q"] >= 0).all()
    # Both strategies share the same (arrival-component) spread value.
    assert stats.loc["inventory", "spread"] == pytest.approx(stats.loc["symmetric", "spread"])


def test_profit_histogram_table_counts_sum_to_n_paths(small_mc_result):
    table = profit_histogram_table(small_mc_result, bin_min=-200.0, bin_max=300.0, bin_width=10.0)
    assert table["inventory"].sum() <= 200
    assert table["symmetric"].sum() <= 200
    assert (table >= 0).values.all()


def test_plot_pnl_histograms_writes_file(small_mc_result):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "pnl.png")
        plot_pnl_histograms(small_mc_result, gamma=0.1, path=path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0


def test_plot_final_inventory_histograms_writes_file(small_mc_result):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "q.png")
        plot_final_inventory_histograms(small_mc_result, gamma=0.1, path=path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0


def test_plot_single_path_writes_two_files():
    df = simulate_single_path(100.0, 1.0, 2.0, 0.005, 0, 0.1, 1.5, 140.0, seed=5)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "path.png")
        plot_single_path(df, gamma=0.1, path=path)
        assert os.path.exists(path)
        assert os.path.exists(os.path.join(tmp, "path_inventory.png"))
