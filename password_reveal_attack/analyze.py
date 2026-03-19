#!/usr/bin/env python3
"""
Multi-strategy analysis of collected acrostics.

Three strategies for generating password candidates:
1. Exact frequency — top 10 most common complete acrostic strings
2. Joint probability — top 10 candidates by combining likely letters at each position
3. Length-grouped — best candidate per observed length group
"""

import heapq
from collections import Counter


def _positional_distributions(acrostics):
    """Build letter frequency distribution for each position."""
    if not acrostics:
        return []
    max_len = max(len(a) for a in acrostics)
    distributions = []
    for pos in range(max_len):
        letters = [a[pos] for a in acrostics if pos < len(a)]
        if not letters:
            break
        freq = Counter(letters)
        total = len(letters)
        # list of (letter, probability) sorted by probability desc
        dist = [(l, c / total) for l, c in freq.most_common()]
        distributions.append(dist)
    return distributions


def _print_positional_table(distributions):
    """Print the positional frequency table."""
    print(f"  {'Pos':<5} {'Best':<6} {'Prob':>6}  Distribution")
    print(f"  {'-' * 60}")
    for pos, dist in enumerate(distributions):
        best_letter, best_prob = dist[0]
        dist_str = ", ".join(f"{l}:{p:.0%}" for l, p in dist[:5])
        print(f"    {pos+1:<3} {best_letter:<6} {best_prob:>5.0%}  {dist_str}")


def strategy_exact_frequency(acrostics, top_n=10):
    """Strategy 1: Top N most frequently occurring complete acrostic strings."""
    print("=" * 70)
    print("STRATEGY 1: EXACT FREQUENCY")
    print("Top 10 most common complete acrostic strings")
    print("=" * 70)

    freq = Counter(acrostics)
    total = len(acrostics)

    for rank, (acrostic, count) in enumerate(freq.most_common(top_n), 1):
        pct = count / total
        print(f"  #{rank:<3} {acrostic:<20} ({count}x, {pct:.0%})")

    print()


def _filter_outliers(acrostics):
    """Filter out acrostics with extreme lengths (< 2 occurrences)."""
    length_counts = Counter(len(a) for a in acrostics)
    valid_lengths = {l for l, c in length_counts.items() if c >= 2}
    if not valid_lengths:
        return acrostics
    return [a for a in acrostics if len(a) in valid_lengths]


def strategy_joint_probability(acrostics, top_n=10):
    """Strategy 2: Top N candidates by joint positional probability.

    At each position, consider the top letters (those covering 95% of
    probability mass). Generate candidates by combinatorial search,
    ranked by the product of per-position probabilities.

    Acrostics with unique lengths (only 1 occurrence) are filtered out
    to avoid outlier positions polluting the results.
    """
    print("=" * 70)
    print("STRATEGY 2: JOINT PROBABILITY")
    print("Top 10 candidates by product of per-position letter probabilities")
    print("=" * 70)

    acrostics = _filter_outliers(acrostics)
    distributions = _positional_distributions(acrostics)
    if not distributions:
        print("  No data.")
        print()
        return

    _print_positional_table(distributions)
    print()

    # At each position, keep letters covering 95% of probability mass
    # (but at least top 2 if there are alternatives)
    candidates_per_pos = []
    for dist in distributions:
        kept = []
        cumulative = 0.0
        for letter, prob in dist:
            kept.append((letter, prob))
            cumulative += prob
            if cumulative >= 0.95 and len(kept) >= 2:
                break
        candidates_per_pos.append(kept)

    # Use a max-heap (negate probs) to find top-N candidates efficiently.
    # Start with the best candidate (all top-1 letters), then explore
    # alternatives by substituting one position at a time.
    #
    # State: (neg_joint_prob, list_of_indices_into_candidates_per_pos)
    initial_indices = [0] * len(candidates_per_pos)
    initial_prob = 1.0
    for pos, idx in enumerate(initial_indices):
        initial_prob *= candidates_per_pos[pos][idx][1]

    heap = [(-initial_prob, initial_indices)]
    seen = {tuple(initial_indices)}
    results = []

    while heap and len(results) < top_n:
        neg_prob, indices = heapq.heappop(heap)
        prob = -neg_prob
        word = "".join(candidates_per_pos[pos][idx][0]
                       for pos, idx in enumerate(indices))
        results.append((word, prob))

        # Generate neighbors: increment one index at a time
        for pos in range(len(indices)):
            if indices[pos] + 1 < len(candidates_per_pos[pos]):
                new_indices = list(indices)
                new_indices[pos] += 1
                key = tuple(new_indices)
                if key not in seen:
                    seen.add(key)
                    new_prob = 1.0
                    for p, idx in enumerate(new_indices):
                        new_prob *= candidates_per_pos[p][idx][1]
                    heapq.heappush(heap, (-new_prob, new_indices))

    print("  Candidates:")
    for rank, (word, prob) in enumerate(results, 1):
        print(f"  #{rank:<3} {word:<20} (prob: {prob:.4f})")

    print()


def strategy_length_grouped(acrostics, top_n=10):
    """Strategy 3: Separate positional analysis per length group."""
    print("=" * 70)
    print("STRATEGY 3: LENGTH-GROUPED")
    print("Best candidate per acrostic length group")
    print("=" * 70)

    length_groups = {}
    for a in acrostics:
        length_groups.setdefault(len(a), []).append(a)

    for length in sorted(length_groups.keys(), reverse=True):
        group = length_groups[length]
        distributions = _positional_distributions(group)
        best_word = "".join(d[0][0] for d in distributions)
        avg_conf = sum(d[0][1] for d in distributions) / len(distributions)
        print(f"  Length {length} (n={len(group):>3}):  {best_word:<20} "
              f"(avg conf: {avg_conf:.0%})")

    print()


def run_analysis(acrostics):
    """Run all strategies on the given acrostics."""
    if not acrostics:
        print("No acrostics collected -- cannot perform analysis.")
        return

    print(f"Total acrostics: {len(acrostics)}")
    length_counts = Counter(len(a) for a in acrostics)
    print(f"Length distribution: {dict(length_counts.most_common())}")
    print()

    strategy_exact_frequency(acrostics)
    strategy_joint_probability(acrostics)
    strategy_length_grouped(acrostics)
