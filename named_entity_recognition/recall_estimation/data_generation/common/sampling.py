import numpy as np
from numpy.typing import NDArray

def balance_sample_sizes(Lambda: NDArray[float], expected_sample_count: int) -> NDArray[int]:
    """
    Returns optimal sample sizes for sub-populations given frequencies of the sub-populations.
    The total number of samples approximately matches the expected sample count.

    Sample sizes are computed to minimise the variance of an event proportion over the  entire
    population provided that the event probilities in sub-populations are roughly equal.
    In the recall setting, all positive cases are split into sub-populations and the event
    marks the fact that an algorithm accepts the positive case.
    """
    return np.round(Lambda/sum(Lambda) * expected_sample_count).astype(int)
