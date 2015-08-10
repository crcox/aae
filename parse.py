def corpus(corppath,semmap,phonmap,phonmap_label,phon_label):
    CORPUS = {}
    with open(corppath, 'r') as f:
        for i,line in enumerate(f):
            data = line.strip().split()

            phon_code = data[2]
            phon = []
            for p in phon_code:
                phon.append(phonmap[p])

            word = data[0]
            CORPUS[word] = {
                    'orth_code' : data[1],
                    'phonmap'   : phonmap_label,
                    'phon'      : {phon_label : phon},
                    'phon_code' : {phon_label : data[2]},
                    'freq'      : int(data[3]),
                    'sem'       : semmap[word]
                    }
    return CORPUS

def homophones(CORPUS):
    x = CORPUS.keys()[0]
    pronunciations = CORPUS[x]['phon'].keys()
    HOMO = {k:{} for k in pronunciations}
    for p in pronunciations:
        for word,d in CORPUS.items():
            phon_code = d['phon_code'][p]
            try:
                HOMO[p][phon_code].append(word)
            except KeyError:
                HOMO[p][phon_code] = [word]

        for word,homo in HOMO[p].items():
            if len(homo) == 1:
                del HOMO[p][word]
    return HOMO

def phonology(phonpath):
    PHON_MAP = {}
    with open(phonpath, 'r') as f:
        for line in f:
            tmp = line.strip().split()
            PHON_MAP[tmp[0]] = [int(x) for x in tmp[1:]]
    return PHON_MAP

def semantics(sempath):
    SEM_MAP = []
    with open(sempath, 'r') as f:
        for line in f:
            tmp = line.strip().split()
            SEM_MAP.append([int(x) for x in tmp[1:]])
    return SEM_MAP

def altpronunciation(CORPUS, plabel, rulelist, PHON_MAP, rootphon='SAE'):
    from aae import rules
    changelog = {k:[] for k in rulelist}
    for word, d in CORPUS.items():
        RuleApplied = False
        phon_code,dashes = stripdash(d['phon_code'][rootphon])
        for r in rulelist:
            rule = getattr(rules, r)
            b,phon_code = rule(phon_code)
            RuleApplied = RuleApplied or b
            if b:
                changelog[r].append(word)

        phon_code = applydash(phon_code,dashes)
        phon = []
        for x in phon_code:
            phon.append(PHON_MAP[x])

        if RuleApplied:
            CORPUS[word]['phon_code'][plabel] = phon_code
            CORPUS[word]['phon'][plabel] = phon
        else:
            CORPUS[word]['phon_code'][plabel] = CORPUS[word]['phon_code'][rootphon]
            CORPUS[word]['phon'][plabel] = CORPUS[word]['phon'][rootphon]
    return (CORPUS,changelog)

def stripdash(p_):
    import re
    # Record dashes
    pat = re.compile('_+')
    dashes = pat.findall(p_)
    if len(dashes) == 1:
        if p_[0] == '_':
            dashes = dashes + ['']
        else:
            dashes = [''] + dashes

    # Strip dashes
    p = p_.strip('_')
    return tuple([p,dashes])

def applydash(p,dashes):
    p_ = ''.join([dashes[0],p,dashes[-1]])
    return p_
