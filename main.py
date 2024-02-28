from itertools import cycle
from typing import Dict, Tuple
import matplotlib.pyplot as plt


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


def read_ctext_file(key: bytearray, fname: str) -> bytearray:
    with open(fname, 'rb') as f:
        cbytes = bytearray(f.read())
        ptext = vigenere(cbytes, key)
        return ptext


def byte_counts(data: bytearray) -> Dict[int, int]:
    out = {b: 0 for b in data}  # Initialize a count of zero for each byte that appears in the data.
    for b in data:
        out[b] += 1  # Count how many times each byte appears.
    return out


def byte_ranks(data: bytearray) -> bytearray:
    counts = sorted(byte_counts(data).items(),  # Convert dictionary to a list of tuples
                    key=lambda item: item[1],  # Sort on the second item in the tuple (the count)
                    reverse=True  # Reverse order (more common bytes first)
                    )
    return bytearray([k[0] for k in counts])  # Throw away the counts, return bytes as a bytearray


def english_score(test: bytearray, english: bytearray, penalty=1000) -> int:
    return sum([english.index(b) if b in english  # The score of a byte is its position in the english ranks
                else penalty  # If a character does not appear in english then assign a high score
                for b in test])  # Add up the scores from each individual byte in test


def gen_english_ranks(infile='pg2701.txt') -> bytearray:
    with open(infile, 'rb') as f:
        data = f.read()
    return byte_ranks(bytearray(data))


def break_single_byte(cbytes: bytearray, eng_ranks: bytearray) -> Tuple[int, bytearray]:
    best_key = 0b00000000
    best_ptext = cbytes
    p_ranks = byte_ranks(cbytes)
    best_score = english_score(p_ranks, eng_ranks)

    for key in range(256):
        ptext = vigenere(cbytes, bytearray([key]))
        p_ranks = byte_ranks(ptext)
        p_score = english_score(p_ranks, eng_ranks)
        if p_score < best_score:
            best_score = p_score
            best_key = key
            best_ptext = ptext

    return best_key, best_ptext


def break_fixed_len_vigenere(cbytes: bytearray, eng_ranks: bytearray, key_len: int) -> Tuple[bytearray, bytearray]:
    partitions = [bytearray() for _ in range(key_len)]

    for i, b in enumerate(cbytes):
        partitions[i % key_len].append(b)

    broken_partitions = [break_single_byte(b, eng_ranks) for b in partitions]
    key = bytearray([x[0] for x in broken_partitions])
    return key, vigenere(cbytes, key)


def key_length_score_english(cbytes: bytearray, eng_ranks: bytearray, key_len: int) -> int:
    key, pbytes = break_fixed_len_vigenere(cbytes, eng_ranks, key_len)
    return english_score(pbytes, eng_ranks)


def key_length_score(cbytes: bytearray, key_len: int) -> float:
    if key_len > len(cbytes)//2:
        raise ValueError(f'Key length {key_len} is longer than half the message size {len(cbytes)}')
    if key_len < 1:
        raise ValueError(f'Key length {key_len} must be at least 1.')
    first_n_bits = cbytes[:key_len]  # The first N bytes of the message
    second_n_bits = cbytes[key_len:2*key_len]  # The second N bytes of the message
    return sum(  # Add up for each pair of bytes
        [(f ^ s).bit_count()  # Use XOR to detect differing bits, then use bit_count to find how many bits differ.
         for f, s in zip(first_n_bits, second_n_bits)])/key_len  # Normalize by dividing by key length.


def break_vigenere(cbytes: bytearray, eng_ranks: bytearray, max_key_len: int = 60) \
        -> Tuple[bytearray, bytearray]:
    min_score = float('inf')
    min_key_len = 1
    for key_len in range(1, min(len(cbytes)//2, max_key_len+1)):
        score = key_length_score(cbytes, key_len)
        if score < min_score:
            min_score = score
            min_key_len = key_len

    return break_fixed_len_vigenere(cbytes, eng_ranks, min_key_len)


def main():
    ctext = read_ctext_file(bytearray([0x00, 0x00, 0x00, 0x00]), 'breakme2.bin')
    eng_ranks = gen_english_ranks()
    key, ptext = break_vigenere(ctext, eng_ranks)
    print(key)
    print(ptext.decode('utf-8'))


def plot_key_length_scores(true_key_len=None, max_key_len=None):
    ctext = read_ctext_file(bytearray([0x00, 0x00, 0x00, 0x00]), 'breakme2.bin')
    eng_ranks = gen_english_ranks()
    if max_key_len is None:
        max_key_len = len(ctext)//2
    scores_english = [key_length_score_english(ctext, eng_ranks, i) for i in range(1, max_key_len)]
    scores_popcount = [key_length_score(ctext, i) for i in range(1, max_key_len)]
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
    ax1.plot(scores_popcount, 'o')
    if true_key_len is not None:
        ax1.hlines(scores_popcount[true_key_len-1], 1, max_key_len, colors='C1', linestyles='dashed')
    ax2.plot(scores_english, 'o')
    if true_key_len is not None:
        ax2.hlines(scores_english[true_key_len-1], 1, max_key_len, colors='C1', linestyles='dashed')
    fig.show()


if __name__ == '__main__':
    plot_key_length_scores(true_key_len=4, max_key_len=60)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
