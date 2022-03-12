import bisect
import os
import random
import string
from collections import Counter
from math import log10, floor
from pathlib import Path

import sqlite3

DATA_ROOT = Path(__file__).parent.resolve() / 'data'
NUM_GUESSES = 6
GREEN_HIGHLIGHT = '\033[42m'
YELLOW_HIGHLIGHT = '\033[43m'
HIGHLIGHT_OFF = '\033[m'

with open(DATA_ROOT / 'winning_words.txt', 'r') as f:
    winning_words = f.read().splitlines()

with open(DATA_ROOT / 'words.txt', 'r') as f:
    all_words = f.read().splitlines()

keyboard = {ch: 0 for ch in string.ascii_lowercase}


def print_keyboard(correct, in_word, not_in_word):
    global keyboard
    keyboard |= {ch: -1 for ch in not_in_word}
    keyboard |= {ch: 1 for ch in in_word if keyboard[ch] != 2}
    keyboard |= {ch: 2 for ch in correct}
    chars = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd',
             'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm']
    for i, char in enumerate(chars):
        if keyboard[char] == -1:
            chars[i] = '_'
        elif keyboard[char] == 1:
            chars[i] = f'{YELLOW_HIGHLIGHT}{char}{HIGHLIGHT_OFF}'
        elif keyboard[char] == 2:
            chars[i] = f'{GREEN_HIGHLIGHT}{char}{HIGHLIGHT_OFF}'
    print(' '.join(chars[:10]))
    print(' ' + ' '.join(chars[10:19]))
    print('  ' + ' '.join(chars[19:]))


def correct_chars(word, guess):
    return [c1 for c1, c2 in zip(word, guess) if c1 == c2]


def in_word_chars(word: str, guess: str):
    return (
            Counter(guess)
            - (Counter(guess) - Counter(word))
            - Counter(correct_chars(word, guess))
    )


def incorrect_chars(word, guess):
    return set(guess).difference(word)


def format_guess(word, guess):
    correct_chars_ = in_word_chars(word, guess)
    guess = list(guess)
    for i, (c1, c2) in enumerate(zip(word, guess)):
        if c1 == c2:
            guess[i] = f'{GREEN_HIGHLIGHT}{c2}{HIGHLIGHT_OFF}'
        elif correct_chars_[c2] > 0:
            correct_chars_.subtract(c2)
            guess[i] = f'{YELLOW_HIGHLIGHT}{c2}{HIGHLIGHT_OFF}'
    return ''.join(guess)


def guess_is_valid(guess: str) -> bool:
    i = bisect.bisect_left(all_words, guess)
    return all_words[i] == guess and len(guess) == 5


def clear():
    os.system('cls||clear')
    print(f'{" Worble! ":~^19}')


def print_game(word, guess, past_guesses, not_in_word):
    clear()
    for attempt in past_guesses:
        print(' ' * 7 + attempt)
    print_keyboard(
        correct_chars(word, guess),
        in_word_chars(word, guess),
        not_in_word,
    )


def get_guess(guess_num):
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
    word = random.choice(winning_words)
    guess_num = 1
    past_guesses = []
    clear()
    while guess_num <= NUM_GUESSES:
        guess = get_guess(guess_num)
        past_guesses.append(format_guess(word, guess))
        print_game(word, guess, past_guesses, incorrect_chars(word, guess))
        if guess == word:
            break
        guess_num += 1
    if guess_num <= NUM_GUESSES:
        CUR.execute(f'INSERT INTO Scores(GUESSES) VALUES ({guess_num})')
        print(f'Congratulations! Word guessed in {guess_num} guesses')
    else:
        print(f'The word was: {word}\nBetter luck next time.')
    guess_histogram()


if __name__ == '__main__':
    CON = sqlite3.connect('worble.db')
    CUR = CON.cursor()
    CUR.execute('CREATE TABLE IF NOT EXISTS Scores('
                'ID INTEGER PRIMARY KEY AUTOINCREMENT,'
                'GUESSES INTEGER'
                ')')
    try:
        main()
    finally:
        CON.commit()
        CON.close()
