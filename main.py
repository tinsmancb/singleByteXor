from itertools import cycle
from typing import Dict

def singleByteXor(text: bytearray, b: int) -> bytearray:
    out = bytearray()

    for i in text:
        out.append(i ^ b)

    return out


def vigenere(text: bytearray, key: bytearray) -> bytearray:
    out = bytearray()

    for i, j in zip(text, cycle(key)):
        out.append(i ^ j)

    return out


def write_ctext_file(ptext: str, key: bytearray, fname: str) -> None:
    pbytes = bytearray(ptext, 'utf-8')
    cbytes = vigenere(pbytes, key)

    with open(fname, 'wb') as f:
        f.write(cbytes)


def read_ctext_file(key: bytearray, fname: str) -> str:
    with open(fname, 'rb') as f:
        cbytes = bytearray(f.read())
        ptext = vigenere(cbytes, key)
        return ptext


def byte_counts(data: bytearray) -> Dict[int, int]:
    out = {}
    for b in data:
        if b in out:
            out[b] += 1
        else:
            out[b] = 1
    return out


def byte_ranks(data):
    counts = dict(sorted(byte_counts(data).items()))
    counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
    return bytearray([k for k, v in counts.items()])


def score(test, english, penalty=100):
    acc = 0
    for b in test:
        try:
            acc += english.index(b)
        except ValueError:
            acc += penalty
    return acc


def gen_english_ranks(infile='pg2701.txt'):
    with open('pg2701.txt', 'rb') as f:
        data = f.read()
    counts = dict(sorted(byte_counts(data).items()))
    counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
    return bytearray([k for k, v in counts.items()])


def break_single_byte(cbytes, eng_ranks):
    true_key = 0b00000000
    true_ptext = cbytes
    pranks = byte_ranks(true_ptext)
    pscore = score(pranks, eng_ranks)

    for key in range(256):
        ptext = vigenere(cbytes, [key])
        pranks = byte_ranks(ptext)
        if score(pranks, eng_ranks) < pscore:
            pscore = score(pranks, eng_ranks)
            true_key = key
            true_ptext = ptext

    return true_key, true_ptext


def main():
    cbytes = read_ctext_file([0b00000000], 'breakme.bin')
    eng_ranks = gen_english_ranks()
    key, message = break_single_byte(cbytes, eng_ranks)
    print(message.decode('utf-8'))

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
