from itertools import cycle


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

def main():
    ptext = 'A Turing machine is a mathematical model of computation describing an abstract machine that manipulates symbols on a strip of tape according to a table of rules. Despite the model\'s simplicity, it is capable of implementing any computer algorithm.'
    pbytes = bytearray(ptext, 'utf-8')
    key = bytearray('GRAYSON', 'utf-8')

    ctext = vigenere(pbytes, key)
    print(ctext.hex())

    write_ctext_file(ptext, key, 'ctext.bin')
    print(read_ctext_file(key, 'ctext.bin').decode('utf-8'))


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
