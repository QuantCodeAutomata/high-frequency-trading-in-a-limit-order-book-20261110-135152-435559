"""Shared evaluation and plotting components for the Monte Carlo experiments.

Used identically by exp/exp2.py, exp/exp3.py and exp/exp4.py (one risk
aversion gamma each), so that the statistics definitions, the histogram bin
edges and the figure layout are common across every Monte Carlo experiment, as
described in "High-frequency trading in a limit order book"
(Avellaneda and Stoikov), Section 3.3, pages 11-12.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def compute_mc_statistics(result: dict) -> pd.DataFrame:
    """Summary table matching the layout of the paper's Tables 1-3.

    ``result`` is the dict returned by ``amm_simulator.simulate_monte_carlo``.
    Returns a DataFrame indexed by strategy name ("inventory", "symmetric")
    with columns: spread, profit, std_profit, final_q, std_final_q.
    """
    rows = {}
    for strategy in ("inventory", "symmetric"):
        profit = np.asarray(result[strategy]["profit"])
        final_q = np.asarray(result[strategy]["final_q"])
        rows[strategy] = {
            "spread": result["arrival_spread_component"],
            "profit": profit.mean(),
            "std_profit": profit.std(ddof=0),
            "final_q": final_q.mean(),
            "std_final_q": final_q.std(ddof=0),
        }
    return pd.DataFrame(rows).T


def profit_histogram_table(result: dict, bin_min: float, bin_max: float, bin_width: float) -> pd.DataFrame:
    """Binned profit counts for both strategies, as in the paper's profit-bin tables."""
    edges = np.arange(bin_min, bin_max + bin_width, bin_width)
    table = {}
    for strategy in ("inventory", "symmetric"):
        profit = np.asarray(result[strategy]["profit"])
        counts, _ = np.histogram(profit, bins=edges)
        table[strategy] = counts
    labels = [f"{edges[i]:.0f} to {edges[i + 1]:.0f}" for i in range(len(edges) - 1)]
    return pd.DataFrame(table, index=labels)


def plot_pnl_histograms(result: dict, gamma: float, path: str) -> None:
    """P&L histogram of both strategies on the same plot (Figure 2-4 of the paper)."""
    fig, ax = plt.subplots(figsize=(8, 5))
    profit_inv = np.asarray(result["inventory"]["profit"])
    profit_sym = np.asarray(result["symmetric"]["profit"])
    bins = 30
    ax.hist(profit_sym, bins=bins, alpha=0.55, label="Symmetric strategy", color="tab:orange")
    ax.hist(profit_inv, bins=bins, alpha=0.55, label="Inventory strategy", color="tab:blue")
    ax.set_xlabel("Terminal P&L")
    ax.set_ylabel("Number of simulations")
    ax.set_title(f"P&L distribution, inventory vs symmetric strategy (gamma = {gamma})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_final_inventory_histograms(result: dict, gamma: float, path: str) -> None:
    """Final-inventory histogram of both strategies."""
    fig, ax = plt.subplots(figsize=(8, 5))
    q_inv = np.asarray(result["inventory"]["final_q"])
    q_sym = np.asarray(result["symmetric"]["final_q"])
    bins = np.arange(min(q_inv.min(), q_sym.min()) - 0.5, max(q_inv.max(), q_sym.max()) + 1.5, 1.0)
    ax.hist(q_sym, bins=bins, alpha=0.55, label="Symmetric strategy", color="tab:orange")
    ax.hist(q_inv, bins=bins, alpha=0.55, label="Inventory strategy", color="tab:blue")
    ax.set_xlabel("Final inventory $q_T$")
    ax.set_ylabel("Number of simulations")
    ax.set_title(f"Final inventory distribution, inventory vs symmetric strategy (gamma = {gamma})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_single_path(path_df: pd.DataFrame, gamma: float, path: str) -> None:
    """Mid-price, indifference price and optimal bid/ask quotes over time (Figure 1)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(path_df.index, path_df["mid_price"], label="Mid-price", color="black", linewidth=1.2)
    ax.plot(path_df.index, path_df["indifference_price"], label="Indifference (reservation) price",
            color="tab:purple", linewidth=1.2, linestyle="--")
    ax.plot(path_df.index, path_df["ask_price"], label="Ask quote", color="tab:red", linewidth=1.0)
    ax.plot(path_df.index, path_df["bid_price"], label="Bid quote", color="tab:green", linewidth=1.0)
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.set_title(f"Inventory strategy: mid-price, indifference price and quotes (gamma = {gamma})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(path_df.index, path_df["inventory"], color="tab:blue")
    ax2.axhline(0.0, color="grey", linewidth=0.8, linestyle=":")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Inventory $q_t$")
    ax2.set_title("Inventory position over time")
    fig2.tight_layout()
    inventory_path = path.replace(".png", "_inventory.png")
    fig2.savefig(inventory_path, dpi=150)
    plt.close(fig2)
