"""Reliability check: many seeded bot-only tournaments, with confidence bounds.

Runs `simulate.play_tournament` for a range of seeds in fast mode and counts
  * failures: any broken invariant, crash or stuck hand (an exception), and
  * unfinished tournaments: nobody had all the chips after the hand cap.
It then prints exact (Clopper-Pearson) 95% bounds for the failure rate and the
completion rate. With zero failures in n runs the upper bound is close to 3/n
(the "rule of three").

Usage: python3 tournament_stats.py [--seed 1] [--tournaments 1000]
"""
import argparse
import statistics
import time
from math import comb

from simulate import play_tournament


def _tail_up(k, n, p):
    """P(X >= k) for X ~ Binomial(n, p)."""
    return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))


def _tail_down(k, n, p):
    """P(X <= k) for X ~ Binomial(n, p)."""
    return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(0, k + 1))


def clopper_pearson(k, n, alpha=0.05):
    """Exact two-sided (1 - alpha) interval for a proportion k out of n."""
    lower = 0.0
    if k > 0:
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if _tail_up(k, n, mid) < alpha / 2:
                lo = mid
            else:
                hi = mid
        lower = lo
    upper = 1.0
    if k < n:
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if _tail_down(k, n, mid) > alpha / 2:
                lo = mid
            else:
                hi = mid
        upper = hi
    return lower, upper


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=1, help="first seed")
    parser.add_argument("--tournaments", type=int, default=1000)
    arguments = parser.parse_args(argv)

    failures = []
    finished = 0
    hands, actions, illegal = [], 0, 0
    started = time.perf_counter()
    last = arguments.seed + arguments.tournaments
    for seed in range(arguments.seed, last):
        try:
            result = play_tournament(seed)
        except Exception as error:  # a broken invariant, crash or stuck hand
            failures.append((seed, f"{type(error).__name__}: {str(error)[:120]}"))
            continue
        finished += 1 if result["finished"] else 0
        hands.append(result["hands"])
        actions += result["actions"]
        illegal += result["illegal_bot_actions"]
    seconds = time.perf_counter() - started

    n = arguments.tournaments
    k_fail = len(failures)
    unfinished = len(hands) - finished
    print(f"tournaments run:        {n} (seeds {arguments.seed} to {last - 1}), {seconds:.1f} s")
    print(f"failures (exceptions):  {k_fail}")
    for seed, message in failures[:5]:
        print(f"   seed {seed}: {message}")
    print(f"finished (one winner):  {finished} of {len(hands)} completed runs")
    print(f"hit the hand cap:       {unfinished}")
    if hands:
        print(f"hands per tournament:   mean {statistics.mean(hands):.0f}, median "
              f"{statistics.median(hands):.0f}, min {min(hands)}, max {max(hands)}")
    print(f"actions checked:        {actions}")
    print(f"illegal bot actions:    {illegal}")

    _, fail_hi = clopper_pearson(k_fail, n)
    print(f"failure rate:           {k_fail}/{n}; 95% upper bound {fail_hi:.2%}"
          + ("  (rule of three: 3/n = %.2f%%)" % (300 / n) if k_fail == 0 else ""))
    if hands:
        low, high = clopper_pearson(finished, len(hands))
        print(f"completion rate:        {finished}/{len(hands)} = {finished / len(hands):.1%}; "
              f"95% interval {low:.1%} to {high:.1%}")


if __name__ == "__main__":
    main()
