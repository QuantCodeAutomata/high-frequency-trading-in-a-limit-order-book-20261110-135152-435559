"""Parameters for the Avellaneda-Stoikov inventory market-making experiments.

All values are module-level constants (no classes or parameter dicts), each
annotated with its meaning, unit and source. The source is either a page of
"High-frequency trading in a limit order book" (Avellaneda and Stoikov) or
"not specified in the paper" when the paper leaves a detail open.
"""

# --- Shared market and strategy parameters (paper, Section 3.3, page 10) ---
S0 = 100.0          # initial mid-price, currency units, page 10
T = 1.0             # trading horizon (terminal time), in time units, page 10
SIGMA = 2.0         # volatility of the mid-price Brownian motion, page 10
DT = 0.005          # simulation time step, in time units, page 10
Q0 = 0              # initial inventory, in shares, page 10
K = 1.5             # order-arrival decay parameter k in lambda(delta) = A*exp(-k*delta), page 10
A_ARRIVAL = 140.0   # order-arrival intensity scale A, page 10
INITIAL_CASH = 0.0  # initial cash wealth x; not specified in the paper, assumed zero

# --- exp_1: single-path illustration of bid/ask/indifference price dynamics (Figure 1, page 10-11) ---
EXP1_GAMMA = 0.1    # risk-aversion parameter used for the single-path illustration, page 10
EXP1_SEED = 42      # random seed; not specified in the paper, fixed for reproducibility

# --- exp_2/exp_3/exp_4: Monte Carlo comparison of inventory vs symmetric strategy ---
# "We then run 1000 simulations to compare our 'inventory' strategy to the
# 'symmetric' strategy." (page 11)
MC_N_SIMULATIONS_PAPER = 1000  # number of Monte Carlo paths used in the paper, page 11
MC_N_SIMULATIONS_RUN = 1000    # executed configuration; equal to the paper's value (simulation is inexpensive)
MC_SEED = 2024                 # random seed; not specified in the paper, fixed for reproducibility

EXP2_GAMMA = 0.1    # risk-aversion parameter, Table 1, page 11
EXP3_GAMMA = 0.01   # risk-aversion parameter, Table 2 (nearly risk-neutral investor), page 12
EXP4_GAMMA = 0.5    # risk-aversion parameter, Table 3 (highly risk-averse investor), page 12

# Profit-bin histogram edges used for the Monte Carlo P&L histograms (page 12-13)
MC_HIST_BIN_WIDTH = 10.0   # width of one profit bin, currency units; page 12-13 table layout
MC_HIST_BIN_MIN = -50.0    # lower edge of the first profit bin, page 12-13 table layout
MC_HIST_BIN_MAX = 140.0    # upper edge of the last profit bin, page 12-13 table layout

