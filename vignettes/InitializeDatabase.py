#!/usr/bin/env python
import os,json,pickle,sys
import sqlite3
import string
import aae
import aae.sql
from aae.accents import standard as PHON_MAP
from aae.semantics import standard_3k as SEM_MAP

db_name = "./aae_base.db"
db_schema = "./data_schema.sql"
stim_master = "../raw/3kdict"

# Load the corpus
CORPUS = aae.parse.corpus(stim_master, SEM_MAP, PHON_MAP, "standard", 'SAE')

# Create AAE
words = [w for w in CORPUS.keys()]
orthcodemap = dict([(w,CORPUS[w]['orth_code']) for w in CORPUS.keys()])
phoncodemap = dict([(w,CORPUS[w]['phon_code']['SAE']) for w in CORPUS.keys()])

# Create basic orthography code
# All letters are orthogonal to each other. No inherent similarity structure at grapheme level.
ORTH_MAP = {}
for i,c in enumerate(string.ascii_lowercase + '_'):
    row = [0] * 26
    if i < 26:
        row[i] = 1
    ORTH_MAP[c] = row

conn = sqlite3.connect(db_name)
conn.row_factory = sqlite3.Row

with open(db_schema, 'r') as f:
    conn.executescript(f.read())

aae.sql.insert.corpus(conn, "3k", "Approx. 3000 word corpus.", word_labels=words)
# Semantics
aae.sql.insert.semantic_representation(conn, "3k", semmap=SEM_MAP)
# Phonology
aae.sql.insert.accent(conn, "standard", "Inherited along with corpora.", phonmap=PHON_MAP)
aae.sql.insert.rule(conn, "devoice", "Final phonemes /b/, /d/, /v/, or /z/ replaced with /p/, /t/, /f/, and /s/, respectively, if preceded by a vowel. ")
aae.sql.insert.rule(conn, "consonant_cluster_reduction", "If a word ends with a consonant cluster, and the cluster ends with /t/ /d/ /s/ or /z/, drop it.")
aae.sql.insert.rule(conn, "postvocalic_reduction", "If a word ends with a vowel followed by an /r/, drop the /r/.")
aae.sql.insert.dialect(conn, "SAE", "Standard American English.", has_rules=[])
aae.sql.insert.dialect(conn, "AAE", "African American English.", has_rules=['consonant_cluster_reduction', 'postvocalic_reduction'])
aae.sql.insert.phonology(conn, "3k", "SAE", phoncodemap=phoncodemap)
aae.sql.insert.phonology(conn, "3k", "AAE", phoncodemap=phoncodemap)
aae.sql.insert.phonology_has_phonemes(conn, update=False)
# Orthography
aae.sql.insert.alphabet(conn, "orthogonal", description="No inherent similarity among graphemes.", orthmap=ORTH_MAP)
aae.sql.insert.orthography(conn, "3k", orthcodemap=orthcodemap)
aae.sql.insert.orthography_has_graphemes(conn, update=False)
# Sample
## A sample can be explicitly defined.
with open("original_stimlist_500_250.txt", "r") as f:
    stimlist=[x.strip() for x in f.readlines()]

aae.sql.insert.sample(conn, "3k", "SAE", "AAE", "standard", 500, 250, 20)
aae.sql.insert.sample(conn, "3k", "SAE", "AAE", "standard", 500, 250, 20, list_stim=stimlist)

conn.close()
