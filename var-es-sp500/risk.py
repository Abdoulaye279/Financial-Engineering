# VaR and ES models for daily returns: normal, historical, GARCH(1,1), filtered historical
# simulation and GARCH-EVT, plus the Kupiec and Christoffersen backtests.
# VaR and ES are given as positive losses.
import numpy as np
from scipy import stats, optimize
from scipy.special import xlogy


def var_es_normal(r, alpha=0.99):
    mu, sd = r.mean(), r.std(ddof=1)
    z = stats.norm.ppf(1 - alpha)
    return -(mu + sd * z), -(mu - sd * stats.norm.pdf(z) / (1 - alpha))


def var_es_hist(r, alpha=0.99):
    q = np.quantile(r, 1 - alpha)
    return -q, -r[r <= q].mean()


def garch_filter(r, omega, a, b):
    # conditional variances; s2[t] uses returns up to t-1, the last one is the forecast for the next day
    s2 = np.empty(len(r) + 1)
    s2[0] = r.var()
    for t in range(len(r)):
        s2[t + 1] = omega + a * r[t] ** 2 + b * s2[t]
    return s2


def garch_fit(r):
    # GARCH(1,1) fitted by maximum likelihood (normal), returns omega, alpha, beta
    x = 100 * (r - r.mean())   # in percent, the optimizer works better with this scale

    def nll(p):
        s2 = garch_filter(x, *p)[:-1]
        return 0.5 * np.sum(np.log(s2) + x ** 2 / s2)

    res = optimize.minimize(nll, [0.05 * x.var(), 0.08, 0.9], method="SLSQP",
                            bounds=[(1e-8, None), (0, 1), (0, 1)],
                            constraints=[{"type": "ineq", "fun": lambda p: 0.9999 - p[1] - p[2]}])
    omega, a, b = res.x
    return omega / 1e4, a, b


def evt_tail(losses, alpha=0.99, tail=0.1):
    # fit a generalized Pareto distribution to the largest 10% of losses (peaks over threshold)
    # and use it for the VaR and ES quantile instead of the empirical one
    u = np.quantile(losses, 1 - tail)
    excess = losses[losses > u] - u
    xi, _, beta = stats.genpareto.fit(excess, floc=0)
    var = u + beta / xi * (((1 - alpha) / tail) ** (-xi) - 1)
    es = (var + beta - xi * u) / (1 - xi)
    return var, es


def kupiec(breaches, alpha=0.99):
    # is the breach rate equal to 1 - alpha? returns LR stat and p-value
    T, x, p = len(breaches), breaches.sum(), 1 - alpha
    lr = -2 * (xlogy(T - x, 1 - p) + xlogy(x, p) - xlogy(T - x, 1 - x / T) - xlogy(x, x / T))
    return lr, stats.chi2.sf(lr, 1)


def christoffersen(breaches):
    # is a breach more likely the day after a breach? returns LR stat and p-value
    b = np.asarray(breaches, dtype=int)
    prev, cur = b[:-1], b[1:]
    n00, n01 = np.sum((prev == 0) & (cur == 0)), np.sum((prev == 0) & (cur == 1))
    n10, n11 = np.sum((prev == 1) & (cur == 0)), np.sum((prev == 1) & (cur == 1))
    p0, p1 = n01 / (n00 + n01), n11 / max(n10 + n11, 1)
    p = (n01 + n11) / (n00 + n01 + n10 + n11)
    ll_h0 = xlogy(n00 + n10, 1 - p) + xlogy(n01 + n11, p)
    ll_h1 = xlogy(n00, 1 - p0) + xlogy(n01, p0) + xlogy(n10, 1 - p1) + xlogy(n11, p1)
    lr = -2 * (ll_h0 - ll_h1)
    return lr, stats.chi2.sf(lr, 1)


def backtest(r, alpha=0.99, window=1000, refit=250):
    # VaR and ES for the next day, for every day after the first `window` days.
    # each model only sees the past `window` returns, GARCH is refitted every `refit` days
    import pandas as pd
    v = r.values
    out = {k: np.full(len(v), np.nan) for k in
           ["var_normal", "es_normal", "var_hist", "es_hist", "var_garch", "es_garch", "var_fhs", "es_fhs", "var_evt", "es_evt"]}
    zq = stats.norm.ppf(1 - alpha)
    for start in range(window, len(v), refit):
        past = v[start - window:start]
        mu = past.mean()
        omega, a, b = garch_fit(past)
        # filter through the fitting window and the next block with the same parameters
        block = v[start - window:min(start + refit, len(v))] - mu
        s = np.sqrt(garch_filter(block, omega, a, b))
        z = (past - mu) / s[:window]            # standardised residuals of the fitting window
        q = np.quantile(z, 1 - alpha)
        z_tail = z[z <= q].mean()
        evt_var, evt_es = evt_tail(-z, alpha)
        for t in range(start, min(start + refit, len(v))):
            w = v[t - window:t]
            out["var_normal"][t], out["es_normal"][t] = var_es_normal(w, alpha)
            out["var_hist"][t], out["es_hist"][t] = var_es_hist(w, alpha)
            st = s[t - start + window]            # GARCH vol forecast for day t
            out["var_garch"][t] = -(mu + st * zq)
            out["es_garch"][t] = -(mu - st * stats.norm.pdf(zq) / (1 - alpha))
            out["var_fhs"][t] = -(mu + st * q)
            out["es_fhs"][t] = -(mu + st * z_tail)
            out["var_evt"][t] = -mu + st * evt_var
            out["es_evt"][t] = -mu + st * evt_es
    df = pd.DataFrame(out, index=r.index)
    df.insert(0, "ret", v)
    return df.iloc[window:]
