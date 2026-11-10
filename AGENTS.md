# AGENTS.md

This repository reproduces four numerical-simulation experiments from Marco
Avellaneda and Sasha Stoikov, "High-frequency trading in a limit order book",
Quantitative Finance, Volume 8, Number 3 (2008), pages 217-224: the
inventory-averse market-making model of Section 3 (reservation price and
optimal spread, equations 3.17-3.18) simulated on a single path (exp1,
Figure 1) and compared against a mid-price-centered "symmetric" benchmark
over 1000 Monte Carlo paths for three levels of risk aversion gamma
(exp2-exp4, Tables 1-3 and Figures 2-4).

## Layout

- `src/amm_simulator.py` — the reservation price, optimal spread, single-path
  simulator (`simulate_single_path`) and vectorized Monte Carlo simulator
  (`simulate_monte_carlo`); the only place the model equations live.
- `src/reporting.py` — statistics and plotting shared by exp2-exp4
  (`compute_mc_statistics`, `profit_histogram_table`, `plot_pnl_histograms`,
  `plot_final_inventory_histograms`).
- `src/config.py` — every experiment parameter as a module-level constant,
  each with a one-line comment giving its meaning, unit and source (a page of
  the paper, or "not specified in the paper").
- `exp/exp1.py`, `exp/exp2.py`, `exp/exp3.py`, `exp/exp4.py` — one script per
  experiment; each calls only the functions in `src/` and writes its tables,
  figures and a JSON summary into `results/`.
- `tests/` — pytest unit tests for `src/amm_simulator.py` and
  `src/reporting.py`, and integration tests that run each `exp/` script
  end-to-end on a reduced configuration.
- `data/` — an empty package. No experiment here loads market or synthetic
  data: every input is one of the closed-form parameters given on page 10 of
  the paper, so there is nothing for a loader or generator to produce.
- `results/` — tables (`*_statistics.csv`, `*_profit_histogram.csv`), figures
  (`*.png`) and JSON summaries written by the experiment scripts, plus
  `results/RESULTS.md` with the paper comparison.

## Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m pytest                       # all tests
python -m pytest -m "not market_data"   # same as above: no test here is marked market_data

python -m exp.exp1
python -m exp.exp2 --full               # --full selects MC_N_SIMULATIONS_PAPER (1000 paths);
python -m exp.exp3 --full               # already the default, since this project's Monte Carlo
python -m exp.exp4 --full               # simulation is inexpensive at the paper's full size

./reproduce.sh                          # runs the tests, then all four experiments
```

## Conventions

- Every experiment parameter lives in `src/config.py` as an upper-case
  module-level constant; no parameter is hardcoded in `exp/` or `src/`.
- No market data is used in this repository. If a future experiment needed
  it, it would be loaded only through `data/data_loader.py` via the QuantX
  Dataloader REST API, with `DATALOADER_API_KEY`/`MASSIVE_API_KEY` read from
  an uncommitted `.env` (see `.env.example` conventions in similar
  repositories); none of that applies to the experiments implemented here.
- Tests use small, fast, deterministic configurations (short horizons, few
  Monte Carlo paths) and check the paper's qualitative properties — signs of
  the indifference-price deviation, convergence to the mid-price at the
  terminal time, the ordering of the two strategies' P&L variance — rather
  than exact reported numbers.
- Running the experiment commands above overwrites every file in `results/`.
  After a rerun, the numbers and verdicts in `results/RESULTS.md` must be
  checked against the newly written files and updated by hand; they are not
  regenerated automatically.
