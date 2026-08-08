from __future__ import annotations

import math

import numpy as np
import pandas as pd


TRAVEL_TIMES = np.array(
    [
        12, 13, 15, 17, 18, 18, 20, 22,
        23, 24, 25, 25, 26, 27, 28, 29,
        30, 31, 32, 33, 34, 35, 35, 36,
        37, 38, 39, 40, 42, 44, 46, 48,
        50, 52, 55, 58, 62, 66, 70, 76,
    ],
    dtype=float,
)


def approximate_class_width(data: np.ndarray, class_count: int) -> float:
    if class_count <= 0:
        raise ValueError("Sınıf sayısı pozitif olmalıdır.")
    return (float(np.max(data)) - float(np.min(data))) / class_count


def class_edges(data: np.ndarray, width: int) -> np.ndarray:
    if width <= 0:
        raise ValueError("Sınıf genişliği pozitif olmalıdır.")
    start = math.floor(float(np.min(data)) / width) * width
    stop = math.ceil(float(np.max(data)) / width) * width
    if stop <= float(np.max(data)):
        stop += width
    return np.arange(start, stop + width, width, dtype=float)


def grouped_frequency(data: np.ndarray, width: int) -> pd.DataFrame:
    edges = class_edges(data, width)
    counts, used_edges = np.histogram(data, bins=edges)
    rows = []
    n = len(data)
    running = 0
    for i, count in enumerate(counts):
        lower = used_edges[i]
        upper = used_edges[i + 1]
        running += int(count)
        rows.append(
            {
                "Alt sınır": lower,
                "Üst sınır": upper,
                "Sınıf": f"{lower:g}–<{upper:g}",
                "Orta nokta": (lower + upper) / 2,
                "Frekans": int(count),
                "Göreli frekans": count / n,
                "Yüzde frekans": 100 * count / n,
                "Kümülatif frekans": running,
                "Kümülatif yüzde": 100 * running / n,
            }
        )
    return pd.DataFrame(rows)


def stem_leaf(data: np.ndarray) -> list[tuple[int, str]]:
    ints = sorted(int(x) for x in data)
    stems: dict[int, list[int]] = {}
    for value in ints:
        stem, leaf = divmod(value, 10)
        stems.setdefault(stem, []).append(leaf)
    return [(stem, " ".join(str(x) for x in leaves)) for stem, leaves in stems.items()]
