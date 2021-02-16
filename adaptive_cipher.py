import os
import string
import random
from tqdm import trange

# unicode from 33 to 126
part1 = string.ascii_uppercase
part2 = string.ascii_lowercase
part3 = string.punctuation
part4 = string.digits
alphabet = part1 + part2 + part3 + part4


# noinspection PyBroadException
def main():
    while True:
        message_input = input("Enter message or filename: ")
        if ''.join(message_input[-4:]) == '.txt':
            try:
                f = open('Data/' + message_input, 'r')
                message_input = f.read()
                f.close()
            except:
                error_a()
                continue
        message = formatting(message_input)
        if len(message) < 2:
            error_b("message")
            continue
        all_characters = formatting_with_spaces(message_input)
        save_spaces = ''
        if ' ' in all_characters:
            save_spaces = input("Save spaces (y/n): ")
            if save_spaces != 'y' and save_spaces != 'n':
                error_a()
                continue
        keyword_input = input("Enter keyword or filename or nothing to generate keyword: ")
        if ''.join(keyword_input[-4:]) == '.txt':
            try:
                f = open(keyword_input, 'r')
                keyword_input = f.read()
                f.close()
            except:
                error_a()
                continue
        elif len(keyword_input) == 0:
            keyword_input = generate_keyword(len(message))
        keyword = formatting(keyword_input)
        if len(keyword) < 2:
            error_b("keyword")
            continue
        keyword = expand_keyword(keyword, message)
        try:
            repetitions = int(input("Number of repetitions: "))
        except:
            error_a()
            continue
        if repetitions <= 0:
            print("ERROR: number of repetitions must be greater than zero")
            repeat()
            continue
        mode = input("Encrypt or decrypt (e/d): ")
        if mode == 'e':
            result = message
            print("")
            for _ in trange(repetitions):
                result = AdaptiveCipher(keyword).encrypt(result)
            a, b = "Plaintext", "Ciphertext"
        elif mode == 'd':
            result = message
            print("")
            for _ in trange(repetitions):
                result = AdaptiveCipher(keyword).decrypt(result)
            a, b = "Ciphertext", "Plaintext"
        else:
            error_a()
            continue
        if ' ' in all_characters and save_spaces == 'y':
            message_output = all_characters
            result_output = insert_spaces(list(all_characters), list(result))
        else:
            message_output = message
            result_output = result
        keyword_strength = round(len(keyword) / len(message) * 100, 1)
        if keyword_strength >= 100:
            keyword_strength = 100
        print(f"\n{a}: {message_output}")
        print(f"{len(message)} characters")
        print(f"Distribution: {frequency_analysis(message)}%")
        print(f"\nKeyword: {keyword}")
        print(f"{len(keyword)} characters")
        print(f"Distribution: {frequency_analysis(keyword)}%")
        print(f"Strength: {keyword_strength}%")
        print(f"\n{b}: {result_output}")
        print(f"{len(result)} characters")
        print(f"Distribution: {frequency_analysis(result)}%")
        filename = f"{b.lower() + '_x' + str(repetitions) + '.txt'}"
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


class AdaptiveCipher:
    def __init__(self, keyword):
        self.keyword = keyword
        self.alphabet = alphabet

    def encrypt(self, message):
        frequency = round(frequency_analysis(self.keyword))
        result = ''
        for i in range(len(message)):
            x = i % len(self.keyword)
            value = ord(message[i]) + ord(self.keyword[x]) - 33
            if value >= 127:
                value -= len(self.alphabet)
            result += chr(value)
            index = self.alphabet.index(self.keyword[i])
            self.alphabet = shift_alphabet(self.alphabet, self.keyword, frequency, index, i)
        return result

    def decrypt(self, message):
        frequency = round(frequency_analysis(self.keyword))
        result = ''
        for i in range(len(message)):
            x = i % len(self.keyword)
            value = ord(message[i]) - ord(self.keyword[x]) + 33
            if value < 32:
                value += len(self.alphabet)
            result += chr(value)
            index = self.alphabet.index(self.keyword[i])
            self.alphabet = shift_alphabet(self.alphabet, self.keyword, frequency, index, i)
        return result


def shift_alphabet(alpha, key, key_freq, index, arg):
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
    text = text.translate(table)
    return text


# noinspection PyTypeChecker
def rail_fence_cipher(text, n):
    fence = [[None] * len(text) for n in range(n)]
    rails = list(range(n - 1)) + list(range(n - 1, 0, -1))
    for n, x in enumerate(text):
        fence[rails[n % len(rails)]][n] = x
    return ''.join([c for rail in fence for c in rail if c is not None])


def frequency_analysis(keyword):
    if len(keyword) == 0:
        frequency = 1
    elif len(keyword) <= len(alphabet):
        value = [(1 / keyword.count(i) * 100) for i in alphabet if keyword.count(i) != 0]
        frequency = round(sum(value) / len(keyword), 1)
    else:
        value = [keyword.count(i) * 100 / len(keyword) for i in alphabet]
        ideal = 100 / len(alphabet)
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
                letter = alphabet[random.randint(0, len(alphabet) - 1)]
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
    message = [i for i in text if i in alphabet]
    return ''.join(message)


def formatting_with_spaces(text):
    message = [i for i in text if i in alphabet or i == ' ']
    return ''.join(message)


def insert_spaces(all_characters, result):
    for i in range(len(all_characters)):
        if all_characters[i] == ' ':
            result.insert(i, ' ')
    return ''.join(result)


def error_a():
    print("ERROR: incorrect input")
    repeat()


def error_b(text):
    print(f"ERROR: {text} must contain at least two letters")
    repeat()


def repeat():
    input("\nPress Enter to repeat\n")
    os.system('cls||clear')


if __name__ == '__main__':
    main()
