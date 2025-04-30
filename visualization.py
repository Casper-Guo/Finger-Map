"""Plot heatmap for keystroke data."""

from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import Callable, TypeAlias

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import Colormap

import layout

RGBA: TypeAlias = tuple[float, float, float, float]


def read_data(test_name: str) -> defaultdict[str, list[int]]:
    """Read data for the named test."""
    keystrokes = defaultdict(list)
    with Path(f"log/{test_name}.txt").open("r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            key, finger = line.split()
            keystrokes[key].append(int(finger))

    return keystrokes


def mean_colors(cmap: str, data: dict[str, list[int]]) -> tuple[dict[str, RGBA], float, float]:
    """Return per-key color based on the mean finger used."""
    cmap = sns.color_palette(cmap, as_cmap=True)
    min_finger = 100
    max_finger = -1
    min_mean = 100
    max_mean = -1
    per_key_mean = {}

    for key, finger in data.items():
        min_finger = min(min(finger), min_finger)
        max_finger = max(max(finger), max_finger)

        key_mean = mean(finger)
        min_mean = min(key_mean, min_mean)
        max_mean = max(key_mean, max_mean)

        per_key_mean[key] = key_mean

    per_key_color = {
        key: cmap((mean_value - min_mean) / (max_mean - min_mean))
        for key, mean_value in per_key_mean.items()
    }
    return per_key_color, min_finger, max_finger


def diversity_colors(
    cmap: Colormap, data: dict[str, list[int]]
) -> tuple[dict[str, RGBA], float, float]:
    """Return per-key color based on the diversity of fingers used."""
    cmap = sns.color_palette(cmap, as_cmap=True)
    min_stdev = 100
    max_stdev = -1

    per_key_stdev = {}

    for key, finger in data.items():
        key_stdev = stdev(finger)
        min_stdev = min(key_stdev, min_stdev)
        max_stdev = max(key_stdev, max_stdev)
        per_key_stdev[key] = key_stdev

    per_key_color = {
        key: cmap((stdev_value - min_stdev) / (max_stdev - min_stdev))
        for key, stdev_value in per_key_stdev.items()
    }
    return per_key_color, min_stdev, max_stdev


def plot_heatmap(
    test_name: str,
    layout_name: str,
    title: str,
    cmap: str,
    color_func: Callable[[str, dict[str, list[int]]], tuple[dict[str, RGBA], float, float]],
    **mpl_kwargs,
):
    """Plot a heatmap of keystroke data using custom data aggregator."""
    sizes, coordinates = layout.parse_layout(layout_name)
    side_length = sizes["key"]
    x_coordinates, y_coordinates = zip(*coordinates.values())
    x_min, x_max = min(x_coordinates), max(x_coordinates)
    y_min, y_max = min(y_coordinates), max(y_coordinates)

    keystroke_data = read_data(test_name)
    facecolors, cmap_min, cmap_max = color_func(cmap, keystroke_data)

    # allocate some vertical space for the color bar
    _, ax = plt.subplots(figsize=(x_max - x_min, (y_max - y_min) * 4 / 3))
    sns.set_style("white")

    for key in keystroke_data:
        key_x, key_y = coordinates[key]
        label_x, label_y = key_x + side_length / 2, key_y + side_length / 2
        ax.add_patch(
            plt.Rectangle(
                (key_x, key_y),
                width=side_length,
                height=side_length,
                facecolor=facecolors[key],
                **mpl_kwargs.get("patch", {}),
            )
        )
        plt.annotate(text=key.upper(), xy=(label_x, label_y), **mpl_kwargs.get("annotate", {}))

    norm = mpl.colors.Normalize(vmin=cmap_min, vmax=cmap_max)
    sm = plt.cm.ScalarMappable(cmap=sns.color_palette(cmap, as_cmap=True), norm=norm)

    cbar = plt.colorbar(
        mappable=sm,
        ax=ax,
        location="bottom",
        orientation="horizontal",
        fraction=0.15,
        pad=0.10,
        **mpl_kwargs.get("colorbar", {}),
    )
    cbar.set_ticklabels(mpl_kwargs.get("colorbar_ticklabels", []))

    sns.despine(left=True, bottom=True)
    ax.set_xlim((x_min, x_max + side_length))
    ax.set_ylim((y_min, y_max + side_length))
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title(title)
    plt.tight_layout()

    Path(f"graphs/{test_name}").mkdir(exist_ok=True)
    plt.savefig(f"graphs/{test_name}/{title}.png", dpi=250)
