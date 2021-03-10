import re
from collections import Counter
from sys import argv


def read_dict(textlines):
    rdict = dict()
    for line in textlines:
        key, value = line.split(":")
        rdict[key] = value
    return rdict


def pattern_create(replacements):
    rep_sorted = sorted(replacements, key=len, reverse=True)
    rep_escaped = list(map(re.escape, rep_sorted))
    return re.compile("|".join(rep_escaped))


def pattern_replacement(text, pattern, replacements):
    return pattern.sub(lambda match: replacements[match.group(0).strip()], text)


filename = argv[1]
if len(argv) > 2:
    dictsize = int(argv[2])

with open(filename, "r", encoding="utf-8") as f:
    text = f.read().lower()
with open("contraction_dict.txt", "r", encoding="utf-8") as f:
    contdict = read_dict(f.read().splitlines())
contpat = pattern_create(contdict)

remstr = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~’–—„“”…‘’"
punctu = str.maketrans(remstr, " " * len(remstr))
text = pattern_replacement(text, contpat, contdict)
text = re.sub(r"(\w)('s|’s|’|')", r"\1", text)
text = text.translate(punctu)
text = re.sub(r"\s+", " ", text)

with open("dict95.txt", "r", encoding="utf-8") as f:
    infdict = read_dict(f.read().splitlines())


clist95 = list()
notinwlist = list()
textsp = text.split()
for w in textsp:
    if any(char.isdigit() for char in w):
        continue
    if not w:
        continue
    #     if w == "israe":
    #         print(text.split().index(w))
    if w in infdict:
        clist95.append(infdict[w])
    else:
        notinwlist.append(w)
wc95 = Counter(clist95)
print(len(wc95))
print(len(set(notinwlist)))
