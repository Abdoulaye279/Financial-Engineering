# Financial Engineering

My quant finance projects.

## 1. Black-Scholes applied to the S&P 500 (`black-scholes-sp500/`)

I implement Black-Scholes in Python, test its assumptions on S&P 500 daily prices since 2000, and compare it with Monte Carlo, a binomial tree and a Monte Carlo on historical returns.

Main result: returns are not normal and volatility is not constant, so Black-Scholes underprices out-of-the-money puts (volatility skew).

Open in Colab: [sp500_black_scholes.ipynb](https://colab.research.google.com/github/Abdoulaye279/Financial-Engineering/blob/main/black-scholes-sp500/sp500_black_scholes.ipynb)

## 2. VaR and Expected Shortfall on the S&P 500 (`var-es-sp500/`)

I compare five risk models (normal, historical, GARCH, filtered historical simulation and GARCH with extreme value theory) and backtest their 99% VaR and ES day by day from 2004 to 2026 with the Kupiec and Christoffersen tests.

Main result: the normal model has 2.3 times more breaches than expected. Only the models that combine a GARCH volatility with a non-normal tail (FHS, GARCH-EVT) get close to 1% with an almost exact ES.

Open in Colab: [sp500_var_es.ipynb](https://colab.research.google.com/github/Abdoulaye279/Financial-Engineering/blob/main/var-es-sp500/sp500_var_es.ipynb)

## 3. Lehman Brothers 2008 with an LLM (`lehman-ai-agents/`)

I use Gemini to find bankruptcy warning signs in Lehman's July 2008 10-Q, with an exact quote for each one, and compare two methods: sending the full filing (Part 1) and RAG with a vector database (Part 2).

Main result: RAG costs about 7 times fewer tokens per question but finds fewer warning signs (7 against 10) and its quotes are less reliable (2/7 found word for word in the filing, against 7/10 with the full filing). Checking the quotes automatically is necessary.

Open in Colab: [part1_full_context.ipynb](https://colab.research.google.com/github/Abdoulaye279/Financial-Engineering/blob/main/lehman-ai-agents/part1_full_context.ipynb), [part2_rag.ipynb](https://colab.research.google.com/github/Abdoulaye279/Financial-Engineering/blob/main/lehman-ai-agents/part2_rag.ipynb) (needs a Gemini API key)
