import sqlite3
import random
import aae
# N.B. SQL statements built with the Python "string".format() method are not
# protected against SQL Injection Attacks. This code is not intended to be web
# hosted or to record sensitive information.
# N.B. In many cases, a single insert command with many values to insert is
# composed and executed. At present, none of these are buffered in any way. For
# anticipated use cases, this is fine, but may be an issue if the amount of
# data to be inserted becomes "too large".

def words(conn, corpus, word_labels, word_frequency=[]):
    """
    Insert word into database and associate with a corpus.

    # Insert one word. [] are required.
    >>> aae.sql.insert.words(conn, "3k", ["apple"])

    # Insert multiple words.
    >>> aae.sql.insert.words(conn, "3k", ["apple", "banana"])

    """
    cmd_select = "SELECT id FROM corpus WHERE label=:corpus LIMIT 1"
    if word_frequency:
        cmd_insert = "INSERT INTO word (corpus_id, word, frequency) VALUES (?, ?, ?)"
    else:
        cmd_insert = "INSERT INTO word (corpus_id, word) VALUES (?, ?)"

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
#        values = ','.join(
#                ["({corpus_id},{word})".format(corpus_id=corpus_id,word=w)
#                    for w in word_labels]
#                )+';'
#        # Append insert values to the rest of the insert command
#        cmd_insert += values

        if word_frequency:
            if len(word_labels) != len(word_frequency):
                raise RuntimeError('Word and frequency lists are of different lengths.')
            values = zip([corpus_id]*len(word_labels), word_labels, word_frequency)
        else:
            values = zip([corpus_id]*len(word_labels), word_labels)

        # Execute insert command
        cur.executemany(cmd_insert, values)

def corpus(conn, label, description='', word_labels=[]):
    """
    Insert corpus into database.

    # Register a corpus
    >>> aae.sql.insert.corpus(conn, "3k")

    # Register a corpus with a description
    >>> aae.sql.insert.corpus(conn, "3k", "~3000 word corpus.")

    # Register a corpus, and also insert a list of words
    >>> words = ["apple","banana","carrot"]
    >>> aae.sql.insert.corpus(conn, "abc", word_labels=words)

    """
    cmd_insert = "INSERT INTO corpus (label, description) VALUES (:label,:desc)"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_insert, {'label': label, 'desc': description})

    if word_labels:
        words(conn, label, word_labels)

def phoneme_representations(conn, accent, phonmap, verbose=False):
    """
    Insert accent into database.

    # Register a accent
    >>> aae.sql.insert.corpus(conn, "standard")

    # Register a accent with a description
    >>> aae.sql.insert.corpus(conn, "mild", "Only vowels differ from standard.")
    >>> aae.sql.insert.corpus(conn, "strong", "Both vowels and consonants differ from standard.")

    """
    cmd_insert = "INSERT INTO phonrep (accent_id,phoneme_id,unit,value) VALUES (?,?,?,?);"
    cmd_select_accent_id = "SELECT id FROM accent WHERE label=:accent LIMIT 1;"
    cmd_select_phoneme_id = "SELECT id FROM phoneme WHERE phoneme=:phoneme LIMIT 1;"
    values = []
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_accent_id, {'accent': accent})
        r = cur.fetchone()
        accent_id = r['id']
        for phoneme,representation in phonmap.items():
            cur.execute(cmd_select_phoneme_id, {'phoneme': phoneme})
            r = cur.fetchone()
            if r is None:
                if verbose:
                    print "Adding phoneme `"+phoneme+"` to database."
                phonemes(conn, phoneme)
                cur.execute(cmd_select_phoneme_id, {'phoneme': phoneme})
                r = cur.fetchone()

            phoneme_id = r['id']
            n = len(representation)
            values.extend(zip([accent_id]*n, [phoneme_id]*n, range(n), representation))
        cur.executemany(cmd_insert, values)

def accent(conn, label, description='', phonmap={}):
    """
    Insert accent into database.

    # Register a accent
    >>> aae.sql.insert.accent(conn, "standard")

    # Register a accent with a description
    >>> aae.sql.insert.accent(conn, "mild", "Only vowels differ from standard.")
    >>> aae.sql.insert.accent(conn, "strong", "Both vowels and consonants differ from standard.")

    """
    cmd_insert = "INSERT INTO accent (label, description) VALUES (:label,:desc)"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_insert, {'label': label, 'desc': description})

    if phonmap:
        phoneme_representations(conn, label, phonmap)

def rule(conn, label, description=''):
    """
    Insert a rule into the database.

    What is stored in the database is just a label so that words within
    dialects can be tagged. In this corpus, different dialects are derived
    from SAE by applying rules. The rule itself is an algorithm, and cannot be
    stored in the database. However, by maintaining a table of rule names the
    influence of each rule on particular words within dialects can be tracked.

    # Register a rule with a description.
    >>> aae.sql.insert.rule(conn, "devoice","Final phonemes /b/, /d/, /v/, or /z/ replaced with /p/, /t/, /f/, and /s/, respectively, if preceded by a vowel. ")
    >>> aae.sql.insert.rule(conn, "consonant_cluster_reduction", "If a word ends with a consonant cluster, and the cluster ends with /t/ /d/ /s/ or /z/, drop it.")
    >>> aae.sql.insert.rule(conn, "postvocalic_reduction", "If a word ends with a vowel followed by an /r/, drop the /r/.")

    """
    cmd_insert = "INSERT INTO rule (label, description) VALUES (:label,:desc)"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_insert, {'label': label, 'desc': description})

def dialect_has_rules(conn, dialect_label, has_rules, verbose=False):
    """
    Insert relationship between a dialect and one or more rules.

    # Insert one rule. [] are required.
    >>> aae.sql.insert.rule(conn, "AAE", ["devoice"])

    # Insert multiple rules.
    >>> aae.sql.insert.rule(conn, "AAE", ["devoice", "consonant_cluster_reduction"])

    """
    cmd_select_dialect_id = "SELECT id FROM dialect WHERE label=:dialect LIMIT 1"
    cmd_select_rule_id = "SELECT id FROM rule WHERE label=:rule LIMIT 1"
    cmd_insert = "INSERT INTO dialect_has_rule (dialect_id,rule_id) VALUES (:lid,:rid)"
    with conn:
        cur = conn.cursor()
        # Lookup the dialect id to use as foreign key
        cur.execute(cmd_select_dialect_id, {'dialect': dialect_label})
        r = cur.fetchone()
        dialect_id = r['id']
        for rule_label in has_rules:
            # Lookup the rule id to use as foreign key
            cur.execute(cmd_select_rule_id, {'rule': rule_label})
            r = cur.fetchone()
            if r is None:
                if verbose:
                    print "Adding rule `"+rule+"` to database."
                rule(conn, rule_label)
                cur.execute(cmd_select_rule_id, {'rule': rule_label})
                r = cur.fetchone()
            rule_id = r['id']
            # Execute insert command
            cur.execute(cmd_insert, {'lid': dialect_id, 'rid': rule_id})

def dialect(conn, label, description='', has_rules=[]):
    """
    Insert a dialect into the database.

    """
    cmd_insert = "INSERT INTO dialect (label, description) VALUES (:label,:desc)"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_insert, {'label': label, 'desc': description})

    if has_rules:
        dialect_has_rules(conn, label, has_rules)

def phonemes(conn, phonemes):
    """
    Insert word into database and associate with a corpus.

    # Insert one phoneme. [] are required.
    >>> aae.sql.insert.phonemes(conn, ["^"])

    # Insert multiple rules.
    >>> aae.sql.insert.phonemes(conn, ["^", "a"])

    """
    cmd_insert = "INSERT INTO phoneme (phoneme) VALUES (?);"
    with conn:
        cur = conn.cursor()
        if isinstance(phonemes, list):
            cur.executemany(cmd_insert, phonemes)
        else:
            cur.execute(cmd_insert, phonemes)

def phonology(conn, corpus_label, dialect_label, phoncodemap):
    """
    Insert phonological transcription code for words within a dialect.

    # Insert phoncode for one word
    >>> aae.sql.insert.phonology(conn, "3k", "SAE", {"fawn": "__fan_____"})

    # Insert phoncode for multiple words.
    >>> aae.sql.insert.phonology(conn, "3k", "SAE", {"fawn": "__fan_____", "foul": "__fWl_____"})

    """
    cmd_select_dialect_id = "SELECT id FROM dialect WHERE label=:dialect LIMIT 1;"
    cmd_select_corpus_id = "SELECT id FROM corpus WHERE label=:corpus LIMIT 1;"
    cmd_select_word_id = "SELECT id FROM word WHERE word=:word AND corpus_id=:corpus_id LIMIT 1;"
    cmd_select_word_ids = "SELECT id FROM word WHERE corpus_id=? AND word IN (?);"
    cmd_select_phonology = "SELECT id FROM phonology WHERE phoncode=:phoncode LIMIT 1;"
    cmd_select_rules = "SELECT id,label FROM rule JOIN dialect_has_rule ON rule.id=dialect_has_rule.rule_id WHERE dialect_id=:dialect_id;"
    cmd_insert_phonology = "INSERT INTO phonology (phoncode) VALUES (?);"
    cmd_insert_phonology_has_rule = "INSERT INTO phonology_has_rule (dialect_id, word_id, phonology_id, rule_id) VALUES (?,?,?,?);"
    # cmd_insert_homo = "INSERT INTO homophones (corpus_id,word_id,homo_id) VALUES (?,?,?);"
    cmd_insert_word_has_phonology = "INSERT INTO word_has_phonology (word_id,dialect_id,phonology_id) VALUES (?,?,?);"
    cmd_insert_dialect_has_phonology = "INSERT INTO dialect_has_phonology (dialect_id,phonology_id) VALUES (?,?);"

    def applyrules(phoncode, rulelist):
        """
        Rules will be applied in order, and effects will accumulate.

        """
        phoncode,dashes = aae.parse.stripdash(phoncode)
        rules_applied = []
        for r in rulelist:
            rule = getattr(aae.rules, r['label'])
            phoncode_new = rule(phoncode)
            if phoncode_new:
                rules_applied.append(r['id'])
                phoncode = phoncode_new

        phoncode = aae.parse.applydash(phoncode,dashes)
        return (phoncode, rules_applied)

    values = []
    homophones = []
    dialect_has_phonology_values = []
    word_has_phonology_values = []
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_dialect_id, {'dialect': dialect_label})
        r = cur.fetchone()
        dialect_id = r['id']
        print '************ ' + str(dialect_id)
        cur.execute(cmd_select_rules, {'dialect_id': dialect_id})
        rules = cur.fetchall()

        for word,phoncode in phoncodemap.items():
            rules_applied = []
            if rules:
                phoncode, rules_applied = applyrules(phoncode, rules)
            cur.execute(cmd_select_corpus_id, {'corpus': corpus_label})
            r = cur.fetchone()
            corpus_id = r['id']
            cur.execute(cmd_select_word_id, {'word': word, 'corpus_id': corpus_id})
            r = cur.fetchone()
            word_id = r['id']
            try:
                cur.execute(cmd_insert_phonology, (phoncode,))
            except sqlite3.IntegrityError:
                # Phonology already exists in database.
                pass
            cur.execute(cmd_select_phonology, {'phoncode': phoncode})
            r = cur.fetchone();
            phoncode_id = r['id']
            word_has_phonology_values.append((word_id,dialect_id,phoncode_id))
            dialect_has_phonology_values.append((dialect_id,phoncode_id))

            if rules_applied:
                n = len(rules_applied)
                phon_has_rules_values = zip([dialect_id]*n,[word_id]*n,[phoncode_id]*n,rules_applied)
                cur.executemany(cmd_insert_phonology_has_rule, phon_has_rules_values)

#            homo = [w for w,p in phoncodemap.items() if p == phoncode and w is not word]
#            cur.execute(cmd_select_word_ids, (corpus_id, ','.join(homo)))
#            r = cur.fetchall()
#            homo_id = [h['id'] for h in r]
#            if homo:
#                homophones.extend(zip([corpus_id]*len(r),[word_id]*len(r),homo_id))

        for row in word_has_phonology_values:
            try:
                cur.execute(cmd_insert_word_has_phonology, row)
            except sqlite3.IntegrityError:
                # The phonology is the same in multiple dialects.
                pass

        for row in dialect_has_phonology_values:
            try:
                cur.execute(cmd_insert_dialect_has_phonology, row)
            except sqlite3.IntegrityError:
                # The phonology is homophonic or the same in multiple dialects.
                pass

#        if homophones:
#            cur.executemany(cmd_insert_homo, homophones)

def phonology_has_phonemes(conn, update=False, verbose=False):
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
    cmd_insert = "INSERT INTO phonology_has_phoneme (phonology_id,phoneme_id,unit) VALUES (?,?,?);"
    values = []
    existing_phonology_id = []
    with conn:
        cur = conn.cursor()
        if not update:
            cur.execute("SELECT DISTINCT phonology_id FROM phonology_has_phoneme;")
            existing_phonology_id = [r['phonology_id'] for r in cur.fetchall()]

        cur.execute("SELECT id, phoneme FROM phoneme;")
        phoneme_to_id = dict([(r['phoneme'],r['id']) for r in cur.fetchall()])
        cur.execute("SELECT id, phoncode FROM phonology;")
        for r in cur.fetchall():
            # if update == True, existing_phonology_id is empty, so statement
            # always evaluates to True.
            if not r['id'] in existing_phonology_id:
                phoncode = r['phoncode']
                phonology_id = r['id']
                phoneme_ids = [phoneme_to_id[p] for p in phoncode]
                n = len(phoncode)
                if verbose:
                    print "-"*20
                    print '|'.join(["{x:>2}".format(x=s) for s in phoncode])
                    print '|'.join(["{x:02d}".format(x=d) for d in phoneme_ids])
                    print "phonology_id: " + str(phonology_id)
                row = zip([phonology_id]*n, phoneme_ids, range(n))
                values.extend(row)
        cur.executemany(cmd_insert, values)

def semantic_representation(conn, corpus_label, semmap):
    """
    Insert semantic representations for words in a corpus.

    # Insert representation for one word
    >>> aae.sql.insert.semantic_representation(conn, "3k", {"apple": [0,1,1,0]})

    # Insert representations for multiple words.
    >>> aae.sql.insert.semantic_representation(conn, "3k", {"apple": [0,1,1,0], "banana": [1,1,1,0]})

    """
    cmd_select_corpus_id = "SELECT id FROM corpus WHERE label=:corpus LIMIT 1;"
    cmd_select_word_id = "SELECT id FROM word WHERE word=:word AND corpus_id=:corpus_id LIMIT 1;"
    cmd_insert = "INSERT INTO semrep (corpus_id,word_id,unit,value) VALUES (?,?,?,?);"
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
            n = len(representation)
            values = zip([corpus_id]*n,[word_id]*n,range(n),representation)
            cur.executemany(cmd_insert, values)

def orthography(conn, corpus_label, orthcodemap):
    """
    Insert orthographic transcription code for words within a dialect.

    # Insert orthcode for one word
    >>> aae.sql.insert.orthography(conn, "3k", "orthogonal", {"fawn": "__fan_____"})

    # Insert orthcode for multiple words.
    >>> aae.sql.insert.orthography(conn, "3k", "orthogonal", {"fawn": "__fan_____", "foul": "__fWl_____"})

    """
    cmd_select_corpus_id = "SELECT id FROM corpus WHERE label=:corpus LIMIT 1;"
    cmd_select_word_id = "SELECT id FROM word WHERE word=:word AND corpus_id=:corpus_id LIMIT 1;"
    cmd_insert = "INSERT INTO orthography (corpus_id,word_id,orthcode) VALUES (?,?,?);"
    values = []
    with conn:
        cur = conn.cursor()
        for word,orthcode in orthcodemap.items():
            cur.execute(cmd_select_corpus_id, {'corpus': corpus_label})
            r = cur.fetchone()
            corpus_id = r['id']
            cur.execute(cmd_select_word_id, {'word': word, 'corpus_id': corpus_id})
            r = cur.fetchone()
            word_id = r['id']
            values.append((corpus_id,word_id,orthcode))
        cur.executemany(cmd_insert, values)

def graphemes(conn, graphemes):
    """
    Insert word into database and associate with a corpus.

    # Insert one phoneme. [] are required.
    >>> aae.sql.insert.graphemes(conn, ["^"])

    # Insert multiple rules.
    >>> aae.sql.insert.graphemes(conn, ["^", "a"])

    """
    cmd_insert = "INSERT INTO grapheme (grapheme) VALUES (?);"
    with conn:
        cur = conn.cursor()
        if isinstance(graphemes, list):
            cur.executemany(cmd_insert, graphemes)
        else:
            cur.execute(cmd_insert, graphemes)

def orthography_has_graphemes(conn, update=False, verbose=False):
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
    cmd_insert = "INSERT INTO orthography_has_grapheme (orthography_id,grapheme_id,unit) VALUES (?,?,?);"
    values = []
    existing_phonology_id = []
    with conn:
        cur = conn.cursor()
        if not update:
            cur.execute("SELECT DISTINCT orthography_id FROM orthography_has_grapheme;")
            existing_orthography_id = [r['orthography_id'] for r in cur.fetchall()]

        cur.execute("SELECT id, grapheme FROM grapheme;")
        grapheme_to_id = dict([(r['grapheme'],r['id']) for r in cur.fetchall()])
        cur.execute("SELECT id, orthcode FROM orthography;")
        for r in cur.fetchall():
            # if update == True, existing_phonology_id is empty, so statement
            # always evaluates to True.
            if not r['id'] in existing_orthography_id:
                orthcode = r['orthcode']
                orthography_id = r['id']
                grapheme_ids = [grapheme_to_id[g] for g in orthcode]
                n = len(orthcode)
                if verbose:
                    print "-"*20
                    print '|'.join(["{x:>2}".format(x=s) for s in orthcode])
                    print '|'.join(["{x:02d}".format(x=d) for d in grapheme_ids])
                    print "orthography_id: " + str(orthography_id)
                row = zip([orthography_id]*n, grapheme_ids, range(n))
                values.extend(row)
        cur.executemany(cmd_insert, values)

def grapheme_representation(conn, alphabet, phonmap, verbose=False):
    """
    Insert accent into database.

    # Register a accent
    >>> aae.sql.insert.corpus(conn, "standard")

    # Register a accent with a description
    >>> aae.sql.insert.corpus(conn, "mild", "Only vowels differ from standard.")
    >>> aae.sql.insert.corpus(conn, "strong", "Both vowels and consonants differ from standard.")

    """
    cmd_insert = "INSERT INTO orthrep (alphabet_id,grapheme_id,unit,value) VALUES (?,?,?,?);"
    cmd_select_alphabet_id = "SELECT id FROM alphabet WHERE label=:alphabet LIMIT 1;"
    cmd_select_grapheme_id = "SELECT id FROM grapheme WHERE grapheme=:grapheme LIMIT 1;"
    values = []
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_alphabet_id, {'alphabet': alphabet})
        r = cur.fetchone()
        alphabet_id = r['id']
        for grapheme,representation in phonmap.items():
            cur.execute(cmd_select_grapheme_id, {'grapheme': grapheme})
            r = cur.fetchone()
            if r is None:
                if verbose:
                    print "Adding grapheme `"+grapheme+"` to database."
                graphemes(conn, grapheme)
                cur.execute(cmd_select_grapheme_id, {'grapheme': grapheme})
                r = cur.fetchone()

            grapheme_id = r['id']
            n = len(representation)
            values.extend(zip([alphabet_id]*n, [grapheme_id]*n, range(n), representation))
        cur.executemany(cmd_insert, values)

def alphabet(conn, label, description='', orthmap={}):
    """
    Insert alphabet into database.

    # Register an alphabet
    >>> aae.sql.insert.alphabet(conn, "orthogonal", orthmap=ORTH_MAP)

    # Register an alphabet with a description
    >>> aae.sql.insert.alphabet(conn, "orthogonal", description="No inherent similarity among graphemes.", orthmap=ORTH_MAP)

    """
    cmd_insert = "INSERT INTO alphabet (label, description) VALUES (:label,:desc)"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_insert, {'label': label, 'desc': description})

    if orthmap:
        grapheme_representation(conn, label, orthmap)

def sample(conn, corpus, dialect_root, dialect_alt, accent, alphabet, n=[], ndiff=[], nhomo_root=[], use_frequency=False, list_id=[], list_stim=[]):
    cmd_select_corpus_id = "SELECT id FROM corpus WHERE label=:corpus LIMIT 1;"
    cmd_select_dialect_id = "SELECT id FROM dialect WHERE label=:dialect LIMIT 1;"
    cmd_select_accent_id = "SELECT id FROM accent WHERE label=:accent LIMIT 1;"
    cmd_select_alphabet_id = "SELECT id FROM alphabet WHERE label=:alphabet LIMIT 1;"
    cmd_select_word_id = "SELECT id FROM word WHERE word=:word AND corpus_id=:corpus_id LIMIT 1;"
    cmd_select_word_by_phon = "SELECT word_id FROM word_has_phonology WHERE phonology_id=:phon AND dialect_id=:dialect;"
    #cmd_select_homo_id = "SELECT word_id,homo_id FROM homophones WHERE corpus_id=:corpus;"
    cmd_select_phonology= ("SELECT phonology_id "
                            "FROM word_has_phonology "
                            "WHERE dialect_id=:dialect AND word_id=:word;")
    cmd_select_orthography = ("SELECT id "
                            "FROM orthography "
                            "WHERE word_id=:word ;")
    cmd_select_homophone = ("SELECT phonology_id, count(word_id) as word_count "
                            "FROM word_has_phonology "
                            "WHERE dialect_id=:dialect "
                            "GROUP BY phonology_id "
                            "HAVING word_count>1;")
    cmd_select_same = ("SELECT word_id "
                       "FROM word_has_phonology "
                       "GROUP BY word_id "
                       "HAVING min(phonology_id)=max(phonology_id);")
    cmd_select_diff = ("SELECT word_id "
                       "FROM word_has_phonology "
                       "GROUP BY word_id "
                       "HAVING min(phonology_id)!=max(phonology_id);")
    cmd_insert_sample = "INSERT INTO sample (dialect_root_id,dialect_alt_id,accent_id,alphabet_id,corpus_id,n,n_root_homophones,n_root_homophonic_words,n_alt_homophones,n_alt_homophonic_words,n_diff_root_alt,p_rule_applied,use_frequency) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);"
    cmd_insert_sample_has_example= "INSERT INTO sample_has_example (sample_id,word_id,phonology_id,orthography_id,dialect_id) VALUES (?,?,?,?,?);"

    def generate(conn, corpus_id, root_id, alt_id, n, ndiff, nhomo_root):
        with conn:
            cur = conn.cursor()
            cur.execute(cmd_select_same, {'root': root_id, 'alt': alt_id})
            SAME = cur.fetchall()
            cur.execute(cmd_select_diff, {'root': root_id, 'alt': alt_id})
            DIFF = cur.fetchall()
            cur.execute(cmd_select_homophone, {'dialect': root_id})
            HOMO = cur.fetchall()

        nsame = n - ndiff
        random.shuffle(SAME)
        random.shuffle(DIFF)
        random.shuffle(HOMO)

        all_word_id_same = [r['word_id'] for r in SAME]
        all_word_id_diff = [r['word_id'] for r in DIFF]

        examples = []
        homo_root_id_set = [r['phonology_id'] for r in HOMO]
        word_id_set = []
        for h in HOMO[:nhomo_root]:
            phon_id_root = h['phonology_id']
            word_count = h['word_count']
            cur.execute(cmd_select_word_by_phon, {'phon': phon_id_root, 'dialect': root_id})
            for R in cur.fetchall():
                word_id = R['word_id']
                if word_id not in examples:
                    word_id_set.append(word_id)
                    cur.execute(cmd_select_orthography, {'word': word_id})
                    r = cur.fetchone()
                    orth_id = r['id']
                    cur.execute(cmd_select_phonology, {'dialect': alt_id, 'word': word_id})
                    r = cur.fetchone()
                    phon_id_alt = r['phonology_id']
                    examples.append((word_id,phon_id_root,orth_id,root_id))
                    examples.append((word_id,phon_id_alt,orth_id,alt_id))

        examples_nsame = sum([1 for w in word_id_set if w in all_word_id_same])
        examples_ndiff = sum([1 for w in word_id_set if w in all_word_id_diff])

        while examples_nsame < nsame:
            r = SAME.pop()
            word_id = r['word_id']
            if word_id not in word_id_set:
                word_id_set.append(word_id)
                cur.execute(cmd_select_orthography, {'word': word_id})
                r = cur.fetchone()
                orth_id = r['id']
                cur.execute(cmd_select_phonology, {'dialect': root_id, 'word': word_id})
                r = cur.fetchone()
                phon_id_root = r['phonology_id']
                if phon_id_root in homo_root_id_set:
                    continue
                cur.execute(cmd_select_phonology, {'dialect': alt_id, 'word': word_id})
                r = cur.fetchone()
                phon_id_alt = r['phonology_id']

                examples.append((word_id,phon_id_root,orth_id,root_id))
                examples.append((word_id,phon_id_alt,orth_id,alt_id))
                examples_nsame += 1

        while examples_ndiff < ndiff:
            r = DIFF.pop()
            word_id = r['word_id']
            if word_id not in word_id_set:
                word_id_set.append(word_id)
                cur.execute(cmd_select_orthography, {'word': word_id})
                r = cur.fetchone()
                orth_id = r['id']
                cur.execute(cmd_select_phonology, {'dialect': root_id, 'word': word_id})
                r = cur.fetchone()
                phon_id_root = r['phonology_id']
                if phon_id_root in homo_root_id_set:
                    continue
                cur.execute(cmd_select_phonology, {'dialect': alt_id, 'word': word_id})
                r = cur.fetchone()
                phon_id_alt = r['phonology_id']

                examples.append((word_id,phon_id_root,orth_id,root_id))
                examples.append((word_id,phon_id_alt,orth_id,alt_id))
                examples_ndiff += 1

        return examples
        # end generate

    examples = []
    values = []

    if list_id and list_stim:
        error("list_id and list_stim cannot both be defined.");
    else:
        if list_id:
            GIVEN_SAMPLE = list_id
            GIVEN_AS_ID = True
            n = len(GIVEN_SAMPLE)
        elif list_stim:
            GIVEN_SAMPLE = list_stim
            GIVEN_AS_ID = False
            n = len(GIVEN_SAMPLE)
        else:
            GIVEN_SAMPLE = []
            GIVEN_AS_ID = False

    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_dialect_id, {'dialect': dialect_root})
        r = cur.fetchone()
        if r is None:
            print "Error: {} is not a recognized dialect label (dialect_root).".format(dialect_root)
        dialect_root_id = r['id']

        cur.execute(cmd_select_dialect_id, {'dialect': dialect_alt})
        r = cur.fetchone()
        if r is None:
            print "Error: {} is not a recognized dialect label (dialect_alt).".format(dialect_alt)
        dialect_alt_id = r['id']

        cur.execute(cmd_select_corpus_id, {'corpus': corpus})
        r = cur.fetchone()
        if r is None:
            print "Error: {} is not a recognized corpus label.".format(corpus)
        corpus_id = r['id']

        cur.execute(cmd_select_accent_id, {'accent': accent})
        r = cur.fetchone()
        if r is None:
            print "Error: {} is not a recognized accent label.".format(corpus)
        accent_id = r['id']

        cur.execute(cmd_select_alphabet_id, {'alphabet': alphabet})
        r = cur.fetchone()
        if r is None:
            print "Error: {} is not a recognized alphabet label.".format(corpus)
        alphabet_id = r['id']

    if not GIVEN_SAMPLE:
        examples = generate(conn, corpus_id, dialect_root_id, dialect_alt_id, n, ndiff, nhomo_root)

    else:
        with conn:
            cur = conn.cursor()
            for w in list_stim:
                cur.execute(cmd_select_word_id, {'word': w, 'corpus_id': corpus_id})
                r = cur.fetchone()
                word_id = r['id']
                cur.execute(cmd_select_phonology, {'dialect': dialect_root_id, 'word': word_id})
                r = cur.fetchone()
                phon_id_root = r['phonology_id']
                cur.execute(cmd_select_phonology, {'dialect': dialect_alt_id, 'word': word_id})
                r = cur.fetchone()
                phon_id_alt = r['phonology_id']
                cur.execute(cmd_select_orthography, {'word': word_id})
                r = cur.fetchone()
                orth_id = r['id']
                examples.append((word_id,phon_id_root,orth_id,dialect_root_id))
                examples.append((word_id,phon_id_alt,orth_id,dialect_alt_id))

    ndiff_samp = 0
    for i,j in zip(range(0,len(examples),2),range(1,len(examples),2)):
        if examples[i][1] != examples[j][1]:
            ndiff_samp += 1

    phon_id_root = [x[1] for i,x in enumerate(examples) if x[3]==dialect_root_id]
    phon_id_alt = [x[1] for i,x in enumerate(examples) if x[3]==dialect_alt_id]

    counts = [phon_id_root.count(x) for x in set(phon_id_root) if phon_id_root.count(x) > 1]
    nhomo_root_samp = len(counts)
    nhomowords_root_samp = sum(counts)

    counts = [phon_id_alt.count(x) for x in set(phon_id_alt) if phon_id_alt.count(x) > 1]
    nhomo_alt_samp = len(counts)
    nhomowords_alt_samp = sum(counts)

    with conn:
        cur = conn.cursor()
        print dialect_root_id,dialect_alt_id,accent_id,alphabet_id,corpus_id,n,nhomo_root_samp,nhomowords_root_samp,nhomo_alt_samp,nhomowords_alt_samp,ndiff_samp,1.0,int(use_frequency)
        cur.execute(cmd_insert_sample, (dialect_root_id,dialect_alt_id,accent_id,alphabet_id,corpus_id,n,nhomo_root_samp,nhomowords_root_samp,nhomo_alt_samp,nhomowords_alt_samp,ndiff_samp,1.0,int(use_frequency)))
        cur.execute("SELECT id FROM sample WHERE rowid=:rowid;", {'rowid': cur.lastrowid})
        r = cur.fetchone()
        sample_id = r['id']
        values = [(sample_id,x[0],x[1],x[2],x[3]) for x in examples]
        cur.executemany(cmd_insert_sample_has_example, values)

    return sample_id

def childsample(conn, parent_sample_id, p_rule_applied):
    cmd_select_sample = "SELECT dialect_root_id,dialect_alt_id,accent_id,alphabet_id,corpus_id,n,n_root_homophones,n_root_homophonic_words,n_diff_root_alt,use_frequency FROM sample WHERE id=:sample_id;"
    cmd_select_examples = "SELECT dialect_id,word_id,phonology_id,orthography_id FROM sample_has_example WHERE sample_id=:sample_id;"
    cmd_select_phonology= ("SELECT phonology_id "
                            "FROM word_has_phonology "
                            "WHERE dialect_id=:dialect AND word_id=:word;")
    cmd_insert_sample = "INSERT INTO sample (dialect_root_id,dialect_alt_id,accent_id,alphabet_id,corpus_id,n,n_root_homophones,n_root_homophonic_words,n_alt_homophones,n_alt_homophonic_words,n_diff_root_alt,p_rule_applied,use_frequency,child_of) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
    cmd_insert_sample_has_example= "INSERT INTO sample_has_example (sample_id,word_id,phonology_id,orthography_id,dialect_id) VALUES (?,?,?,?,?);"

    # alias
    child_of = parent_sample_id
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_sample, {"sample_id": parent_sample_id})
        r = cur.fetchone()
        dialect_root_id = r['dialect_root_id']
        dialect_alt_id = r['dialect_alt_id']
        accent_id = r['accent_id']
        alphabet_id = r['alphabet_id']
        corpus_id = r['corpus_id']
        n = r['n']
        nhomo_root_samp = r['n_root_homophones']
        nhomowords_root_samp = r['n_root_homophonic_words']
        n_diff_parent = r['n_diff_root_alt']
        use_frequency = r['use_frequency']
        ndiff = int(n_diff_parent * p_rule_applied) # this truncates any decimal information and returns an integer
        n_to_change = n_diff_parent-ndiff

        cur.execute(cmd_select_examples, {"sample_id": parent_sample_id})
        examples = []
        n_made_same = 0
        for r in cur.fetchall():
            dialect_id = r['dialect_id']
            word_id = r['word_id']
            phonology_id = r['phonology_id']
            orthography_id = r['orthography_id']
            # If the dialect is the "changed" alternate form, and we haven't
            # already undone the number of changes we planned to, then pull the
            # root phonology and overwrite the variable.
            if dialect_id == dialect_alt_id and n_made_same < n_to_change:
                cur.execute(cmd_select_phonology,{"dialect": dialect_root_id, "word": word_id})
                p = cur.fetchone()
                phonology_id = p['phonology_id']
                n_made_same += 1

            examples.append( (word_id,phonology_id,orthography_id,dialect_id) )

    phon_id_alt = [x[1] for i,x in enumerate(examples) if x[3]==dialect_alt_id]
    counts = [phon_id_alt.count(x) for x in set(phon_id_alt) if phon_id_alt.count(x) > 1]
    nhomo_alt_samp = len(counts)
    nhomowords_alt_samp = sum(counts)

    with conn:
        cur = conn.cursor()
        cur.execute(cmd_insert_sample, (dialect_root_id,dialect_alt_id,accent_id,alphabet_id,corpus_id,n,nhomo_root_samp,nhomowords_root_samp,nhomo_alt_samp,nhomowords_alt_samp,ndiff,p_rule_applied,use_frequency,child_of))
        cur.execute("SELECT id FROM sample WHERE rowid=:rowid;", {'rowid': cur.lastrowid})
        r = cur.fetchone()
        sample_id = r['id']
        values = [(sample_id,x[0],x[1],x[2],x[3]) for x in examples]
        cur.executemany(cmd_insert_sample_has_example, values)

    return sample_id
