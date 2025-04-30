"""Helper file for creating layout files."""

from pathlib import Path

layout_name = input("Enter the name of the layout: ")
key_size = float(input("Enter side length of the keys (usually 1): "))
spacing_size = float(input("Enter spacing size: "))
offset_size = float(input("Enter offset size: "))

keyboard_rows = []
row_index = 1

while True:
    row = input(
        f"Enter row {row_index} of the keyboard, from top to bottom. Enter nothing to stop: "
    )

    if not row:
        break

    row = "".join([key.lower() if key.isalpha() else key for key in row])
    keyboard_rows.append(row)
    row_index += 1


with Path(f"layout/{layout_name}.txt").open("w", encoding="utf-8") as f:
    f.write(f"{key_size}\n")
    f.write(f"{spacing_size}\n")
    f.write(f"{offset_size}\n")
    for row in keyboard_rows:
        f.write(f"{row}\n")
