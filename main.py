"""Collect typing data and produce visualizations."""

import argparse
from datetime import datetime
from pathlib import Path

import wordfreq

import data
import layout
import visualization


def get_parser() -> argparse.ArgumentParser:
    """Set up CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Visualize what finger you use to type each key. "
            "Test stops when either word or character limit is reached."
        ),
    )
    parser.add_argument(
        "left_hand",
        type=int,
        help="Number of left hand fingers you use to type.",
    )
    parser.add_argument(
        "right_hand",
        type=int,
        help="Number of right hand fingers you use to type.",
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        default=str(datetime.now()),
        help="Name of the test. Default: time of the test",
    )
    parser.add_argument(
        "--layout",
        type=str,
        default="qwerty_en",
        help=(
            "Keyboard layout to use. "
            "These can be specified under the layout directory. Default: qwerty_en"
        ),
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="en",
        choices=wordfreq.available_languages().keys(),
        help="Language to use for word generation. Default: en",
    )
    parser.add_argument(
        "--wordlist",
        type=str,
        default="small",
        choices=["small", "best"],
        help="Selecting best will use the large wordlist whenever available. Default: small",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=30,
        help="Number of words to test. Default: 30",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=200,
        help="Number of characters to test. Default: 200",
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        default="letter",
        choices=["letter", "freq", "random"],
        help=(
            "Algorithms for word generation. "
            "Letter is the default and tries to collect data for all keys equally. "
            "Freq samples based on word frequency. "
            "Random is true random sampling."
        ),
    )
    parser.add_argument(
        "--no-repeat",
        action="store_true",
        help="Ensure test words are not repeated.",
    )
    parser.add_argument(
        "--plot-only",
        action="store_true",
        help="Skip the testing phase and produce visualizations directly.",
    )
    parser.add_argument(
        "--cmap",
        type=str,
        default="Spectral",
        choices=[
            "PiYG",
            "PRGn",
            "BrBG",
            "PuOr",
            "RdGy",
            "RdBu",
            "RdYlBu",
            "RdYlGn",
            "Spectral",
            "coolwarm",
            "bwr",
            "seismic",
            "berlin",
            "managua",
            "vanimo",
        ],
        help="Colormap to use for visualizations. Default: Spectral",
    )
    return parser


def main():
    """Driver for running test and visualization."""
    args = get_parser().parse_args()
    finger_mapping = data.generate_finger_mapping(args.left_hand, args.right_hand)

    if not args.plot_only:
        Path("log").mkdir(exist_ok=True)

        data.collect_data(
            data.get_zipf_frequency(args.lang, args.wordlist),
            args.name,
            finger_mapping,
            args.max_words,
            args.max_chars,
            args.algorithm,
            args.no_repeat,
            layout.available_letters(args.layout),
        )

    visualization.plot_heatmap(
        args.name,
        args.layout,
        "Finger Map",
        args.cmap,
        visualization.mean_colors,
        patch={"edgecolor": "black", "linewidth": 1},
        annotate={
            "fontfamily": "monospace",
            "fontsize": "large",
            "ha": "center",
            "va": "center",
        },
        colorbar={
            "label": "Finger Color Code",
            "ticks": range(1, args.left_hand + args.right_hand + 1),
        },
        colorbar_ticklabels=[
            finger for finger, _ in sorted(finger_mapping.items(), key=lambda x: x[1])
        ],
    )

    visualization.plot_heatmap(
        args.name,
        args.layout,
        "Keystroke Diversity",
        args.cmap,
        visualization.diversity_colors,
        patch={"edgecolor": "black", "linewidth": 1},
        annotate={
            "fontfamily": "monospace",
            "fontsize": "large",
            "ha": "center",
            "va": "center",
        },
    )


if __name__ == "__main__":
    main()
