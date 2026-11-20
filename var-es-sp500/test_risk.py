import numpy as np
import pandas as pd
from scipy import stats
from risk import evt_tail, var_es_normal, var_es_hist, garch_filter, garch_fit, kupiec, christoffersen, backtest

rng = np.random.default_rng(0)


def simulate_garch(n, omega=2e-6, a=0.08, b=0.9):
    r, s2 = np.empty(n), omega / (1 - a - b)
    for t in range(n):
        r[t] = np.sqrt(s2) * rng.standard_normal()
        s2 = omega + a * r[t] ** 2 + b * s2
    return r


def test_normal_and_hist_on_normal_data():
    r = rng.normal(0, 0.01, 1_000_000)
    var_n, es_n = var_es_normal(r)
    var_h, es_h = var_es_hist(r)
    assert abs(var_n - 0.02326) < 1e-4 and abs(es_n - 0.02665) < 1e-4   # 2.326 sd and 2.665 sd
    assert abs(var_h - var_n) < 2e-4 and abs(es_h - es_n) < 2e-4


def test_garch_recovers_parameters():
    omega, a, b = garch_fit(simulate_garch(20_000))
    assert abs(a - 0.08) < 0.02 and abs(b - 0.9) < 0.03
    assert abs(omega / (1 - a - b) - 1e-4) < 3e-5   # long-run variance


def test_evt_on_student_t():
    # fat tailed data: EVT should find the true 99% quantile and ES of a Student-t(4)
    x = stats.t.rvs(4, size=200_000, random_state=1)
    var, es = evt_tail(x)
    true_var = stats.t.ppf(0.99, 4)
    true_es = stats.t.expect(lambda y: y, args=(4,), lb=true_var) / 0.01
    assert abs(var / true_var - 1) < 0.03 and abs(es / true_es - 1) < 0.05


def test_kupiec():
    good = np.zeros(10_000, bool); good[::100] = True       # exactly 1%
    bad = np.zeros(10_000, bool); bad[::40] = True          # 2.5%
    assert kupiec(good)[1] > 0.5 and kupiec(bad)[1] < 1e-6


def test_christoffersen():
    spread = np.zeros(10_000, bool); spread[::100] = True
    clustered = np.zeros(10_000, bool)
    for s in range(0, 10_000, 500):
        clustered[s:s + 5] = True                          # breaches come in groups of 5
    assert christoffersen(spread)[1] > 0.05 and christoffersen(clustered)[1] < 1e-6


def test_backtest_on_garch_data():
    r = pd.Series(simulate_garch(3000), index=pd.bdate_range("2000-01-03", periods=3000))
    bt = backtest(r, window=1000, refit=250)
    assert len(bt) == 2000 and not bt.isna().any().any()
    rate = (bt["ret"] < -bt["var_garch"]).mean()
    assert 0.003 < rate < 0.02    # close to 1% when the model is right
    for m in ["normal", "hist", "garch", "fhs", "evt"]:
        assert (bt[f"es_{m}"] >= bt[f"var_{m}"]).all()
