import bisect
import os
import random
import sqlite3
import string
import textwrap
from collections import Counter
from pathlib import Path

DATA_ROOT = Path(__file__).parent.resolve() / 'data'
with open(DATA_ROOT / 'winning_words.txt', 'r') as f:
    WINNING_WORDS = f.read().splitlines()

with open(DATA_ROOT / 'words.txt', 'r') as f:
    ALL_WORDS = f.read().splitlines()

NUM_GUESSES = 6
GREEN = '\033[42m'
YELLOW = '\033[43m'
OFF = '\033[m'
ROW_1 = 'qwertyuiop'
ROW_2 = 'asdfghjkl'
ROW_3 = 'zxcvbnm'

# index of value refers to knowledge.
# 0: not in word, 1: unknown, 2: wrong location, 3: correct
CHARACTER_DISPLAY = {
    ch: ('_', ch, f'{YELLOW}{ch}{OFF}', f'{GREEN}{ch}{OFF}')
    for ch in string.ascii_lowercase
}
character_knowledge = {ch: 1 for ch in string.ascii_lowercase}

past_guesses = []


def format_row(chars):
    return ' '.join(
        CHARACTER_DISPLAY[ch][character_knowledge[ch]]
        for ch in chars
    )


def print_keyboard():
    print(format_row(ROW_1))
    print(' ' + format_row(ROW_2))
    print('  ' + format_row(ROW_3))


def correct_chars(guess):
    return [c1 for c1, c2 in zip(WORD, guess) if c1 == c2]


def in_wrong_place_chars(guess: str):
    return (
            Counter(guess)
            - (Counter(guess) - Counter(WORD))
            - Counter(correct_chars(guess))
    )


def incorrect_chars(guess):
    return set(guess).difference(WORD)


def update_knowledge(guess):
    not_in_word = incorrect_chars(guess)
    in_wrong_place = in_wrong_place_chars(guess)
    correct = correct_chars(guess)
    for char, value in character_knowledge.items():
        if char in not_in_word:
            character_knowledge[char] = 0
        if char in in_wrong_place and value == 1:
            character_knowledge[char] = 2
        if char in correct:
            character_knowledge[char] = 3


def format_guess(guess):
    in_wrong_place_count = in_wrong_place_chars(guess)
    guess = list(guess)
    for i, (c1, c2) in enumerate(zip(WORD, guess)):
        if c1 == c2:
            guess[i] = f'{GREEN}{c2}{OFF}'
        elif in_wrong_place_count[c2] > 0:
            in_wrong_place_count.subtract(c2)
            guess[i] = f'{YELLOW}{c2}{OFF}'
    return ''.join(guess)


def print_text(text):
    print(*textwrap.wrap(text, 19), sep='\n')


def print_game():
    os.system('cls||clear')
    print(f'{" Worble! ":~^19}')
    for attempt in past_guesses:
        print(' ' * 7 + attempt)
    print_keyboard()


def get_guess(guess_num):
    def guess_is_valid(guess: str) -> bool:
        i = bisect.bisect_left(ALL_WORDS, guess)
        return ALL_WORDS[i] == guess

    guess = ''
    while not guess_is_valid(guess):
        guess = input(f'{guess_num}/{NUM_GUESSES} > ').lower()
        if not guess_is_valid(guess):
            print('Not a valid word')
            continue
    return guess


def guess_histogram():
    CUR.execute('SELECT GUESSES FROM Scores')
    data = [val[0] for val in CUR.fetchall()]
    counts = {n: 0 for n in range(1, 7)} | Counter(data)
    max_count = max(counts.values())
    for guess, count in sorted(counts.items()):
        if max_count > 17:
            print(f'{guess}:{"*" * round(count / (max_count / 17))}')
        else:
            print(f'{guess}:{"*" * count}')


def main():
    guess_num = 1
    for guess_num in range(1, NUM_GUESSES + 1):
        print_game()
        guess = get_guess(guess_num)
        update_knowledge(guess)
        past_guesses.append(format_guess(guess))
        if guess == WORD:
            break
        guess_num += 1
    print_game()
    if guess_num <= NUM_GUESSES:
        CUR.execute(f'INSERT INTO Scores(GUESSES) VALUES ({guess_num})')
        print_text(f'Congratulations! Word guessed in {guess_num} guesses')
    else:
        print_text(f'The word was: {WORD}')
        print_text('Better luck next time.')


if __name__ == '__main__':
    db = Path(__file__).parent.resolve() / 'worble.db'
    CON = sqlite3.connect(db)
    CUR = CON.cursor()
    CUR.execute(
        'CREATE TABLE IF NOT EXISTS Scores('
        'ID INTEGER PRIMARY KEY AUTOINCREMENT,'
        'GUESSES INTEGER)'
    )
    try:
        WORD = random.choice(WINNING_WORDS)
        main()
        guess_histogram()
    finally:
        CON.commit()
        CON.close()
