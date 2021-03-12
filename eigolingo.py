import re
from collections import Counter
from sys import argv


def _create_dict(textlines):
    rdict = dict()
    for line in textlines:
        key, value = line.split(":")
        rdict[key] = value
    return rdict


def read_dict(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return _create_dict(f.read().splitlines())


def clean_text(text, contdict=None):
    remstr = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~’–—„“”…‘’"
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
    wdict = read_dict(f"dict{dictsize}.txt")
    contdict = read_dict("contraction_dict.txt")

    text = read_and_clean(filename, contdict)
    clist95 = list()
    notinwlist = list()
    for w in text.split():
        if not w.isalpha():
            continue
        if w in wdict:
            clist95.append(wdict[w])
        else:
            notinwlist.append(w)
    wc95 = Counter(clist95)
    print(len(wc95))
    print(len(set(notinwlist)))
    print(sum(wc95.values()))
    print(f"{100*sum(wc95.values())/text.count(' '):.2f}%")
