# eigolingo
This repository contains the resources necessary to generate English wordlists (namely wordlist70, 80, and 95.txt). To see how they are generated feel free to open the notebook in Google Colab and modify the process as you please.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/exc4l/eigolingo/blob/main/generate_spacy_wordlist.ipynb)

Furthermore, it contains a simple script to calculate the number of unique words in any given text file.

## Motivation

It all started with the simple question: "How many unique words are there in {Novel}". While fiddling out ways to answer this question I've encountered several obstacles which ultimately led me to create the wordlists. Some of these obstacles include:
1. Do inflected forms count separately?
2. To what extend should proper nouns be included?
3. Should adjectives denoting origin (e.g. French, Swedish) count?
4. What about denominal verbs?
5. Should one include words the author made up (e.g. ungood, doublethink)?
6. ...

Therefore I decided to create wordlists that define what an "allowed" English word is, but also deemed it necessary to create multiple lists of varying magnitude following different considerations.



