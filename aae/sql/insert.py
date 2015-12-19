import sqlite3
# N.B. SQL statements built with the Python "string".format() method are not
# protected against SQL Injection Attacks. This code is not intended to be web
# hosted or to record sensitive information.
# N.B. In many cases, a single insert command with many values to insert is
# composed and executed. At present, none of these are buffered in any way. For
# anticipated use cases, this is fine, but may be an issue if the amount of
# data to be inserted becomes "too large".

def words(conn, corpus, word_labels):
    """
    Insert word into database and associate with a corpus.

    # Insert one word. [] are required.
    >>> aae.sql.insert.words(conn, "3k", ["apple"])

    # Insert multiple words.
    >>> aae.sql.insert.words(conn, "3k", ["apple", "banana"])

    """
    cmd_select = "SELECT id FROM corpus WHERE label=:corpus LIMIT 1"
    cmd_insert = "INSERT INTO word (corpus_id, word) VALUES "
    values = []
    # In the event of an exception, the transaction is rolled back; otherwise,
    # the transaction is committed.
    with conn:
        cur = conn.cursor()
        # Lookup an id to use as foreign key
        cur.execute(cmd_select, {'corpus': corpus})
        r = cur.fetchone()
        corpus_id = r['id']
        # Compose a string of multiple insert values
        values = ','.join(
                ["({corpus_id},{word},{ortho})".format(corpus_id=corpus_id,word=w)
                    for w in word_labels]
                )+';'
        # Append insert values to the rest of the insert command
        cmd_insert += values
        # Execute insert command
        cur.execute(cmd_insert)

def corpus(conn, label, description='', word_labels=[]):
    """
    Insert corpus into database.

    # Register a corpus
    >>> aae.sql.insert.corpus(conn, "3k")

    # Register a corpus with a description
    >>> aae.sql.insert.corpus(conn, "3k", "~3000 word corpus.")

    # Register a corpus, and also insert a list of words
    >>> words = ["apple","banana","carrot"]
    >>> ortho = ["_apple","banana","carrot"]
    >>> aae.sql.insert.corpus(conn, "abc", words=words)

    """
    cmd_insert = "INSERT INTO corpus (label, description) VALUES (:label,:desc)"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_insert, {'label': corpus, 'desc': description})

    if word_labels:
        words(conn, label, word_labels)

def phoneme_representations(conn, dialect, phonmap):
    """
    Insert dialect into database.

    # Register a dialect
    >>> aae.sql.insert.corpus(conn, "standard")

    # Register a dialect with a description
    >>> aae.sql.insert.corpus(conn, "mild", "Only vowels differ from standard.")
    >>> aae.sql.insert.corpus(conn, "strong", "Both vowels and consonants differ from standard.")

    """
    cmd_insert = "INSERT INTO phonrep (phoneme_id,dialect_id,unit,value) VALUES (:phoneme_id,:dialect_id,:unit,:value)"
    cmd_select_dialect_id = "SELECT id FROM dialect WHERE label=:dialect LIMIT 1"
    cmd_select_phoneme_id = "SELECT id FROM phoneme WHERE phoneme=:phoneme LIMIT 1"
    values = []
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_dialect_id, {'dialect': dialect})
        r = cur.fetchone()
        dialect_id = r['id']
        for phoneme,representation in phonmap.items():
            try:
                cur.execute(cmd_select_phoneme_id, {'phoneme': phoneme})
            except sqlite3.DataError:
                print "Adding phoneme `"+phoneme+"` to database."
                phonemes(conn, phoneme)
                cur.execute(cmd_select_phoneme_id, {'phoneme': phoneme})

            r = cur.fetchone()
            phoneme_id = r['id']
            values.extend(
                    ["({dialect_id},{phoneme_id},{unit},{value})".format(dialect_id=dialect_id,phoneme_id=word_id,unit=i,value=v)
                        for i,v in enumerate(representation)]
                    )
        cmd_insert += ','.join(values)+';'
        cur.execute(cmd_insert)

def dialect(conn, label, description='', phonmap={}):
    """
    Insert dialect into database.

    # Register a dialect
    >>> aae.sql.insert.dialect(conn, "standard")

    # Register a dialect with a description
    >>> aae.sql.insert.dialect(conn, "mild", "Only vowels differ from standard.")
    >>> aae.sql.insert.dialect(conn, "strong", "Both vowels and consonants differ from standard.")

    """
    cmd_insert = "INSERT INTO dialect (label, description) VALUES (:label,:desc)"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_insert, {'label': dialect, 'desc': description})

    if phonmap:
        phoneme_representations(conn, label, phonmap)

def rule(conn, label, description=''):
    """
    Insert a rule into the database.

    What is stored in the database is just a label so that words within
    languages can be tagged. In this corpus, different languages are derived
    from SAE by applying rules. The rule itself is an algorithm, and cannot be
    stored in the database. However, by maintaining a table of rule names the
    influence of each rule on particular words within languages can be tracked.

    # Register a rule with a description.
    >>> aae.sql.insert.rule(conn, "devoice","Final phonemes /b/, /d/, /v/, or /z/ replaced with /p/, /t/, /f/, and /s/, respectively, if preceded by a vowel. ")
    >>> aae.sql.insert.rule(conn, "consonant_cluster_reduction", "If a word ends with a consonant cluster, and the cluster ends with /t/ /d/ /s/ or /z/, drop it.")
    >>> aae.sql.insert.rule(conn, "postvocalic_reduction", "If a word ends with a vowel followed by an /r/, drop the /r/.")

    """
    cmd_insert = "INSERT INTO rule (label, description) VALUES (:label,:desc)"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_insert, {'label': dialect, 'desc': description})

def language_has_rules(conn, language_label, has_rules):
    """
    Insert relationship between a language and one or more rules.

    # Insert one rule. [] are required.
    >>> aae.sql.insert.rule(conn, "AAE", ["devoice"])

    # Insert multiple rules.
    >>> aae.sql.insert.rule(conn, "AAE", ["devoice", "consonant_cluster_reduction"])

    """
    cmd_select_language_id = "SELECT id FROM language WHERE label=:language LIMIT 1"
    cmd_select_rule_id = "SELECT id FROM rule WHERE label=:rule LIMIT 1"
    cmd_insert = "INSERT INTO language_has_rule (language_id,rule_id) VALUES (:lid,:rid)"
    with conn:
        cur = conn.cursor()
        # Lookup the language id to use as foreign key
        cur.execute(cmd_select_language_id, {'language': language_label})
        r = cur.fetchone()
        language_id = r['id']
        for rule_label in has_rules:
            # Lookup the rule id to use as foreign key
            try:
                cur.execute(cmd_select_rule_id, {'phoneme': phoneme})
            except sqlite3.DataError:
                print "Adding rule `"+rule+"` to database."
                rule(conn, rule_label)
                cur.execute(cmd_select_phoneme_id, {'phoneme': phoneme})
                cur.execute(cmd_select_rule_id, {'phoneme': phoneme})
            cur.execute(cmd_select_rule, {'rule': rule})
            r = cur.fetchone()
            rule_id = r['id']
            # Execute insert command
            cur.execute(cmd_insert, {'lid': language_id, 'rid': rule_id})

def language(conn, label, description='', has_rules=[]):
    """
    Insert a language into the database.

    """
    cmd_insert = "INSERT INTO language (label, description) VALUES (:label,:desc)"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_insert, {'label': dialect, 'desc': description})

    if has_rules:
        language_has_rules(conn, label, has_rules)

def phonemes(conn, phonemes):
    """
    Insert word into database and associate with a corpus.

    # Insert one phoneme. [] are required.
    >>> aae.sql.insert.phonemes(conn, ["^"])

    # Insert multiple rules.
    >>> aae.sql.insert.phonemes(conn, ["^", "a"])

    """
    cmd_insert = "INSERT INTO phoneme (phoneme) VALUES "
    values = ','.join(phonemes)+';'
    cmd_insert += values
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_insert)

def phonology(conn, corpus_label, language_label, phoncodemap):
    """
    Insert phonological transcription code for words within a language.

    # Insert phoncode for one word
    >>> aae.sql.insert.phonology(conn, "3k", "SAE", {"fawn": "__fan_____"})

    # Insert phoncode for multiple words.
    >>> aae.sql.insert.phonology(conn, "3k", "SAE", {"fawn": "__fan_____", "foul": "__fWl_____"})

    """
    cmd_select_language_id = "SELECT id FROM language WHERE label=:language LIMIT 1"
    cmd_select_corpus_id = "SELECT id FROM corpus WHERE corpus=:corpus LIMIT 1"
    cmd_select_word_id = "SELECT id FROM word WHERE word=:word AND corpus_id=:corpus_id LIMIT 1"
    cmd_insert = "INSERT INTO phonology (corpus_id,language_id,word_id,phoncode) VALUES "
    values = []
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_language_id, {'language': language_label})
        r = cur.fetchone()
        language_id = r['id']
        for word,phoncode in phonology_phoncode.items():
            cur.execute(cmd_select_corpus_id, {'corpus': corpus_label})
            corpus_id = r['id']
            cur.execute(cmd_select_word_id, {'word': word, 'corpus_id': corpus_id})
            r = cur.fetchone()
            word_id = r['id']
            values.append("({corpus_id},{language_id},{word_id},{phoncode})".format(corpus_id=corpus_id,language_id=language_id,word_id=word_id,phoncode=phoncode))
        cmd_insert += ','.join(values)+';'
        cur.execute(cmd_insert)

def phonology_has_rule(conn, language_label, phonology_phoncode, rule):
    """
    Insert relationship between a rule application and a non-standard
    phonological transcription code within a language.

    # Insert relationship between one phonological transcription and one rule.
    >>> aae.sql.insert.phonology_has_rule(conn, "AAE", ["str@n_____"], "consonant_cluster_reduction")

    # Insert relationship between multiple phonological transcriptions and one rule.
    >>> aae.sql.insert.phonology_has_rule(conn, "AAE", ["str@n_____", "__rWn_____"], "consonant_cluster_reduction")

    """
    cmd_select_language_id = "SELECT id FROM language WHERE label=:language LIMIT 1"
    cmd_select_rule_id = "SELECT id FROM rule WHERE label=:rule LIMIT 1"
    cmd_select_phonology_id = "SELECT id FROM phonology WHERE language_id=:language_id AND phoncode IN (" + ",".join("?"*len(phonology_phoncode)) + ")"
    cmd_insert = "INSERT INTO phonology_has_rule (rule_id,phonology_id) VALUES "
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_language_id, {'language': language_label})
        r = cur.fetchone()
        language_id = r['id']
        cur.execute(cmd_select_rule_id, {'rule': rule})
        r = cur.fetchone()
        rule_id = r['id']
        cur.execute(cmd_select_phonology_id, phonology_phoncode)
        R = cur.fetchall()
        values = ','.join(
                ["({rule_id},{phon_id})".format(rule_id=rule_id,phon_id=r['id'])
                    for r in R]
                )+';'
        cmd_insert += values
        cur.execute(cmd_insert)

def phonology_has_phonemes(conn, update=False):
    """
    Insert relationships between all phonological transcriptions (strings), and
    their contituent phonemes. Necessary to produce phonological representations
    for complete utterances.

    # Insert all relationships between phonological transcriptions and phonemes
    # that do not already exist.
    >>> aae.sql.insert.phonology_has_phonemes(conn)

    # Insert all relationships between phonological transcriptions and
    # phonemes, updating existing ones.
    >>> aae.sql.insert.phonology_has_phonemes(conn, update=True)

    """
    cmd_insert = "INSERT INTO phonology_has_phoneme (phonology_id,phoneme_id,unit) VALUES "
    values = []
    existing_phonology_id = []
    with conn:
        cur = conn.cursor()
        if not update:
            cur.execute("SELECT DISTINCT phonology_id FROM phonology_has_phoneme")
            existing_phonology_id = [r['id'] for r in cur.fetchall()]

        cur.execute("SELECT id, phoneme FROM phoneme;")
        phoneme_to_id = dict([(r['phoneme'],r['id']) for r in cur.fetchall()])
        cur.execute("SELECT id, phoncode FROM phonology;")
        for r in cur.fetchall():
            # if update == True, existing_phonology_id is empty, so statement
            # always evaluates to True.
            if not r['id'] in existing_phonology_id:
                values.extend(
                        ["({phonology_id},{phoneme_id},{unit})".format(
                            phonology_id=r['id'],phoneme_id=phoneme_to_id[p],unit=i)
                            for p in r['phoncode']])

        cmd_insert += ','.join(values)+';'
        cur.execute(cmd_insert)

def semantic_representation(conn, corpus_label, semmap):
    """
    Insert semantic representations for words in a corpus.

    # Insert representation for one word
    >>> aae.sql.insert.semantic_representation(conn, "3k", {"apple": [0,1,1,0]})

    # Insert representations for multiple words.
    >>> aae.sql.insert.semantic_representation(conn, "3k", {"apple": [0,1,1,0], "banana": [1,1,1,0]})

    """
    cmd_select_corpus_id = "SELECT id FROM corpus WHERE label=:corpus LIMIT 1"
    cmd_select_word_id = "SELECT id FROM word WHERE word=:word AND corpus_id=:corpus_id LIMIT 1"
    cmd_insert = "INSERT INTO semrep (corpus_id,word_id,unit,value) VALUES "
    values = []
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_corpus_id, {'corpus': corpus_label})
        r = cur.fetchone()
        corpus_id = r['id']
        for word,representation in semmap.items():
            cur.execute(cmd_select_word_id, {'word': word, 'corpus_id': corpus_id})
            r = cur.fetchone()
            word_id = r['id']
            values.extend(
                    ["({corpus_id},{word_id},{unit},{value})".format(corpus_id=corpus_id,word_id=word_id,unit=i,value=v)
                        for i,v in enumerate(representation)]
                    )
        cmd_insert += ','.join(values)+';'
        cur.execute(cmd_insert)
