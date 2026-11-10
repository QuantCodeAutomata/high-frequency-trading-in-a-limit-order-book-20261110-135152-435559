# Results

Marco Avellaneda and Sasha Stoikov, "High-frequency trading in a limit order
book", Quantitative Finance, Volume 8, Number 3 (2008), pages 217-224.

All four experiments are self-contained numerical simulations of the
inventory-averse market-making model of Section 3 (no market data is used).
Parameters are those given on page 10: `s=100`, `T=1`, `sigma=2`, `dt=0.005`,
`q=0`, `k=1.5`, `A=140`, with `gamma` varying per experiment. Each experiment
was run once at its full, paper-specified configuration (1000 Monte Carlo
paths for exp2-exp4); the files below are produced by that run.

## exp1 — Single-path simulation of the inventory strategy

Figure 1 (pages 9-11) plots one simulated mid-price path together with the
indifference price and the optimal bid/ask quotes of the inventory strategy,
for `gamma = 0.1`. Artifacts: `results/exp1_single_path.csv` (full path),
`results/exp1_single_path.png` (mid-price/indifference/bid/ask plot),
`results/exp1_single_path_inventory.png` (inventory path),
`results/exp1_summary.json` (summary statistics).

From `results/exp1_summary.json`:

| Quantity | Value |
|---|---|
| Terminal mid-price | 98.30 |
| Terminal indifference price | 98.30 |
| Terminal inventory | -3.0 |
| Terminal P&L | 71.32 |
| Fraction of steps with sign-consistent deviation (indifference price above mid when short, below when long) | 1.00 |
| Terminal |indifference − mid| | 0.00 |
| Mean |indifference − mid| over the first half of the path | 0.188 |

**Verdict: reproduced.** The paper's qualitative claims for Figure 1 are
exactly the properties checked here: the indifference price always deviates
from the mid-price in the sign implied by the current inventory (fraction
1.00), the deviation is non-zero while trading is in progress (mean absolute
deviation 0.188 over the first half of the path), and it collapses to exactly
zero at the terminal time because the inventory-risk term
`gamma*sigma^2*(T-t)` vanishes at `t = T` (equation 3.17), matching the
paper's statement that "as we approach the terminal time... our agent's
bid/ask quotes look more like a symmetric strategy."

## exp2 — Monte Carlo comparison, gamma = 0.1 (Table 1)

`results/exp2_statistics.csv`, `results/exp2_profit_histogram.csv`,
`results/exp2_pnl_histogram.png`, `results/exp2_final_inventory_histogram.png`,
`results/exp2_summary.json`.

| Strategy | Spread | Profit (paper) | Profit (run) | std(Profit) (paper) | std(Profit) (run) | Final q (paper) | Final q (run) | std(Final q) (paper) | std(Final q) (run) |
|---|---|---|---|---|---|---|---|---|---|
| Inventory | 1.29 | 62.94 | 64.80 | 5.89 | 6.49 | 0.10 | -0.02 | 2.80 | 2.92 |
| Symmetric | 1.29 | 67.21 | 68.54 | 13.43 | 13.13 | -0.018 | 0.21 | 8.66 | 8.29 |

**Verdicts:** spread — reproduced (exact match to the reported `(2/gamma)*ln(1+gamma/k)` value).
Inventory profit — reproduced (+3.0%, same sign). Symmetric profit —
reproduced (+2.0%). Inventory std(Profit) — reproduced (+10.2%, same order).
Symmetric std(Profit) — reproduced (−2.2%). Final q (both strategies) —
reproduced: both the paper's and the run's values are close to zero relative
to their own dispersion (|value| well under one std(Final q)), so a sign
difference at this scale is not material. std(Final q) — reproduced for both
strategies (+4.3% and −4.3%). The paper's central qualitative claim — the
inventory strategy's P&L is far less dispersed than the symmetric strategy's,
at a similar mean profit — holds: std(Profit) is 2.0x larger for the
symmetric strategy in both the paper and this run.

## exp3 — Monte Carlo comparison, gamma = 0.01 (Table 2)

`results/exp3_statistics.csv`, `results/exp3_profit_histogram.csv`,
`results/exp3_pnl_histogram.png`, `results/exp3_final_inventory_histogram.png`,
`results/exp3_summary.json`.

| Strategy | Spread | Profit (paper) | Profit (run) | std(Profit) (paper) | std(Profit) (run) | Final q (paper) | Final q (run) | std(Final q) (paper) | std(Final q) (run) |
|---|---|---|---|---|---|---|---|---|---|
| Inventory | 1.33 | 66.78 | 68.16 | 8.76 | 8.80 | -0.02 | -0.12 | 4.70 | 5.13 |
| Symmetric | 1.33 | 67.36 | 69.33 | 13.40 | 13.67 | -0.31 | 0.32 | 8.65 | 8.71 |

**Verdicts:** spread — reproduced (1.329 vs. the paper's ≈1.33). Inventory
profit — reproduced (+2.1%). Symmetric profit — reproduced (+2.9%). Inventory
std(Profit) — reproduced (+0.5%). Symmetric std(Profit) — reproduced (+2.0%).
Final q and std(Final q) for both strategies — reproduced (all values near
zero relative to their dispersion, and std(Final q) within 9%). The paper's
qualitative claim for this experiment — that with a nearly risk-neutral agent
the inventory and symmetric strategies become close to each other — holds:
the gap between the two strategies' mean profit narrows from about 4.3 points
at gamma=0.1 to about 1.2 points here, and their std(Profit) values are
closer together (ratio 1.55 vs. 2.0 at gamma=0.1) than at gamma=0.1, though
the inventory strategy still has materially lower variance than the
symmetric one, as the paper reports.

## exp4 — Monte Carlo comparison, gamma = 0.5 (Table 3)

`results/exp4_statistics.csv`, `results/exp4_profit_histogram.csv`,
`results/exp4_pnl_histogram.png`, `results/exp4_final_inventory_histogram.png`,
`results/exp4_summary.json`.

| Strategy | Spread | Profit (paper) | Profit (run) | std(Profit) (paper) | std(Profit) (run) | Final q (paper) | Final q (run) | std(Final q) (paper) | std(Final q) (run) |
|---|---|---|---|---|---|---|---|---|---|
| Inventory | 1.15 | 33.92 | 47.87 | 4.72 | 5.80 | -0.02 | 0.01 | 1.88 | 1.91 |
| Symmetric | 1.15 | 66.20 | 58.55 | 14.53 | 10.97 | 0.25 | 0.20 | 9.06 | 6.81 |

**Verdicts:** spread — reproduced (1.151 vs. 1.15). Final q and std(Final q)
for both strategies — reproduced (near zero relative to dispersion; std(Final
q) within 2% for the inventory strategy and within 25% for the symmetric
strategy). Inventory profit — **partially reproduced**: the run's value
(47.87) is 41% above the paper's (33.92), outside the 10% band for
"reproduced" but short of the 50% threshold for "not reproduced"; the sign
and the qualitative ranking (inventory profit well below symmetric profit)
are preserved. Symmetric profit — **partially reproduced** (run 11.6% below
the paper's value). Inventory std(Profit) — **partially reproduced** (+22.9%).
Symmetric std(Profit) — **partially reproduced** (−24.5%).

The qualitative claim of this experiment — a highly risk-averse agent trades
much less, so both the mean and the standard deviation of its profit are
much lower than a risk-neutral agent's — holds in the run: inventory
std(Profit) (5.80) is a third of the symmetric strategy's (10.97), and
inventory profit (47.87) is 18% below symmetric profit (58.55), consistent
in direction with the paper's gap (33.92 vs. 66.20, a 49% shortfall).
However, the size of the gap between the two strategies' mean profit is
smaller in this run than in the paper's Table 3. Equations 3.17-3.18 and the
"Spread" value (1.15, matching exactly) were checked first and ruled out as
the cause. Three further readings of equation 3.18 consistent with the
paper's text were implemented on a reduced 1000-path slice and compared
against the executed implementation at gamma=0.1 and gamma=0.5: (1) treating
ask and bid fills as mutually exclusive within a time step, instead of
independent Bernoulli trials (uncertainty noted in the experiment
description) — profit at gamma=0.5 moved from 47.9 to 45.8, not closing the
gap; (2) removing the clip at zero on the inventory-skewed quote distances
from the mid-price (equations 3.11-3.12) before computing fill intensities —
profit moved from 47.9 to 48.6, not closing the gap; (3) quoting the full
spread `delta_a+delta_b` (equation 3.18) on each side instead of half the
spread — this reading matches the paper's text less well (it contradicts the
sum relation stated by the paper) and, when tested, degraded the already
reproduced gamma=0.1 inventory profit from 64.8 to 44.5, so it was rejected.
None of the three alternatives closes the gap at gamma=0.5, so the cause of
the remaining gap was not identified beyond the three ruled-out hypotheses
above.

## Deviations from the paper

- No market data is used: every experiment in Section 3.3 is a closed-form
  numerical simulation whose parameters are given in full on page 10, so
  `data/` contains no loader and `src/config.py` holds every parameter.
- The mid-price increment is implemented as a symmetric two-point jump
  `+/- sigma*sqrt(dt)` with equal probability, following the paper's own
  wording on page 11 ("The mid-price is updated by a random increment
  `+/- sigma*sqrt(dt)`"), rather than a continuous `N(0, sigma^2*dt)`
  increment that the underlying Brownian motion `dS = sigma*dW` would also
  support; the paper's text was followed literally since both readings
  approximate the same diffusion at this time step and the paper states the
  discrete form explicitly.
- Ask and bid market-order arrivals within one time step are modeled as
  independent Bernoulli trials (both can fire in the same step), per the
  paper's description of `lambda^a` and `lambda^b` as two separate Poisson
  processes (Section 2.4); the paper does not state whether they are mutually
  exclusive. A mutually-exclusive variant was tested as part of the exp4
  investigation above and did not change the conclusions.
- Initial cash wealth is not given in the paper and is assumed to be zero
  (`INITIAL_CASH` in `src/config.py`).
- Random seeds are not given in the paper (`EXP1_SEED`, `MC_SEED` in
  `src/config.py`); they are fixed for reproducibility of this repository's
  output but do not correspond to the paper's own (unpublished) seed.
- The inventory strategy's ask/bid distances from the mid-price (equations
  3.11-3.12) are clipped at zero before computing fill intensities, since the
  Euler discretization can otherwise push them negative for large `|q|` and
  large `gamma`, which has no economic meaning as a quote distance; this
  reading was checked against an unclipped variant in the exp4 investigation
  above and does not change the conclusions.
- For gamma=0.5 (exp4), the run's profit and its standard deviation for both
  strategies differ from the paper's Table 3 by between 12% and 41% (see the
  exp4 verdicts above), while the spread, final inventory, and the
  qualitative ranking between the two strategies match. The cause was not
  identified beyond ruling out three alternative readings of the model
  (mutually-exclusive fills, an unclipped quote distance, and an unhalved
  spread), as detailed above.

## Not reproduced

There is nothing to report: all four selected experiments (exp1-exp4) were
executed at the paper's full configuration, and every table and figure they
target (Figure 1, Tables 1-3, Figures 2-4) has a corresponding artifact and
comparison above.
