"""Unit tests for the Avellaneda-Stoikov inventory market-making simulator.

These tests check the paper's properties (signs, formulas, absence of
look-ahead, window lengths) on small synthetic inputs, not the paper's
reported numbers, which are checked in exp/ integration runs.
"""
import numpy as np
import pandas as pd
import pytest

from src.amm_simulator import (
    arrival_spread_component,
    optimal_spread,
    reservation_price,
    simulate_monte_carlo,
    simulate_single_path,
)


def test_reservation_price_equals_mid_when_inventory_zero():
    # Equation (3.17): r = s - q*gamma*sigma^2*(T-t); with q=0, r=s exactly.
    s = 100.0
    assert reservation_price(s, 0.0, tau=0.5, gamma=0.1, sigma=2.0) == pytest.approx(s)


def test_reservation_price_sign_with_inventory():
    # Long inventory (q>0) must lower the reservation price below the mid-price,
    # since the agent quotes more aggressively to sell; short inventory (q<0)
    # must raise it above the mid-price (page 9-10).
    s, tau, gamma, sigma = 100.0, 0.5, 0.1, 2.0
    r_long = reservation_price(s, 1.0, tau, gamma, sigma)
    r_short = reservation_price(s, -1.0, tau, gamma, sigma)
    assert r_long < s < r_short


def test_reservation_price_converges_to_mid_as_t_to_T():
    # As t -> T (tau -> 0), the reservation price converges to the mid-price
    # regardless of inventory (paper, page 11: "As we approach the terminal
    # time... our agent's bid/ask quotes look more like a symmetric strategy").
    s = 100.0
    r = reservation_price(s, q=5.0, tau=0.0, gamma=0.1, sigma=2.0)
    assert r == pytest.approx(s)


def test_arrival_spread_component_matches_paper_tables():
    # Table 1 (gamma=0.1): Spread = 1.29; Table 3 (gamma=0.5): Spread = 1.15;
    # Table 2 (gamma=0.01): Spread ~ 1.33. These paper values correspond to
    # the (2/gamma)*ln(1+gamma/k) term of equation (3.13)/(3.18), not the full
    # time-varying spread.
    k = 1.5
    assert arrival_spread_component(0.1, k) == pytest.approx(1.29, abs=0.01)
    assert arrival_spread_component(0.5, k) == pytest.approx(1.15, abs=0.01)
    assert arrival_spread_component(0.01, k) == pytest.approx(1.33, abs=0.01)


def test_optimal_spread_decreases_as_t_to_T():
    # The inventory-risk term gamma*sigma^2*(T-t) vanishes at t=T, so the full
    # spread at t=T must equal exactly the arrival component.
    gamma, sigma, k = 0.1, 2.0, 1.5
    spread_t0 = optimal_spread(tau=1.0, gamma=gamma, sigma=sigma, k=k)
    spread_tT = optimal_spread(tau=0.0, gamma=gamma, sigma=sigma, k=k)
    assert spread_t0 > spread_tT
    assert spread_tT == pytest.approx(arrival_spread_component(gamma, k))


def test_simulate_single_path_output_shape_and_no_lookahead():
    df = simulate_single_path(
        s0=100.0, T=1.0, sigma=2.0, dt=0.005, q0=0, gamma=0.1, k=1.5, A=140.0, seed=1,
    )
    n_steps = int(round(1.0 / 0.005))
    assert len(df) == n_steps + 1
    assert list(df.index)[0] == 0.0
    assert list(df.index)[-1] == pytest.approx(1.0)
    # The quotes at time t must be computable from state known at t (no
    # look-ahead): ask/bid must bracket the indifference price at every step.
    assert (df["ask_price"] >= df["indifference_price"]).all()
    assert (df["bid_price"] <= df["indifference_price"]).all()
    # Inventory changes by at most +/-1 per step (single order arrivals).
    assert (df["inventory"].diff().abs().dropna() <= 1.0 + 1e-9).all()


def test_simulate_single_path_deterministic_with_seed():
    df1 = simulate_single_path(100.0, 1.0, 2.0, 0.005, 0, 0.1, 1.5, 140.0, seed=7)
    df2 = simulate_single_path(100.0, 1.0, 2.0, 0.005, 0, 0.1, 1.5, 140.0, seed=7)
    pd.testing.assert_frame_equal(df1, df2)


def test_simulate_single_path_zero_volatility_quotes_symmetric_at_zero_inventory():
    # With sigma=0 and q0=0 the mid-price never moves and inventory stays at
    # zero (fills are symmetric in expectation but any single fill breaks the
    # zero mid-price motion only through inventory, not price), so the
    # indifference price must equal the mid-price throughout.
    df = simulate_single_path(100.0, 1.0, 0.0, 0.01, 0, 0.1, 1.5, 140.0, seed=3)
    assert np.allclose(df["mid_price"].values, 100.0)


def test_simulate_monte_carlo_shapes_and_bounds():
    n_paths = 50
    result = simulate_monte_carlo(
        n_paths=n_paths, s0=100.0, T=1.0, sigma=2.0, dt=0.005, q0=0,
        gamma=0.1, k=1.5, A=140.0, seed=11,
    )
    for strategy in ("inventory", "symmetric"):
        assert result[strategy]["profit"].shape == (n_paths,)
        assert result[strategy]["final_q"].shape == (n_paths,)
        assert np.isfinite(result[strategy]["profit"]).all()
    assert result["spread_t0"] > result["arrival_spread_component"] > 0.0


def test_inventory_strategy_has_lower_pnl_variance_than_symmetric_gamma_0_1():
    # Core qualitative claim of the paper (page 11-12): with gamma=0.1 the
    # inventory strategy produces a markedly narrower P&L distribution than
    # the symmetric strategy.
    result = simulate_monte_carlo(
        n_paths=600, s0=100.0, T=1.0, sigma=2.0, dt=0.005, q0=0,
        gamma=0.1, k=1.5, A=140.0, seed=123,
    )
    std_inv = result["inventory"]["profit"].std()
    std_sym = result["symmetric"]["profit"].std()
    assert std_inv < std_sym


def test_inventory_effect_shrinks_as_gamma_to_zero():
    # Page 12: with a small gamma (nearly risk-neutral investor), the
    # inventory effect is much smaller and the two strategies become similar.
    # The spread between mean |final_q| of the two strategies should shrink
    # relative to the gamma=0.1 case.
    result_small_gamma = simulate_monte_carlo(
        n_paths=600, s0=100.0, T=1.0, sigma=2.0, dt=0.005, q0=0,
        gamma=0.01, k=1.5, A=140.0, seed=321,
    )
    result_base_gamma = simulate_monte_carlo(
        n_paths=600, s0=100.0, T=1.0, sigma=2.0, dt=0.005, q0=0,
        gamma=0.1, k=1.5, A=140.0, seed=321,
    )
    gap_small = abs(
        result_small_gamma["inventory"]["profit"].std()
        - result_small_gamma["symmetric"]["profit"].std()
    )
    gap_base = abs(
        result_base_gamma["inventory"]["profit"].std()
        - result_base_gamma["symmetric"]["profit"].std()
    )
    assert gap_small < gap_base


def test_higher_risk_aversion_reduces_final_inventory_dispersion():
    # Page 12: a highly risk-averse investor (gamma=0.5) aggressively avoids
    # accumulating inventory, producing a lower std of final inventory than a
    # less risk-averse investor (gamma=0.1) under the inventory strategy.
    result_high_gamma = simulate_monte_carlo(
        n_paths=600, s0=100.0, T=1.0, sigma=2.0, dt=0.005, q0=0,
        gamma=0.5, k=1.5, A=140.0, seed=55,
    )
    result_base_gamma = simulate_monte_carlo(
        n_paths=600, s0=100.0, T=1.0, sigma=2.0, dt=0.005, q0=0,
        gamma=0.1, k=1.5, A=140.0, seed=55,
    )
    assert result_high_gamma["inventory"]["final_q"].std() < result_base_gamma["inventory"]["final_q"].std()


def test_invalid_parameters_raise():
    with pytest.raises(Exception):
        simulate_single_path(100.0, 1.0, 2.0, 0.005, 0, gamma=0.0, k=1.5, A=140.0)


def test_single_path_edge_case_very_short_horizon():
    # A single step (T == dt) must still return a valid two-row path.
    df = simulate_single_path(100.0, 0.005, 2.0, 0.005, 0, 0.1, 1.5, 140.0, seed=9)
    assert len(df) == 2
