#!/usr/bin/env python
from aae import parse
import json,pickle
import os
import random

def subcorpus(CORPUS, n, ndiff, nhomo, rootphon='SAE', altphon='AAE'):
    nsame = n-ndiff
    words_diff = []
    words_same = []
    for word, d in CORPUS.items():
        if d['phon'][rootphon] is not d['phon'][altphon]:
            words_diff.append(word)
        else:
            words_same.append(word)

    HOMO = parse.homophones(CORPUS)
    tmp = random.sample(HOMO[rootphon].values(),nhomo)
    words_homo_a = [item for sublist in tmp for item in sublist]
    words_homo = list(set(words_homo_a))
    samp = list(words_homo)

    samp_nsame = sum([1 for w in samp if w in words_same])
    samp_ndiff = sum([1 for w in samp if w in words_diff])

    samp.extend(random.sample(words_diff, ndiff-samp_ndiff))
    samp.extend(random.sample(words_same, nsame-samp_nsame))

    ## Subset the full datasets
    subcorpus = {word: CORPUS[word] for word in samp}

    ## Document Homophones
    subhomo = parse.homophones(subcorpus)

    return (subcorpus, subhomo)
