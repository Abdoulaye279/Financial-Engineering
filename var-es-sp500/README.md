# VaR / Expected Shortfall backtest

How often is a 99% one-day VaR actually breached? It should be 1% of days. I tested five models on the S&P 500 from 2004 to 2026 (5,761 days), each one only using the previous 1000 days, and counted.

![cumulative breaches](breaches.png)

| model | breaches | Kupiec | Christoffersen | real loss / ES |
|---|---|---|---|---|
| normal | 2.34% | ✗ | ✗ | 1.39 |
| historical | 1.46% | ✗ | ✗ | 1.07 |
| GARCH, normal errors | 2.24% | ✗ | ✓ | 1.12 |
| GARCH, Student-t errors | 1.53% | ✗ | ✓ | 1.01 |
| GJR-GARCH, Student-t errors | 1.49% | ✗ | ✓ | 1.01 |
| GARCH, skewed t (Hansen) | 1.20% | ✓ | ✓ (p = 0.06) | 1.01 |
| GJR-GARCH, skewed t | 1.06% | ✓ | ✓ | 1.05 |
| FHS (GARCH + empirical residuals) | 1.23% | ✓ | ✓ | 1.03 |
| GARCH-EVT (generalized Pareto tail) | 1.15% | ✓ | ✗ (p = 0.047) | 1.03 |

You need both a volatility that moves (GARCH) and a tail that isn't normal. Fixing only one isn't enough. Student-t errors help but the t is symmetric, and S&P 500 losses are heavier than gains (residual 1% quantile -2.75 against -2.55 for the fitted t). A GJR-GARCH doesn't change that: the fit says only down days raise the volatility (alpha ≈ 0, gamma = 0.21), but the residuals stay just as skewed, so the asymmetry is in the shocks themselves. Hansen's skewed t is what fixes it: it finds the heavier left tail by itself (lambda = -0.13, 1% quantile -2.74 against -2.75 in the data) and passes both tests with the same GARCH as before. And with the skewed t in place, GJR finally helps: the breaches become clearly independent (Christoffersen p from 0.06 to 0.68), only 4 in 2008, for the same average VaR. That's the best model on the S&P 500.

Then I added Apple (data in `data/aapl.csv`) for a 50/50 portfolio. Their correlation swings between 0.2 and 0.9 and jumps in crises, and on the worst 1% of days they fall together 28% of the time, against 20% for a Gaussian dependence. A t copula with ~4.5 degrees of freedom fits better. So diversification only cuts the VaR by 13%, and Apple ends up with 68% of the ES for 50% of the money (36% in Apple would split it equally).

On the portfolio most models get caught in autumn 2008. A few still pass both tests over the full period. The best are the GARCH and GJR with skewed-t errors: 1.02% and 1.04% breaches, ES exact. The plain Student-t versions pass too (1.18%, 1.25% for GJR), and so does a DCC-GARCH version of FHS where the correlation moves every day (1.20%). The fitted t tails get through 2008 with 6 breaches, where the models built on the calm 2004-07 residuals have 14 to 18.

Last thing, the 10-day horizon used by Basel (`06_ten_day_horizon`). Scaling the 1-day VaR by sqrt(10) is the usual shortcut. Simulating 10-day paths of the GJR skewed-t model instead gives a VaR 22% higher on average on the S&P 500, up to 70% higher in calm markets: the vol tends to rise back during the 10 days, and every bad day raises it for the next ones. On 576 non-overlapping 10-day periods the simulated VaR has 6 breaches for 5.8 expected, the sqrt(10) versions 9. With so few breaches the tests can't separate the models much, though.

Then seven assets (`07_seven_assets`): the S&P 500, Apple, Microsoft, JPMorgan, ExxonMobil, gold and long US Treasuries, from 2004 (when the gold ETF starts). The most interesting thing there is the bonds: from 2007 to 2021 they went up when stocks fell (correlation down to -0.7), and since 2022 the correlation is positive, so that hedge is mostly gone. With 1/7 in each asset, JPMorgan alone brings 28% of the ES and the bonds reduce it. Splitting the ES equally needs 44.5% in bonds and 17% in gold, and cuts the ES from 3.9% to 2.1% (5.2% for the S&P 500 alone), with a lower return. On the backtest from late 2008, most models land near 1% but have their breaches bunched in March 2020; only GJR skewed-t, FHS and GARCH-EVT pass both tests.

Notebooks 01-02 are the S&P 500 part, 03-05 the two-asset portfolio, 06 the 10-day horizon, 07 the seven assets, 08 the yearly weights. The GARCH and DCC likelihood fits, the EVT tail, the copula and the tests are written by hand in `risk.py` (tests in `test_risk.py`).

Those equal-risk weights knew the whole period, so in `08_yearly_weights` I recompute them every January from the last 1000 days only. Hindsight turns out to matter little (ES 2.26% out of sample against 2.09%), but 2022 shows the weak spot: the weights set on 2018-2021 still put 47% in bonds, the bonds ended up bringing half of the risk, and the portfolio lost 17% that year, close to the S&P 500 (-19%) and twice the 1/7 portfolio. Its worst drawdown is 2022, where for the S&P 500 and 1/7 it is March 2020.

Things I'd still like to try: a shorter window or DCC-based weights to react faster to a change like 2022, and transaction costs.
