import aae
def addpronunciation(CORPUS, plabel, rulelist, PHON_MAP, rootphon='SAE'):
    changelog = {k:[] for k in rulelist}
    for word, d in CORPUS.items():
        phon_code,dashes = stripdash(d['phon_code'][rootphon])
        for r in rulelist:
            rule = getattr(aae.rules, r)
            RuleApplied,phon_code = rule(phon_code)
            if RuleApplied:
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
