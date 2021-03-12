# eigolingo

Using eigolingo you can answer the question "How many unique words are in this book/text/novel?" in under a second.

This repository contains the resources necessary to generate English wordlists (namely wordlist70, 80, and 95.txt) and inflection dictionaries (dict70, 80 adn 95.txt). To see how they are generated feel free to open the notebook in Google Colab and modify the process as you please.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/exc4l/eigolingo/blob/main/generate_spacy_wordlist.ipynb)

## Motivation

It all started with the simple question: "How many unique words are there in {novel}". While fiddling out ways to answer this question I've encountered several obstacles which ultimately led me to create the wordlists and dictionaries. Some of these obstacles include:
1. Do inflected forms count separately?
2. To what extend should proper nouns be included?
3. Should words denoting origin (e.g. French, Swedish) count?
4. What about denominal verbs?
5. Should one include words the author made up (e.g. ungood, doublethink)?
6. ...

Therefore I decided to create wordlists that define what an "allowed" English word is, but also deemed it necessary to create multiple lists of varying magnitude following different considerations, which is denoted by the number in the filename and using those wordlists inflection dictionaries were created which map inflections to the lemma.

## Result

In its current form, the question the eigolingo answers is closer to: "How many unique words does one need to know to understand the novel?" This is due to how I decided to answer the posed questions. The inflection dictionary is used to determine the lemma of a token(word). In the creation of the dictionary several filters are applied which do (or should) remove proper nouns to a large extent. I did this as I currently believe that most proper nouns are not integral to understanding the novel and therefore don't carry the weight of what I wanted to call a unique word. This is, of course, my own opinion and the filtering can easily be excluded if deemed necessary.

To illustrate the workings I will use George Orwell's Novel - 1984, which recently fell into the public domain in most countries.\
Using the varying dictionary sizes we receive:
| Dict Size | Unique Tokens | Tokens Counted | Total Tokens |
|-----------|---------------|----------------|--------------|
| 70        | 6158          | 98.41%         | 104759       |
| 80        | 6166          | 98.44%         | 104759       |
| 95        | 6215          | 98.85%         | 104759       |

The 8 additional tokens counted for 80 are:\
eard, sye, versificator, stepney, mache, mediterranean, schoolmasterish

Part of the additional words in the 95 dictionary vs 80 are:\
russian, cromwell, noctis, brazilian, undark, dane, eurasian, african, jewish, chinese, australian, milton, leopoldville, ungood

Part of the tokens not counted:\
doubleplusungood, japan, minitrue, baal, doubleplusgood, sunday, doubleplus, russia, uncold, brazzaville, byron, thoughtcriminals, goldstein, presia, adam, tibet, rhine\
\
This also includes typos inside the book and errors caused by my pre-processing:\
lslands (first letter is a L not an i), ealth ('ealth as dialect), humand ("machine did raise the living standards of the average humand being very greatly over a period of about fifty years")

In this case, going from 70 to 80 counts just 8 additional tokens. The interesting bit lies in the jump from 80 to 95. Nearly 50 additional tokens and, as one can see, a lot of them are adjectives denoting origin. I don't actively filter them, it just so happens that only the 95 dictionary includes them. Not-counted are, of course, the proper nouns that I actively filter for but also most words made up by Orwell fall into this category. In total, 206 tokens are not considered by the script.

## Usage

It's as easy as it gets. The dictionary size defaults to 70.
```python
python eigolingo.py [textfile] [dictionary size]
```
e.g.
```python
python eigolingo.py 1984.txt 70
python eigolingo.py 1984.txt 80
python eigolingo.py 1984.txt 95
```

## License
Please check the licenses of the wordlists used. The necessary sources can be found in the README in the lists directory.

Check the MIT-like License of this repository.