from aae import phoncodes
import re

# DEVOICING
# Rule 1: Final phonemes /b/, /d/, /v/, or /z/ replaced with /p/, /t/,
# /f/, and /s/, respectively, if preceded by a vowel.
def devoice(p):
    devoicing_rules = {
        'b':'p',
        'd':'t',
    #	'g':'k',
        'v':'f',
        'z':'s'
        }

    plist = list(p)
    b = False
    try:
        if p[-2] in phoncodes.vowels and p[-1] in devoicing_rules.keys():
            plist[-1] = devoicing_rules[p[-1]]
            p = ''.join(plist)
            b = True
    except IndexError:
        pass

    return (b,p)

def consonant_cluster_reduction(p):
    # Consonant Cluster Reduction
    # Rule 2: If a word ends with a consonant cluster, and the cluster ends
    # with /t/ /d/ /s/ or /z/, drop it.
    plist = list(p)
    b = False
    try:
        if p[-2] in phoncodes.consonants and p[-1] in ['t','d','s','z']:
            plist[-1] = '_'
            p = ''.join(plist)
            b = True
    except IndexError:
        pass

    return (b,p)

def postvocalic_reduction(p):
    # Post-vocalic Reduction
    # Rule 3: If a word ends with a vowel followed by an /r/, drop the /r/.
    plist = list(p)
    b = False
    try:
        if p[-2] in phoncodes.vowels and p[-1] == 'r':
            plist[-1] = '_'
            p = ''.join(plist)
            b = True
    except IndexError:
        pass

    return (b,p)
