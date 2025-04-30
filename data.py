"""Sample random words from language corpora and record typing statitistics."""

import random
from collections import Counter
from pathlib import Path

import wordfreq


def get_zipf_frequency(lang: str, wordlist: str) -> dict[str, float]:
    """Map words to their Zipf scale frequency."""
    word_freq = wordfreq.get_frequency_dict(lang, wordlist)

    return {key: wordfreq.freq_to_zipf(val) for key, val in word_freq.items() if key.isalpha()}


def split_by_letter(freq_dict: dict[str, float]) -> dict[str, dict[str, float]]:
    """Make a index of word frequency by the letters they contain."""
    letter_index = {}

    for word, freq in freq_dict.items():
        for letter in word:
            if letter not in letter_index:
                letter_index[letter] = {}
            letter_index[letter][word] = freq

    return letter_index


def generate_finger_mapping(lhs: int = 3, rhs: int = 3) -> dict[str, int]:
    """
    Map fingers to a number, counting from left to right.

    If three fingers, assume index, middle, and ring.
    If four fingers, assume index, middle, ring, and pinky.
    If five fingers, assume index, middle, ring, pinky, and thumb.
    """
    match lhs:
        case 3:
            lhs_fingers = {"L_ring": 1, "L_Middle": 2, "L_Index": 3}
        case 4:
            lhs_fingers = {"L_Pinky": 1, "L_Index": 2, "L_Middle": 3, "L_Ring": 4}
        case 5:
            lhs_fingers = {"L_Pinky": 1, "L_Index": 2, "L_Middle": 3, "L_Ring": 4, "L_Thumb": 5}
        case _:
            lhs_fingers = {f"L_Finger{i}": i for i in range(1, lhs + 1)}

    match rhs:
        case 3:
            rhs_fingers = {"R_Index": lhs + 1, "R_Middle": lhs + 2, "R_ring": lhs + 3}
        case 4:
            rhs_fingers = {
                "R_Index": lhs + 1,
                "R_Middle": lhs + 2,
                "R_Ring": lhs + 3,
                "R_Pinky": lhs + 4,
            }
        case 5:
            rhs_fingers = {
                "R_Thumb": lhs + 1,
                "R_Index": lhs + 2,
                "R_Middle": lhs + 3,
                "R_Ring": lhs + 4,
                "R_Pinky": lhs + 5,
            }
        case _:
            rhs_fingers = {f"R_Finger{i}": lhs + i for i in range(1, rhs + 1)}

    return lhs_fingers | rhs_fingers


def request_input(char: str) -> int:
    """Prompt user until they have entered the expected character along with a finger index."""
    while True:
        try:
            finger = input(f"Enter {char}, followed by the finger you would use to type it: ")
            if not finger:
                continue
            if finger[0] == char and finger[1:].isdigit():
                return int(finger[1:])
        except EOFError:
            return -1


def find_min_count_letter(available_letters: list[str], seen_words: set[str]) -> str:
    """Find the letter that has so far been typed the least."""
    if not seen_words:
        return random.choice(available_letters)

    letter_count = Counter()
    for word in seen_words:
        letter_count.update(word)

    letter_freq = {letter: letter_count.get(letter, 0) for letter in available_letters}
    return min(letter_freq, key=letter_freq.get)


def select_word(
    freq_dict: dict[str, float],
    letter_index: dict[str, dict[str, float]],
    seen_words: set[str],
    algorithm: str,
    no_repeat: bool,
    available_letters: list[str],
) -> str:
    """Select a test word from a corpus."""
    if algorithm == "letter":
        min_count_letter = find_min_count_letter(available_letters, seen_words)

    words, freqs = zip(*freq_dict.items())

    while True:
        match algorithm:
            case "random":
                word = random.choice(words)
            case "freq":
                word = random.choices(words, weights=freqs, k=1)[0]
            case "letter":
                candidate_words = letter_index[min_count_letter]
                word = random.choices(
                    list(candidate_words.keys()), weights=list(candidate_words.values()), k=1
                )[0]
            case _:
                raise NotImplementedError

        for letter in word:
            if letter not in available_letters:
                continue

        if not no_repeat or word not in seen_words:
            return word


def collect_data(
    freq_dict: dict[str, float],
    log_path: str,
    finger_mapping: dict[str, int],
    max_word: int,
    max_char: int,
    algorithm: str,
    no_repeat: bool,
    available_letters: list[str],
):
    """Sample random words and collect typing statistics."""
    num_words = 0
    num_char = 0

    letter_index = split_by_letter(freq_dict)
    seen_words = set()

    print("You have specified the following finger mapping:")
    for finger, index in finger_mapping.items():
        print(f"{finger} -> {index}")

    with Path(f"log/{log_path}.txt").open("w", encoding="utf-8") as log:
        while num_char < max_char and num_words < max_word:
            word = select_word(
                freq_dict, letter_index, seen_words, algorithm, no_repeat, available_letters
            )
            seen_words.add(word)

            print(f"\nTyping: {word}")

            for char in word:
                finger = request_input(char)

                if finger == -1:
                    # exit immediately when ctrl+d is received
                    return

                log.write(f"{char} {finger}\n")

            num_words += 1
            num_char += len(word)
