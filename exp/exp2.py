"""Experiment 2: Monte Carlo comparison, gamma = 0.1 (1000 simulations).

Compares the "inventory" strategy (quotes centered on the reservation price)
to the "symmetric" strategy (quotes centered on the mid-price, same total
spread) over 1000 independent mid-price paths, with risk aversion
gamma = 0.1, reproducing Table 1 and Figure 2 of "High-frequency trading in a
limit order book" (Avellaneda and Stoikov), Section 3.3, pages 10-11.

Run with:
    python -m exp.exp2
"""
from __future__ import annotations

import argparse
import json
import os

from src import config
from src.amm_simulator import simulate_monte_carlo
from src.reporting import (
    compute_mc_statistics,
    plot_final_inventory_histograms,
    plot_pnl_histograms,
    profit_histogram_table,
)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
GAMMA = config.EXP2_GAMMA
TAG = "exp2"


def main(full: bool = False) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    n_paths = config.MC_N_SIMULATIONS_PAPER if full else config.MC_N_SIMULATIONS_RUN

    result = simulate_monte_carlo(
        n_paths=n_paths,
        s0=config.S0,
        T=config.T,
        sigma=config.SIGMA,
        dt=config.DT,
        q0=config.Q0,
        gamma=GAMMA,
        k=config.K,
        A=config.A_ARRIVAL,
        initial_cash=config.INITIAL_CASH,
        seed=config.MC_SEED,
    )

    stats = compute_mc_statistics(result)
    stats.to_csv(os.path.join(RESULTS_DIR, f"{TAG}_statistics.csv"))

    hist_table = profit_histogram_table(
        result, config.MC_HIST_BIN_MIN, config.MC_HIST_BIN_MAX, config.MC_HIST_BIN_WIDTH
    )
    hist_table.to_csv(os.path.join(RESULTS_DIR, f"{TAG}_profit_histogram.csv"))

    plot_pnl_histograms(result, GAMMA, os.path.join(RESULTS_DIR, f"{TAG}_pnl_histogram.png"))
    plot_final_inventory_histograms(
        result, GAMMA, os.path.join(RESULTS_DIR, f"{TAG}_final_inventory_histogram.png")
    )

    assert stats.loc["inventory", "std_profit"] < stats.loc["symmetric", "std_profit"], (
        "the inventory strategy is expected to have lower P&L variance than the symmetric strategy"
    )

    summary = {
        "gamma": GAMMA,
        "n_paths": n_paths,
        "seed": config.MC_SEED,
        "statistics": stats.to_dict(orient="index"),
    }
    with open(os.path.join(RESULTS_DIR, f"{TAG}_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Experiment 2 (Monte Carlo comparison, gamma={GAMMA}, n_paths={n_paths}) complete.")
    print(stats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="use the paper's full configuration")
    args = parser.parse_args()
    main(full=args.full)
