import re
from collections import Counter
from sys import argv, path


def _create_dict(textlines):
    rdict = dict()
    for line in textlines:
        key, value = line.split(":")
        rdict[key] = value
    return rdict


def read_dict(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return _create_dict(f.read().splitlines())


def read_wdict(dictpath, dictsize):
    if dictsize not in [70, 80, 95]:
        raise ValueError("Specify an available dictsize [70, 80, 95]")
    wdict = read_dict(f"{dictpath}/dict70.txt")
    if dictsize == 70:
        return wdict
    wdict.update(read_dict(f"{dictpath}/dict80.txt"))
    if dictsize == 80:
        return wdict
    wdict.update(read_dict(f"{dictpath}/dict95.txt"))
    return wdict


def clean_text(text, contdict=None):
    remstr = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~’–—„“”…‘’\x93\x94‡†‴»∥§\x92\x91·"
    punctu = str.maketrans(remstr, " " * len(remstr))
    if contdict:
        for key in sorted(list(contdict.keys()), key=len, reverse=True):
            text = text.replace(key, contdict[key])
    text = re.sub(r"(\w)('s|’s|’|')", r"\1", text)
    text = text.translate(punctu)
    text = re.sub(r"\s+", " ", text)
    return text


def read_and_clean(filename, contdict=None):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read().lower()
    return clean_text(text, contdict=contdict)


if __name__ == "__main__":
    if len(argv) > 1:
        filename = argv[1]
    else:
        filename = "1984.txt"
        dictsize = 70
    if len(argv) > 2:
        dictsize = int(argv[2])
    else:
        dictsize = 70
    wdir = path[0]
    wdict = read_wdict(wdir, dictsize)
    contdict = read_dict(f"{wdir}/contraction_dict.txt")

    text = read_and_clean(filename, contdict)
    clist95 = list()
    notinwlist = list()
    number_counter = 0
    for w in text.split():
        if not w.isalpha():
            number_counter += 1
            continue
        if w in wdict:
            clist95.append(wdict[w])
        else:
            notinwlist.append(w)
    wc95 = Counter(clist95)
    unkcount = Counter(notinwlist)
    print("unique tokens: ".ljust(20), len(wc95))
    print(
        "tokens counted: ".ljust(20),
        f"{100*sum(wc95.values())/(text.count(' ')-number_counter):.2f}%",
    )
    print("total tokens: ".ljust(20), text.count(" ") - number_counter)
