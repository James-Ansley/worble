import bisect
import os
import random
from collections import Counter
from pathlib import PurePath

DATA_ROOT = PurePath('data')
NUM_GUESSES = 6
GREEN_HIGHLIGHT = '\033[42m'
YELLOW_HIGHLIGHT = '\033[43m'
HIGHLIGHT_OFF = '\033[m'

with open(DATA_ROOT / 'winning_words.txt', 'r') as f:
    winning_words = f.read().splitlines()

with open(DATA_ROOT / 'words.txt', 'r') as f:
    all_words = f.read().splitlines()


def print_keyboard(correct, in_word, not_in_word):
    chars = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd',
             'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm']
    for i, char in enumerate(chars):
        if char in not_in_word:
            chars[i] = '_'
        elif char in in_word:
            chars[i] = f'{YELLOW_HIGHLIGHT}{char}{HIGHLIGHT_OFF}'
        elif char in correct:
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


def main():
    word = random.choice(winning_words)
    guess_num = 1
    not_in_word = set()
    past_guesses = []
    clear()
    while guess_num <= NUM_GUESSES:
        guess = get_guess(guess_num)
        past_guesses.append(format_guess(word, guess))
        not_in_word |= incorrect_chars(word, guess)
        print_game(word, guess, past_guesses, not_in_word)
        if guess == word:
            print(f'Congratulations! Word guessed in {guess_num} guesses')
            return
        guess_num += 1
    print(f'The word was: {word}\nBetter luck next time.')


if __name__ == '__main__':
    main()
