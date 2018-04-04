"""Pearson correlation."""

from math import sqrt


def pearson(common_critics):
    """Return Pearson correlation for common_critics.
    Using a set of pairwise ratings, produces a Pearson similarity rating.
    """

    film1 = [float(pair[0]) for pair in common_critics]
    film2 = [float(pair[1]) for pair in common_critics]

    film1_sum = sum(film1)
    film2_sum = sum(film2)

    film1_square = sum([n * n for n in film1])
    film2_square = sum([n * n for n in film2])

    num_critics = len(common_critics)

    product_sum = sum([n * m for n, m in common_critics])

    numerator = product_sum - ((film1_sum * film2_sum) / num_critics)

    denominator = sqrt(
        (film1_square - pow(film1_sum, 2) / num_critics) *
        (film2_square - pow(film2_sum, 2) / num_critics)
    )

    if denominator == 0:
        return 0

    return numerator / denominator
