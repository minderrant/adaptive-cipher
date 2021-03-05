import os
import sys
import time
import string
import random

ALPHABET = string.ascii_uppercase


def main():
    while True:
        message_input = input("Enter message or filename: ")
        if ''.join(message_input[-4:]) == '.txt':
            try:
                f = open('Data/' + message_input, 'r')
                message_input = f.read()
                f.close()
            except OSError:
                print(f"\nError: Data/{message_input} was not found")
                repeat()
                continue
        message = formatting(message_input)
        if len(message) < 2:
            print("\nError: message must contain at least two letters")
            repeat()
            continue
        all_characters = formatting_with_spaces(message_input)
        if ' ' in all_characters:
            save_spaces = input("Save spaces (y/n): ")
            if save_spaces != 'y' and save_spaces != 'n':
                print("\nError: invalid input")
                repeat()
                continue
        keyword_input = input("Enter keyword or filename or nothing to generate keyword: ")
        if ''.join(keyword_input[-4:]) == '.txt':
            try:
                f = open('Data/' + keyword_input, 'r')
                short_keyword = f.read()
                f.close()
            except OSError:
                print(f"\nError: Data/{keyword_input} was not found")
                repeat()
                continue
        elif len(keyword_input) == 0:
            short_keyword = generate_keyword(len(message))
        else:
            short_keyword = formatting(keyword_input)
        if len(short_keyword) < 2:
            print("\nError: keyword must contain at least two letters")
            repeat()
            continue
        keyword = expand_keyword(short_keyword, message)
        repetitions = float(input("Number of repetitions: "))
        if repetitions <= 0:
            print("\nError: number of repetitions must be greater than zero")
            repeat()
            continue
        mode = input("Encrypt or decrypt (e/d): ")
        if mode == 'e':
            a, b = "Plaintext", "Ciphertext"
            result = message
            print("")
            start_time = time.time()
            for _ in range(round(repetitions)):
                result = Adaptive(keyword).encrypt(result)
            elapsed_time(time.time() - start_time)
        elif mode == 'd':
            a, b = "Ciphertext", "Plaintext"
            result = message
            print("")
            start_time = time.time()
            for _ in range(round(repetitions)):
                result = Adaptive(keyword).decrypt(result)
            elapsed_time(time.time() - start_time)
        else:
            print("\nError: invalid input")
            repeat()
            continue
        if ' ' in all_characters and save_spaces == 'y':
            message_output = all_characters
            result_output = insert_spaces(list(all_characters), list(result))
        else:
            message_output = message
            result_output = result
        keyword_strength = round(len(short_keyword) / len(message) * 100, 1)
        if keyword_strength >= 100:
            keyword_strength = 100
        print(f"\n{a}: {message_output}")
        print(f"Characters: {len(message)}")
        print(f"Distribution: {frequency_analysis(message)}%")
        print(f"\nKeyword: {short_keyword}")
        print(f"Characters: {len(short_keyword)}")
        print(f"Distribution: {frequency_analysis(short_keyword)}%")
        print(f"Strength: {keyword_strength}%")
        print(f"\n{b}: {result_output}")
        print(f"Characters: {len(result)}")
        print(f"Distribution: {frequency_analysis(result)}%")
        filename = f"{b.lower() + '_x' + str(round(repetitions)) + '.txt'}"
        if os.path.exists('Data'):
            pass
        else:
            os.mkdir('Data')
        f = open('Data/' + filename, 'w')
        f.write(result_output)
        f.close()
        print(f"\n{b} saved in Data/{filename}")
        if len(keyword_input) == 0:
            f = open('Data/keyword.txt', 'w')
            f.write(keyword)
            f.close()
            print("Keyword saved in Data/keyword.txt")
        repeat()
        continue


class Adaptive:
    def __init__(self, keyword):
        self.keyword = keyword
        self.alphabet = ALPHABET

    def encrypt(self, message):
        frequency = round(frequency_analysis(self.keyword))
        result = ''
        for i in progress_bar(range(len(message)), "Encryption: ", 50):
            x = i % len(self.keyword)
            value = ord(message[i]) + ord(self.keyword[x]) - 65
            if value >= 91:
                value -= len(self.alphabet)
            result += chr(value)
            index = self.alphabet.index(self.keyword[i])
            self.alphabet = Adaptive.shift(self.alphabet, self.keyword, frequency, index, i)
        return result

    def decrypt(self, message):
        frequency = round(frequency_analysis(self.keyword))
        result = ''
        for i in progress_bar(range(len(message)), "Decryption: ", 50):
            x = i % len(self.keyword)
            value = ord(message[i]) - ord(self.keyword[x]) + 65
            if value < 64:
                value += len(self.alphabet)
            result += chr(value)
            index = self.alphabet.index(self.keyword[i])
            self.alphabet = Adaptive.shift(self.alphabet, self.keyword, frequency, index, i)
        return result

    @staticmethod
    def shift(alpha, key, key_freq, index, arg):
        if index % 2 == 0:
            shift = round(index * (key_freq + arg) % len(key))
        else:
            shift = round(index * (len(key) + arg) % len(key))
        alpha = caesar_cipher(alpha, shift)
        if shift > 1:
            alpha = rail_fence_cipher(alpha, shift)
        if arg % 2 == 1:
            pair = str.maketrans(key[arg - 1] + key[arg], key[arg] + key[arg - 1])
            alpha = alpha.translate(pair)
        return alpha


def caesar_cipher(text, shift):
    shifted = text[shift:] + text[:shift]
    table = str.maketrans(text, shifted)
    result = text.translate(table)
    return result


def rail_fence_cipher(text, n):
    fence = [[None] * len(text) for n in range(n)]
    rails = list(range(n - 1)) + list(range(n - 1, 0, -1))
    for n, x in enumerate(text):
        fence[rails[n % len(rails)]][n] = x
    result = ''.join([c for rail in fence for c in rail if c is not None])
    return result


def frequency_analysis(keyword):
    if len(keyword) == 0:
        frequency = 1
    elif len(keyword) <= len(ALPHABET):
        value = [(1 / keyword.count(i) * 100) for i in ALPHABET if keyword.count(i) != 0]
        frequency = round(sum(value) / len(keyword), 1)
    else:
        value = [keyword.count(i) * 100 / len(keyword) for i in ALPHABET]
        ideal = 100 / len(ALPHABET)
        result = []
        for i in value:
            if i < ideal:
                result.append(i / ideal * 100)
            elif i > ideal:
                result.append(ideal / i * 100)
            elif i == ideal:
                result.append(100)
        frequency = round(sum(result) / len(result), 1)
    if frequency == 0:
        frequency = 1
    elif frequency == 100:
        frequency = 100
    return frequency


def expand_keyword(keyword, message):
    exp_keyword = ''
    while len(exp_keyword) <= len(message):
        exp_keyword += keyword
    return exp_keyword[:len(message)]


def generate_keyword(length):
    while True:
        keyword = []
        for i in range(length):
            while True:
                letter = ALPHABET[random.randint(0, len(ALPHABET) - 1)]
                if i > 0:
                    if letter != keyword[i - 1]:
                        keyword.append(letter)
                        break
                    else:
                        continue
                else:
                    keyword.append(letter)
                    break
        if frequency_analysis(keyword) < 50:
            continue
        else:
            break
    return ''.join(keyword)


def formatting(text):
    message = [i for i in text.upper() if i in ALPHABET]
    return ''.join(message)


def formatting_with_spaces(text):
    message = [i for i in text.upper() if i in ALPHABET or i == ' ']
    return ''.join(message)


def insert_spaces(all_characters, result):
    for i in range(len(all_characters)):
        if all_characters[i] == ' ':
            result.insert(i, ' ')
    return ''.join(result)


def progress_bar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)

    def show(j):
        x = int(size * j / count)
        file.write("%s|%s%s| %i/%i\r" % (prefix, "█" * x, " " * (size - x), j, count))
        file.flush()

    show(0)
    for i, item in enumerate(it):
        yield item
        show(i + 1)
    file.write("\n")
    file.flush()


def elapsed_time(gap):
    min = gap // 60
    if min >= 1:
        hour = min // 60
        if hour >= 1:
            print(f"Elapsed time: {round(hour)} hours, ", end='')
            print(f"{round(min % 60), 2} minutes, {round(gap % 60), 2} seconds")
        else:
            print(f"Elapsed time: {round(min)} minutes, ", end='')
            print(f"{round(gap % 60), 2} seconds")
    else:
        print(f"Elapsed time: {round(gap, 2)} seconds")


def repeat():
    input("\nPress Enter to repeat")
    os.system('cls||clear')


if __name__ == '__main__':
    main()
