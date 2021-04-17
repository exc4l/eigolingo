from importlib.metadata import version

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
    return -np.sum(arr * np.log(arr) / np.log(base))


def _crossentropy(counter, true_counter, base=2, eps=1e-15):
    """true_counter is expected to contain propabilities - not counts"""
    # inbetween = list(
    #     (true_counter[k], counter.get(k, eps)) for k in true_counter.keys()
    # )
    inbetween = list(
            (v, counter.get(k, eps)) for k, v in true_counter.items()
    )
    vals = np.array(inbetween)
    p, q = np.hsplit(vals, 2)
    tot = np.sum(q)
    return -np.sum(p * np.log(q / tot) / np.log(base))


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


def read_total_counter():
    dictpath = _get_dictpath()
    with open(f"{dictpath}/total_counter.txt", "r", encoding="utf-8") as f:
        data = f.read().splitlines()
    rdict = dict()
    for line in data:
        key, value = line.split(":")
        rdict[key] = int(value)
    return rdict


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
    if len(argv) > 3:
        if "cross" in argv[3]:
            CALC_CROSS = True
    else:
        CALC_CROSS = False
    wdict = read_wdict(dictsize)
    contdict = read_dict(f"{_get_dictpath()}/contraction_dict.txt")

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
    print("entropy: ".ljust(20), _entropy(wc95))
    if CALC_CROSS:
        true_probs = Counter(read_total_counter())
        temptotal = sum(true_probs.values())
        for key in true_probs.keys():
            true_probs[key] /= temptotal
        print("cross-entropy: ".ljust(20), _crossentropy(wc95, true_probs))


class Eigo:
    """docstring for Eigo"""

    def __init__(self):
        self.df = pd.DataFrame()
        self.dictpath = _get_dictpath()
        self.contdict = read_dict(self.dictpath / "contraction_dict.txt")
        self.cross95 = False
        self.w70 = read_wdict(70)
        self.w80 = self.w70.copy()
        self.w80.update(read_dict(self.dictpath / "dict80.txt"))
        self.w95 = self.w80.copy()
        self.w95.update(read_dict(self.dictpath / "dict95.txt"))
        print("w95 dictsize: ",len(self.w95))
        self.total_counter = Counter()
        self.total_uknown = Counter()
        self.true_counts = Counter(read_total_counter())
        self.true_probs = self.true_counts.copy()
        temptotal = sum(self.true_counts.values())
        for key in self.true_probs.keys():
            self.true_probs[key] /= temptotal

    def _get_add_data(self, wcount, totalcount, dictsize, crossentropy=False):
        if crossentropy:
            return {
            f"UniqueTokens{dictsize}": len(wcount),
            f"TokensCounted{dictsize}": 100 * sum(wcount.values()) / (totalcount),
            f"Entropy{dictsize}": _entropy(wcount),
            f"Cross-Entropy{dictsize}": _crossentropy(wcount, self.true_probs),
            }
        return {
            f"UniqueTokens{dictsize}": len(wcount),
            f"TokensCounted{dictsize}": 100 * sum(wcount.values()) / (totalcount),
            f"Entropy{dictsize}": _entropy(wcount),
            f"Counter{dictsize}": wcount,
        }
        

    def clean_total_uknown(self):
        for k in list(self.total_uknown.keys()):
            if k in self.w95:
                del self.total_uknown[k]

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
        totalcount = text.count(" ") - number_counter
        add_data = [
            {
                "Name": name,
                "TotalTokens": totalcount,
            }
        ]
        add70 = self._get_add_data(wcount, totalcount, 70)
        for k, v in unkcount.items():
            if k in self.w80:
                wcount[k] = v
        add80 = self._get_add_data(wcount, totalcount, 80)
        for k, v in unkcount.items():
            if k in self.w95:
                wcount[k] = v
        add95 = self._get_add_data(wcount, totalcount, 95, crossentropy=self.cross95)
        add_data[0].update(add70)
        add_data[0].update(add80)
        add_data[0].update(add95)
        self.df = self.df.append(add_data, ignore_index=True, sort=False)
        self.total_counter.update(wcount)
        self.total_uknown.update(unkcount)

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
