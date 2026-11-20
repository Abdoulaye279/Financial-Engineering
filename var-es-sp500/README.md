# VaR and Expected Shortfall on the S&P 500

1-day VaR and Expected Shortfall at 99% for a position in the S&P 500, with five models, backtested day by day from 2004 to 2026 (5,761 days).

Files:
- `risk.py`: the five models (normal, historical, GARCH(1,1), filtered historical simulation, GARCH-EVT), the GARCH maximum likelihood fit, the GPD tail fit and the Kupiec and Christoffersen tests
- `sp500_var_es.ipynb`: the analysis with plots
- `test_risk.py`: tests on simulated data
- data: `../black-scholes-sp500/data/sp500.csv`

Results (breach rate, expected 1%):
- Normal: 2.34%, rejected by both tests, losses on breach days 39% above the ES
- Historical: 1.46%, rejected by both tests
- GARCH with normal errors: 2.24%, breaches independent but too many
- FHS: 1.23%, passes both tests, ES almost exact
- GARCH-EVT: 1.15%, best breach rate and ES almost exact, independence test at the limit (p = 0.047)

Both the volatility (GARCH) and the tail (empirical or EVT) have to be modelled to get a correct VaR.

To run:
```
pip install numpy pandas scipy matplotlib jupyter pytest
jupyter notebook sp500_var_es.ipynb
pytest
```
