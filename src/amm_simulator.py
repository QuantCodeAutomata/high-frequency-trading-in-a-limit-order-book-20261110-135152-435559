"""Avellaneda-Stoikov inventory market-making simulator.

Custom implementation of the reservation price and bid/ask spread derived in
"High-frequency trading in a limit order book" (Avellaneda and Stoikov),
Section 3.2-3.3 (equations 3.17 and 3.18, pages 9-10). No open-source
quantitative library (checked: mlfinlab) implements this exact closed-form
approximation, so the model is implemented directly from the paper's
equations rather than reused from a library.

The module provides:
  - reservation_price / optimal_spread: the closed-form quote formulas.
  - simulate_single_path: one simulated mid-price path with the quotes of the
    inventory strategy, used by exp_1.
  - simulate_monte_carlo: a vectorized Monte Carlo comparison of the
    inventory strategy against the mid-price-centered "symmetric" strategy
    that shares the same spread, used by exp_2/exp_3/exp_4.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _validate_params(T: float, sigma: float, dt: float, gamma: float, k: float, A: float) -> None:
    """Basic parameter validation shared by both simulation entry points."""
    if T <= 0:
        raise ValueError(f"T must be positive, got {T}")
    if sigma < 0:
        raise ValueError(f"sigma must be non-negative, got {sigma}")
    if dt <= 0 or dt > T:
        raise ValueError(f"dt must be in (0, T], got dt={dt}, T={T}")
    if gamma <= 0:
        raise ValueError(f"gamma must be strictly positive, got {gamma}")
    if k <= 0:
        raise ValueError(f"k must be strictly positive, got {k}")
    if A <= 0:
        raise ValueError(f"A must be strictly positive, got {A}")


def reservation_price(s: np.ndarray | float, q: np.ndarray | float, tau: np.ndarray | float,
                       gamma: float, sigma: float) -> np.ndarray | float:
    """Indifference (reservation) price r(s, q, t) = s - q*gamma*sigma^2*(T - t).

    Equation (3.17) of the paper. ``tau`` is the remaining time T - t.
    """
    return s - q * gamma * sigma ** 2 * tau


def optimal_spread(tau: np.ndarray | float, gamma: float, sigma: float, k: float) -> np.ndarray | float:
    """Total optimal bid/ask spread delta_a + delta_b.

    Equation (3.18): gamma*sigma^2*(T - t) + (2/gamma)*ln(1 + gamma/k).
    The second term alone, ``arrival_spread_component``, is the value the
    paper's result tables (Tables 1-3) label "Spread" (see Eq. 3.13 and the
    verification in ``arrival_spread_component``).
    """
    return gamma * sigma ** 2 * tau + arrival_spread_component(gamma, k)


def arrival_spread_component(gamma: float, k: float) -> float:
    """Order-arrival component of the spread, (2/gamma)*ln(1 + gamma/k).

    This is the inventory-independent, time-independent part of equation
    (3.13)/(3.18). It reproduces the "Spread" values printed in the paper's
    Tables 1-3 (1.29 for gamma=0.1, 1.15 for gamma=0.5, ~1.33 for gamma=0.01),
    which do not include the time-varying inventory-risk term
    gamma*sigma^2*(T-t); that term is zero only in the limit t -> T.
    """
    return (2.0 / gamma) * np.log(1.0 + gamma / k)


def inventory_side_deltas(delta_half: np.ndarray | float, q: np.ndarray | float, tau: np.ndarray | float,
                           gamma: float, sigma: float) -> tuple:
    """Distances of the inventory strategy's ask/bid quotes from the mid-price s.

    Section 2.4 defines the Poisson fill intensities lambda^a(delta^a) and
    lambda^b(delta^b) as functions of delta^a = p^a - s and delta^b = s - p^b,
    i.e. the distance from the TRUE mid-price, not from the reservation
    price r. Although the inventory strategy quotes delta_half = spread/2 on
    each side of r (equations 3.11-3.13), since r = s - q*gamma*sigma^2*tau
    this implies, by substitution:

        delta^a = delta_half - q*gamma*sigma^2*tau
        delta^b = delta_half + q*gamma*sigma^2*tau

    so the ask/bid distances from the mid-price are skewed by the inventory
    even though the total quoted spread (2*delta_half) is not (eq. 3.13:
    "The bid-ask spread ... is independent of the inventory"). This skew is
    exactly the mechanism through which the inventory strategy pulls the
    position back toward zero. Distances are clipped at zero: the Euler time
    discretization can otherwise push the effective distance negative for
    large gamma and large |q|, which has no economic meaning for a quote
    distance and would make the discretized fill probability exceed one.
    """
    skew = q * gamma * sigma ** 2 * tau
    delta_a = np.clip(delta_half - skew, 0.0, None)
    delta_b = np.clip(delta_half + skew, 0.0, None)
    return delta_a, delta_b


def simulate_single_path(
    s0: float, T: float, sigma: float, dt: float, q0: float,
    gamma: float, k: float, A: float, initial_cash: float = 0.0,
    seed: int | None = None,
) -> pd.DataFrame:
    """Simulate one mid-price path and the inventory strategy's quotes.

    Implements the procedure on page 9-10: at each step the agent's quotes
    are computed from the current state, then market orders arrive as
    independent Bernoulli trials with probability lambda(delta)*dt
    (Poisson-process approximation for small dt), and the mid-price moves by
    +/- sigma*sqrt(dt) with equal probability, exactly as stated on page 11
    ("The mid-price is updated by a random increment +/- sigma*sqrt(dt)").

    Returns a DataFrame indexed by time with columns: mid_price,
    indifference_price, ask_price, bid_price, inventory, cash, pnl.
    """
    _validate_params(T, sigma, dt, gamma, k, A)
    rng = np.random.default_rng(seed)
    n_steps = int(round(T / dt))
    times = np.linspace(0.0, T, n_steps + 1)

    s = s0
    q = float(q0)
    cash = float(initial_cash)

    mid = np.empty(n_steps + 1)
    indiff = np.empty(n_steps + 1)
    ask = np.empty(n_steps + 1)
    bid = np.empty(n_steps + 1)
    inventory = np.empty(n_steps + 1)
    cash_path = np.empty(n_steps + 1)

    for i in range(n_steps + 1):
        tau = T - times[i]
        r = reservation_price(s, q, tau, gamma, sigma)
        spread = optimal_spread(tau, gamma, sigma, k)
        delta = spread / 2.0
        p_ask = r + delta
        p_bid = r - delta

        mid[i] = s
        indiff[i] = r
        ask[i] = p_ask
        bid[i] = p_bid
        inventory[i] = q
        cash_path[i] = cash

        if i == n_steps:
            break

        # Fill intensities use the distance from the mid-price (Section 2.4),
        # which is skewed by the inventory even though the quoted spread
        # around r is not (see inventory_side_deltas).
        delta_a, delta_b = inventory_side_deltas(delta, q, tau, gamma, sigma)
        p_fill_ask = np.clip(A * np.exp(-k * delta_a) * dt, 0.0, 1.0)
        p_fill_bid = np.clip(A * np.exp(-k * delta_b) * dt, 0.0, 1.0)
        if rng.random() < p_fill_ask:  # a market buy order lifts our ask
            q -= 1.0
            cash += p_ask
        if rng.random() < p_fill_bid:  # a market sell order hits our bid
            q += 1.0
            cash -= p_bid

        # Mid-price increment: +/- sigma*sqrt(dt) with equal probability (page 11).
        step = sigma * np.sqrt(dt)
        s = s + (step if rng.random() < 0.5 else -step)

    pnl = cash_path + inventory * mid
    return pd.DataFrame(
        {
            "time": times,
            "mid_price": mid,
            "indifference_price": indiff,
            "ask_price": ask,
            "bid_price": bid,
            "inventory": inventory,
            "cash": cash_path,
            "pnl": pnl,
        }
    ).set_index("time")


def simulate_monte_carlo(
    n_paths: int, s0: float, T: float, sigma: float, dt: float, q0: float,
    gamma: float, k: float, A: float, initial_cash: float = 0.0,
    seed: int | None = None,
) -> dict:
    """Vectorized Monte Carlo comparison of the inventory and symmetric strategies.

    Both strategies run on the same simulated mid-price paths (one random
    walk per Monte Carlo draw, shared between the two strategies), but each
    strategy's own quotes generate independent order-arrival Bernoulli
    trials, since each strategy represents a separate hypothetical quoting
    book with its own (possibly different) quoted prices.

    Returns a dict with keys ``"inventory"`` and ``"symmetric"``, each
    mapping to a dict with 1-D numpy arrays ``"profit"`` (terminal P&L,
    cash + q_T * S_T) and ``"final_q"`` (terminal inventory) of length
    ``n_paths``, plus ``"spread_t0"`` (the full spread at t=0) and
    ``"arrival_spread_component"`` (the (2/gamma)*ln(1+gamma/k) term, which
    is the "Spread" value reported in the paper's Tables 1-3).
    """
    _validate_params(T, sigma, dt, gamma, k, A)
    if n_paths <= 0:
        raise ValueError(f"n_paths must be strictly positive, got {n_paths}")
    rng = np.random.default_rng(seed)
    n_steps = int(round(T / dt))

    s = np.full(n_paths, s0, dtype=float)
    q_inv = np.full(n_paths, float(q0))
    q_sym = np.full(n_paths, float(q0))
    cash_inv = np.full(n_paths, float(initial_cash))
    cash_sym = np.full(n_paths, float(initial_cash))

    for i in range(n_steps):
        t = i * dt
        tau = T - t
        spread = optimal_spread(tau, gamma, sigma, k)
        delta = spread / 2.0
        p_fill = A * np.exp(-k * delta) * dt

        r = reservation_price(s, q_inv, tau, gamma, sigma)
        ask_inv = r + delta
        bid_inv = r - delta
        ask_sym = s + delta
        bid_sym = s - delta

        # Inventory strategy: fill intensities use the (inventory-skewed)
        # distance from the mid-price, not the symmetric distance from r
        # (see inventory_side_deltas). Symmetric strategy: no skew, delta
        # from the mid-price equals delta on both sides, so p_fill applies
        # unchanged to both sides.
        delta_a_inv, delta_b_inv = inventory_side_deltas(delta, q_inv, tau, gamma, sigma)
        p_fill_ask_inv = np.clip(A * np.exp(-k * delta_a_inv) * dt, 0.0, 1.0)
        p_fill_bid_inv = np.clip(A * np.exp(-k * delta_b_inv) * dt, 0.0, 1.0)

        fill_ask_inv = rng.random(n_paths) < p_fill_ask_inv
        fill_bid_inv = rng.random(n_paths) < p_fill_bid_inv
        fill_ask_sym = rng.random(n_paths) < p_fill
        fill_bid_sym = rng.random(n_paths) < p_fill

        q_inv -= fill_ask_inv
        cash_inv += fill_ask_inv * ask_inv
        q_inv += fill_bid_inv
        cash_inv -= fill_bid_inv * bid_inv

        q_sym -= fill_ask_sym
        cash_sym += fill_ask_sym * ask_sym
        q_sym += fill_bid_sym
        cash_sym -= fill_bid_sym * bid_sym

        step = sigma * np.sqrt(dt)
        jump = np.where(rng.random(n_paths) < 0.5, step, -step)
        s = s + jump

    pnl_inv = cash_inv + q_inv * s
    pnl_sym = cash_sym + q_sym * s

    return {
        "inventory": {"profit": pnl_inv, "final_q": q_inv.copy()},
        "symmetric": {"profit": pnl_sym, "final_q": q_sym.copy()},
        "spread_t0": optimal_spread(T, gamma, sigma, k),
        "arrival_spread_component": arrival_spread_component(gamma, k),
    }
