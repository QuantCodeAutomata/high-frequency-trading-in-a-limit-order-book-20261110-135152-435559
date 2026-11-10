# High-frequency trading in a limit order book

Reproduction of selected experiments from Marco Avellaneda and Sasha Stoikov,
"High-frequency trading in a limit order book", Quantitative Finance,
Volume 8, Number 3 (2008), pages 217-224 (working paper version cited by
page numbers throughout this repository).

The paper derives, in Section 3.2, a closed-form approximation to the
optimal quotes of an inventory-averse market maker: an indifference
(reservation) price

```
r(s, q, t) = s - q * gamma * sigma^2 * (T - t)                      (3.17)
```

and a total bid/ask spread

```
delta_a + delta_b = gamma * sigma^2 * (T - t) + (2/gamma) * ln(1 + gamma/k)   (3.18)
```

quoted symmetrically around `r`. Section 3.3 simulates this "inventory"
strategy against a "symmetric" benchmark that quotes the same total spread
but centered on the mid-price `s` instead of `r`, and compares the
distribution of terminal profit and of the final inventory `q_T` over 1000
Monte Carlo paths, for three levels of risk aversion gamma.

## Experiments reproduced

1. **exp1 — single-path simulation** (Figure 1, pages 9-11): one simulated
   mid-price path with the indifference price and the optimal bid/ask quotes
   of the inventory strategy plotted over time, with gamma = 0.1.
2. **exp2 — Monte Carlo comparison, gamma = 0.1** (Table 1, Figure 2,
   pages 10-11): 1000 simulations of the inventory strategy versus the
   symmetric strategy.
3. **exp3 — Monte Carlo comparison, gamma = 0.01** (Table 2, Figure 3,
   page 12): the same comparison for a nearly risk-neutral investor.
4. **exp4 — Monte Carlo comparison, gamma = 0.5** (Table 3, Figure 4,
   page 12): the same comparison for a highly risk-averse investor.

All four experiments are self-contained numerical simulations: the paper
specifies every input parameter (page 10), and no market data is used or
required.

## Repository layout

```
src/            amm_simulator.py (reservation price, spread, single-path and
                Monte Carlo simulators) and reporting.py (shared statistics
                and plotting used by every Monte Carlo experiment);
                config.py holds every parameter as a module-level constant.
exp/            exp1.py, exp2.py, exp3.py, exp4.py — one script per
                experiment, calling only the functions in src/.
tests/          pytest unit and integration tests.
data/           empty package; no market or synthetic data loader is needed
                because every experiment is a self-contained simulation
                whose inputs are the parameters in src/config.py.
results/        tables, figures and RESULTS.md produced by the experiments.
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

No API keys or external data are required.

## Running the tests

```bash
python -m pytest
```

(There are no `market_data`-marked tests in this repository, since no
experiment loads market data.)

## Running the experiments

```bash
python -m exp.exp1
python -m exp.exp2
python -m exp.exp3
python -m exp.exp4
```

Each script writes its tables, figures and a JSON summary directly into
`results/`. `exp2`, `exp3` and `exp4` accept a `--full` flag that selects the
paper's number of Monte Carlo paths (`MC_N_SIMULATIONS_PAPER` in
`src/config.py`, 1000 paths); since this is already the number used by
default, `--full` reproduces exactly the executed configuration.

## Reproduction script

```bash
./reproduce.sh
```

runs the test suite and all four experiments in sequence, overwriting the
contents of `results/`.

## Results

See `results/RESULTS.md` for the numbers produced by the latest run, compared
against the values reported in the paper's Tables 1-3, with verdicts and a
record of every deviation and unresolved detail.
