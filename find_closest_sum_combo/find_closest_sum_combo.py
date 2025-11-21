#!/usr/bin/env python3

import sys
from itertools import combinations
from pathlib import Path

SCRIPTNAME = Path(__file__).name


def find_closest_sum_combo(numbers: list[float], goal: float) -> tuple[float, ...]:
    """Search for shortest combination of numbers which sum() is closest to the goal."""
    best_sum = 0
    best_combo = ()
    for r in range(1, len(numbers) + 1):
        for combo in combinations(numbers, r):
            combo_sum = sum(combo)
            if combo_sum == goal:
                return combo
            if combo_sum < goal and combo_sum > best_sum:
                best_sum = combo_sum
                best_combo = combo
    return best_combo


if __name__ == "__main__":
    if len(sys.argv) < 3:  # noqa: PLR2004
        print(f"Usage: {SCRIPTNAME} goal number1 number2 ...")
        sys.exit(1)

    goal = float(sys.argv[1])
    numbers = [float(i) for i in sys.argv[2:]]

    res = find_closest_sum_combo(goal=goal, numbers=numbers)

    print(f"sum{res} =", f"{sum(res):.2f}".rstrip("0").rstrip("."))
