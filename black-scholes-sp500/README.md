# Black-Scholes applied to the S&P 500

Quant finance project: I implement the Black-Scholes model in Python, check its assumptions on S&P 500 prices since 2000, and compare the prices with other methods.

Files:
- `pricing.py`: Black-Scholes, Monte Carlo, CRR binomial tree, implied volatility
- `sp500_black_scholes.ipynb`: the full analysis with plots
- `data/sp500.csv`: S&P 500 daily prices (2000-2026)
- `test_pricing.py`: a few tests

Main results:
- S&P 500 returns are not normal (46 days beyond 4 standard deviations instead of less than 1 expected)
- volatility is not constant (from 3% to 98% on a 1-month rolling window)
- Monte Carlo and the binomial tree give the same price as BS, so the implementation is correct
- with a Monte Carlo on historical returns, BS underprices out-of-the-money puts (about 3.7 times for a put at 85% of spot), which matches the volatility skew

To run:
```
pip install -r requirements.txt
jupyter notebook sp500_black_scholes.ipynb
pytest
```
