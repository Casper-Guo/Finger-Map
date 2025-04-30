"""
Parse layout text files.

The first three rows should specify the key size, spacing size, and offset size in order.

Each subsequent row should correspond to a row on your keyboard.
"""

# TODO: Allows specifying multi-level layouts (fn layers etc.)
from pathlib import Path


def available_letters(layout: str) -> list[str]:
    """Get the available letters on the keyboard layout."""
    with Path(f"layout/{layout}.txt").open("r", encoding="utf-8") as f:
        lines = f.read().splitlines()[3:]
        return list("".join(lines))


def parse_layout(layout: str) -> tuple[dict[str, float], dict[str, tuple[float, float]]]:
    """
    Translate the layout to xy positions for matplotlib.

    Positions are given for the bottom left corners of keys.

    key_size refers to the side length of a key.

    spacing_size refers to the width of the gaps between keys.

    offset_size refers to the horizontal offset of a row from the row above.

    These three parameters should be provided as the first three rows of a layout file.
    """
    key_positions = {}
    with Path(f"layout/{layout}.txt").open("r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    key_size = float(lines[0])
    spacing_size = float(lines[1])
    offset_size = float(lines[2])

    key_rows = lines[3:]
    for row_index, row in enumerate(key_rows):
        # matplotlib y values increase upwards
        mpl_y = len(key_rows) - row_index - 1
        row_y = mpl_y * (key_size + spacing_size)
        row_offset = offset_size * row_index
        for col_index, key in enumerate(row):
            key_x = col_index * (key_size + spacing_size) + row_offset
            key_positions[key] = (key_x, row_y)

    return {"key": key_size, "spacing": spacing_size, "offset": offset_size}, key_positions
