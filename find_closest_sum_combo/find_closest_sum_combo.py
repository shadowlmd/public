#!/usr/bin/env python3

from itertools import combinations
from sys import argv


def find_closest_sum_combo(numbers, goal):
    """Searches for shortest combination of numbers which sum() is closest to the goal"""
    best_sum = 0
    best_combo = ()
    for r in range(1, len(numbers) + 1):
        for combo in combinations(numbers, r):
            combo_sum = sum(combo)
            if combo_sum == goal:
                return combo
            elif combo_sum < goal and combo_sum > best_sum:
                best_sum = combo_sum
                best_combo = combo
    return best_combo


if __name__ == '__main__':
    if len(argv) < 3:
        print(f'Usage: {argv[0]} goal number1 number2 ...')
        exit(1)

    goal = float(argv[1])
    numbers = [float(i) for i in argv[2:]]

    res = find_closest_sum_combo(goal=goal, numbers=numbers)

    print(f'sum{res} =', format(sum(res), '.2f').rstrip('0').rstrip('.'))
