from importlib_metadata import version

__version__ = version(__package__)


import re
from collections import Counter
from sys import argv, path
from math import log
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import importlib.resources as pkg_resources
import pandas as pd
import numpy as np
from . import wdicts


def _create_dict(textlines):
    rdict = dict()
    for line in textlines:
        key, value = line.split(":")
        rdict[key] = value
    return rdict


def _get_dictpath():
    with pkg_resources.path(wdicts, "dict70.txt") as p:
        return p.parent


def _entropy(counter, base=2):
    arr = np.fromiter(counter.values(), float)
    tot = np.sum(arr)
    arr = arr / tot
    arr = arr * np.log(arr) / np.log(base)
    return -np.sum(arr)


def read_dict(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return _create_dict(f.read().splitlines())


def read_wdict(dictsize):
    dictpath = _get_dictpath()
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


def clean_textMT(args):
    text, contdict = args
    return clean_text(text.lower(), contdict=contdict)


def read_and_cleanMT(args):
    file, contdict = args
    with open(file, "r", encoding="utf-8") as f:
        text = f.read().lower()
    return clean_text(text, contdict=contdict)


def read_and_clean(filename, contdict=None):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read().lower()
    return clean_text(text, contdict=contdict)


def main():
    if len(argv) > 1:
        filename = argv[1]
    else:
        raise SyntaxError("Specify valid filename")
    if len(argv) > 2:
        dictsize = int(argv[2])
    else:
        dictsize = 70
    wdict = read_wdict(dictsize)
    contdict = read_dict(f"{wdir}/contraction_dict.txt")

    text = read_and_clean(filename, contdict)
    wc95 = Counter()
    unkcount = Counter()
    number_counter = 0
    for w in text.split():
        if not w.isalpha():
            number_counter += 1
            continue
        if w in wdict:
            wc95.update([wdict[w]])
        else:
            unkcount.update([w])
    print("unique tokens: ".ljust(20), len(wc95))
    print(
        "tokens counted: ".ljust(20),
        f"{100*sum(wc95.values())/(text.count(' ')-number_counter):.2f}%",
    )
    print("total tokens: ".ljust(20), text.count(" ") - number_counter)


class Eigo:
    """docstring for Eigo"""

    def __init__(self):
        self.df = pd.DataFrame()
        self.dictpath = _get_dictpath()
        self.contdict = read_dict(self.dictpath / "contraction_dict.txt")
        self.w70 = read_wdict(70)
        self.w80 = self.w70.copy()
        self.w80.update(read_dict(self.dictpath / "dict80.txt"))
        self.w95 = self.w80.copy()
        self.w95.update(read_dict(self.dictpath / "dict95.txt"))
        print(len(self.w95))
        self.total_counter = Counter()
        print(len(self.total_counter))

    def feed_text(self, name, text, cleaned=False):
        wdict = self.w70
        if not cleaned:
            text = clean_text(text.lower(), self.contdict)
        wcount = Counter()
        unkcount = Counter()
        number_counter = 0
        for w in text.split():
            if not w.isalpha():
                number_counter += 1
                continue
            if w in wdict:
                wcount.update([wdict[w]])
            else:
                unkcount.update([w])
        add_data = [
            {
                "Name": name,
                "TotalTokens": text.count(" ") - number_counter,
                "UniqueTokens70": len(wcount),
                "TokensCounted70": 100
                * sum(wcount.values())
                / (text.count(" ") - number_counter),
                "Entropy70": _entropy(wcount),
            }
        ]
        for k, v in unkcount.items():
            if k in self.w80:
                wcount[k] = v
        add80 = {
            "UniqueTokens80": len(wcount),
            "TokensCounted80": 100
            * sum(wcount.values())
            / (text.count(" ") - number_counter),
            "Entropy80": _entropy(wcount),
        }
        for k, v in unkcount.items():
            if k in self.w95:
                wcount[k] = v
        add95 = {
            "UniqueTokens95": len(wcount),
            "TokensCounted95": 100
            * sum(wcount.values())
            / (text.count(" ") - number_counter),
            "Entropy95": _entropy(wcount),
        }
        add_data[0].update(add80)
        add_data[0].update(add95)
        self.df = self.df.append(add_data, ignore_index=True, sort=False)
        self.total_counter.update(wcount)

    def feed_filelist(self, filelist, threads=6):
        args = ((book, self.contdict) for book in filelist)
        with ProcessPoolExecutor(max_workers=threads) as executor:
            for arg, res in tqdm(zip(filelist, executor.map(read_and_cleanMT, args))):
                self.feed_text(arg.stem, res, cleaned=True)

    def feed_text_list(self, textlist, namelist, threads=6):
        if len(textlist) != len(namelist):
            raise ValueError("lengths of textlist and namelist differ")
        args = ((book, self.contdict) for book in textlist)
        with ProcessPoolExecutor(max_workers=threads) as executor:
            for arg, res in tqdm(zip(namelist, executor.map(clean_textMT, args))):
                self.feed_text(arg, res, cleaned=True)
