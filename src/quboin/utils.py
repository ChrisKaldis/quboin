"""Basic utility functions for the quboin package.

Includes helper functions to:
-Read integer input files,
"""

import os


def read_integers_from_file(filename: str) -> list[int]:
    """Reads integers from a text file where each line contains one integer.

    This function is used in order to read the data used in knapsack example.

    Args:
        filename: Path to the text file containing one integer per line.

    Returns:
        A list of integers parsed from the file.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If a line doesn't contain a valid integer.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The file '{filename}' was not found.")

    integers: list[int] = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            # Strip in case of whitespaces or empty lines
            stripped_line = line.strip()
            if stripped_line:
                try:
                    integers.append(int(stripped_line))
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid integer found in {filename}: {exc}"
                    ) from exc

    return integers
