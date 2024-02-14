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
    with open('pg2701.txt', 'rb') as f:
        data = f.read()
    return byte_ranks(data)


def break_single_byte(cbytes: bytearray, eng_ranks: bytearray) -> (int, bytearray):
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


def break_fixed_len_vigenere(cbytes: bytearray, eng_ranks: bytearray, key_len: int) -> (bytearray, bytearray):
    partitions = [bytearray() for _ in range(key_len)]

    for i, b in enumerate(cbytes):
        partitions[i % key_len].append(b)

    broken_partitions = [break_single_byte(b, eng_ranks) for b in partitions]
    key = bytearray([x[0] for x in broken_partitions])
    return key, vigenere(cbytes, key)


def break_vigenere(cbytes: bytearray, eng_ranks: bytearray, max_key_len: int = 20):
    candidate_plaintexts = [break_fixed_len_vigenere(cbytes, eng_ranks, i) for i in range(1, max_key_len)]
    candidate_plaintexts = [(key, ptext, english_score(ptext, eng_ranks)) for key, ptext in candidate_plaintexts]
    for key, ptext, score in candidate_plaintexts:
        print(f'{key}: {score}')
    return min(candidate_plaintexts, key=lambda x: x[2])[0:2]


def main():
    ctext = read_ctext_file(bytearray([0x00, 0x00, 0x00, 0x00]), 'breakme2.bin')
    eng_ranks = gen_english_ranks()
    key, ptext = break_vigenere(ctext, eng_ranks)
    print(key)
    print(ptext.decode('utf-8'))


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
