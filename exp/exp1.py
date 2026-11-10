"""Experiment 1: single-path simulation of the inventory strategy.

Simulates one mid-price path and displays the mid-price, the indifference
(reservation) price, and the optimal bid/ask quotes of the inventory
strategy over time, as in Figure 1 of "High-frequency trading in a limit
order book" (Avellaneda and Stoikov), Section 3.3, pages 9-11.

Run with:
    python -m exp.exp1
"""
from __future__ import annotations

import json
import os

from src import config
from src.amm_simulator import simulate_single_path
from src.reporting import plot_single_path

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")


def main() -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    path_df = simulate_single_path(
        s0=config.S0,
        T=config.T,
        sigma=config.SIGMA,
        dt=config.DT,
        q0=config.Q0,
        gamma=config.EXP1_GAMMA,
        k=config.K,
        A=config.A_ARRIVAL,
        initial_cash=config.INITIAL_CASH,
        seed=config.EXP1_SEED,
    )

    assert len(path_df) == int(round(config.T / config.DT)) + 1, "unexpected number of time steps"
    assert (path_df["ask_price"] >= path_df["bid_price"]).all(), "ask must never be below bid"

    csv_path = os.path.join(RESULTS_DIR, "exp1_single_path.csv")
    path_df.to_csv(csv_path)

    plot_path = os.path.join(RESULTS_DIR, "exp1_single_path.png")
    plot_single_path(path_df, config.EXP1_GAMMA, plot_path)

    # Qualitative checks from the paper's expected outcomes (page 10-11):
    # the indifference price deviates from the mid-price with sign opposite
    # to the inventory sign, and the two converge as t -> T.
    deviation = path_df["indifference_price"] - path_df["mid_price"]
    inventory = path_df["inventory"]
    sign_consistent = float(((deviation * (-inventory)) >= -1e-9).mean())
    terminal_gap = abs(deviation.iloc[-1])
    mean_abs_gap_first_half = deviation.iloc[: len(deviation) // 2].abs().mean()

    summary = {
        "gamma": config.EXP1_GAMMA,
        "seed": config.EXP1_SEED,
        "n_steps": len(path_df) - 1,
        "terminal_mid_price": float(path_df["mid_price"].iloc[-1]),
        "terminal_indifference_price": float(path_df["indifference_price"].iloc[-1]),
        "terminal_inventory": float(path_df["inventory"].iloc[-1]),
        "terminal_pnl": float(path_df["pnl"].iloc[-1]),
        "fraction_of_steps_with_sign_consistent_deviation": sign_consistent,
        "terminal_abs_deviation": float(terminal_gap),
        "mean_abs_deviation_first_half": float(mean_abs_gap_first_half),
    }
    with open(os.path.join(RESULTS_DIR, "exp1_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print("Experiment 1 (single-path simulation) complete.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
