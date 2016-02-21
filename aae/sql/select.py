import operator
def phonology(conn, phonology_id):
    cmd_select_phonology = "SELECT phoncode FROM phonology WHERE id=:phonology_id;"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_phonology, {'phonology_id': phonology_id})
        r = cur.fetchone()

    return r['phoncode']

def word_has_phonology(conn, word_id, dialect_id=[]):
    cmd_select_phonology = "SELECT id,phoncode FROM phonology WHERE id=:phonology_id;"
    if dialect_id:
        cmd_select_word_has_phonology = "SELECT phonology_id FROM word_has_phonology WHERE word_id=:word_id AND dialect_id=:dialect_id;"
    else:
        cmd_select_word_has_phonology = "SELECT phonology_id FROM word_has_phonology WHERE word_id=:word_id;"

    with conn:
        cur = conn.cursor()
        if dialect_id:
            cur.execute(cmd_select_word_has_phonology, {'word_id': word_id, 'dialect_id':dialect_id})
        else:
            cur.execute(cmd_select_word_has_phonology, {'word_id': word_id})

        phonlist = []
        for R in cur.fetchall():
            phonology_id = R['phonology_id']
            cur.exectute(cmd_select_phonology,{'phonology_id': 'phonology_id'})
            r = cur.fetchone();
            phonlist.append( (r['id'], r['phoncode']) )

    return phonlist

def phonrep(conn, phonology_id, accent_id):
    cmd_select_phonrep= "SELECT phoneme_id,A.unit,B.unit,value FROM phonology_has_phoneme as A INNER JOIN phonrep as B ON A.phoneme_id = B.phoneme_id WHERE A.id=:phonology_id AND b.accent_id=:accent_id;"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_phonrep, {'phonology_id':phonology_id,'accent_id':accent_id})
        R = cur.fetchall()
        # this sorts by phonemes, and then representational units within each
        # phoneme.
        R.sort(key=operator.itemgetter(1,2))
        rep = [list() for i in range(10)]
        for r in R:
            rep[r['A.unit']].append(r['value'])

    return rep

def orthography(conn, orthography_id):
    cmd_select_orthography = "SELECT orthcode FROM orthography WHERE id=:orthography_id;"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_orthography, {'orthography_id': orthography_id})
        r = cur.fetchone()

    return r['orthcode']

def orthrep(conn, orthography_id, alphabet_id):
    cmd_select_phonrep= "SELECT grapheme_id,A.unit,B.unit,value FROM orthography_has_grapheme as A INNER JOIN orthrep as B ON A.grapheme_id = B.grapheme_id WHERE A.id=:orthography_id AND b.alphabet_id=:alphabet_id;"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_orthrep, {'orthography_id':orthography_id,'alphabet_id':alphabet_id})
        R = cur.fetchall()
        # this sorts by graphemes, and then representational units within each
        # grapheme.
        R.sort(key=operator.itemgetter(1,2))
        rep = [list() for i in range(14)]
        for r in R:
            rep[r['A.unit']].append(r['value'])

    return rep

def semrep(conn, word_id):
    cmd_select_semrep = "SELECT unit,value FROM semrep WHERE word_id=:word_id;"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_semrep, {'word_id':word_id})
        R = cur.fetchall()
        R.sort(key=operator.itemgetter(0))
        rep = [list() for i in range(14)]
        for r in R:
            rep[r['unit']].append(r['value'])

def sample(conn, sample_id):
    cmd_select_sample = "SELECT accent_id,alphabet_id,corpus_id,dialect_root_id,dialect_alt_id,use_frequency FROM sample WHERE id=:sample_id;"
    cmd_select_examples = "SELECT word_id,phonology_id,orthography_id,dialect_id FROM sample_has_examples WHERE sample_id=:sample_id;"
    cmd_select_word = "SELECT word FROM word WHERE id=:word_id";
    cmd_select_orthcode = "SELECT orthcode FROM orthography WHERE id=:orthography_id";
    cmd_select_phoncode = "SELECT phoncode FROM phonology WHERE id=:phonology_id";
    cmd_select_dialect = "SELECT label FROM dialect WHERE id=:dialect_id";

    example_prototype = {
            "devoiced": false,
            "consonant_cluster_reduction": false,
            "post_vocalic_reduction": false,
            "freq": 1,
            "orth_code": "______________",
            "orth": [],
            "phon_code": "__________",
            "phon": [list() for i in range(10)],
            "sem": []
        }

    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_sample, {"sample_id": sample_id})
        r = fetchone()
        alphabet_id = r['alphabet_id']
        accent_id = r['accent_id']
        corpus_id = r['corpus_id']
        dialect_root_id = r['dialect_root_id']
        dialect_alt_id = r['dialect_alt_id']
        use_frequency = r['use_frequency']

        cur.execute("SELECT id,label FROM rule;")
        rule_dict = {r['id']:r['label'] for r in cur.fetchall()}

        cur.execute(cmd_select_examples, {"sample_id": sample_id})
        for R in cur.fetchall():
            ex = example_prototype.deepcopy()
            dialect_id = R['dialect_id']
            orthography_id = R['orthography_id']
            phonology_id = R['phonology_id']
            semantic_id = R['semantic_id']
            word_id = R['word_id']

            if use_frequency:
                cur.execute("SELECT word,frequency FROM word WHERE id=:word_id;", {'word_id':word_id})
                r = cur.fetchone()
                word = r['word']
                freq = r['frequency']
            else:
                cur.execute(cmd_select_word, {'word_id': word_id});
                r = cur.fetchone()
                word = r['word']
                freq = 1

            cur.execute(cmd_select_orthography, {'orthography_id': orthography_id});
            r = cur.fetchone()
            orthcode = r['orthcode']

            cur.execute(cmd_select_phonology, {'phonology_id': phonology_id});
            r = cur.fetchone()
            phoncode = r['phoncode']

            cur.execute(cmd_select_dialect, {'dialect_id': word_id});
            r = cur.fetchone()
            dialect = r['label']

            cur.execute(cmd_select_rules, {'phonology_



  "word_id" INTEGER NOT NULL,
  "phonology_id" INTEGER NOT NULL,
  "orthography_id" INTEGER NOT NULL,
  "dialect_id" INTEGER NOT NULL,
