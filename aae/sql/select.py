from __future__ import absolute_import, division, print_function
import operator
import copy
def dialect_id(conn, dialect):
    cmd_select_dialect_id = "SELECT id FROM dialect WHERE label=:dialect;"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_dialect_id, {'dialect': dialect})
        r = cur.fetchone()

    return r['id']

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
    cmd_select_phonrep= ("SELECT A.phoneme_id,A.unit,B.unit,value "
                         "FROM phonology_has_phoneme as A "
                         "INNER JOIN phonrep as B "
                         "ON A.phoneme_id = B.phoneme_id "
                         "WHERE A.phonology_id=:phonology_id AND B.accent_id=:accent_id;")
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_phonrep, {'phonology_id':phonology_id,'accent_id':accent_id})
        R = cur.fetchall()
        # this sorts by phonemes, and then representational units within each
        # phoneme.
        R.sort(key=operator.itemgetter(1,2))
        rep = [list() for i in range(10)]
        for r in R:
            rep[r[1]].append(r['value'])

    return rep

def orthography(conn, orthography_id):
    cmd_select_orthography = "SELECT orthcode FROM orthography WHERE id=:orthography_id;"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_orthography, {'orthography_id': orthography_id})
        r = cur.fetchone()

    return r['orthcode']

def orthrep(conn, orthography_id, alphabet_id):
    cmd_select_orthrep= ("SELECT A.grapheme_id,A.unit,B.unit,value "
                         "FROM orthography_has_grapheme as A "
                         "INNER JOIN orthrep as B "
                         "ON A.grapheme_id = B.grapheme_id "
                         "WHERE A.orthography_id=:orthography_id AND b.alphabet_id=:alphabet_id;")
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_orthrep, {'orthography_id':orthography_id,'alphabet_id':alphabet_id})
        R = cur.fetchall()
        # this sorts by graphemes, and then representational units within each
        # grapheme.
        R.sort(key=operator.itemgetter(1,2))
        rep = [list() for i in range(14)]
        for r in R:
            rep[r[1]].append(r['value'])

    return rep

def semrep(conn, word_id):
    cmd_select_semrep = "SELECT unit,value FROM semrep WHERE word_id=:word_id;"
    with conn:
        cur = conn.cursor()
        cur.execute(cmd_select_semrep, {'word_id':word_id})
        R = cur.fetchall()
        R.sort(key=operator.itemgetter(0))
        rep = [r['value'] for r in R]

    return rep

def sample(conn, sample_id, accent_id=None):
    cmd_select_sample = "SELECT accent_id,alphabet_id,corpus_id,dialect_root_id,dialect_alt_id,use_frequency FROM sample WHERE id=:sample_id;"
    cmd_select_examples = "SELECT word_id,phonology_id,orthography_id,dialect_id FROM sample_has_example WHERE sample_id=:sample_id;"
    cmd_select_word = "SELECT word FROM word WHERE id=:word_id";
    cmd_select_orthography = "SELECT orthcode FROM orthography WHERE id=:orthography_id;"
    cmd_select_phonology = "SELECT phoncode FROM phonology WHERE id=:phonology_id;"
    cmd_select_dialect = "SELECT label FROM dialect WHERE id=:dialect_id";
    cmd_select_phonology_has_rule = "SELECT rule_id FROM phonology_has_rule WHERE phonology_id=:phonology_id";
    cmd_select_example_data = "SELECT dialect_id,word_id,word,frequency,orthography_id,orthcode,phonology_id,phoncode,dialect FROM example_data WHERE sample_id=:sample_id;"
    cmd_select_orthography_representation = "SELECT orthography_id, grapheme_id,grapheme_unit,orthrep_unit,orthrep_value FROM orthography_representation WHERE sample_id=:sample_id AND orthography_id=:orthography_id AND dialect_id=:dialect_id AND alphabet_id=:alphabet_id AND word_id=:word_id ORDER BY grapheme_unit,orthrep_unit;"
    cmd_select_phonology_representation = "SELECT phonology_id, phoneme_id,phoneme_unit,phonrep_unit,phonrep_value FROM phonology_representation WHERE sample_id=:sample_id AND phonology_id=:phonology_id AND dialect_id=:dialect_id AND accent_id=:accent_id AND word_id=:word_id ORDER BY phoneme_unit,phonrep_unit;"
    cmd_select_semantic_representation = "SELECT word_id,semrep_unit,semrep_value FROM semantic_representation WHERE sample_id=:sample_id AND word_id=:word_id AND dialect_id=:dialect_id ORDER BY semrep_unit;"
    example_prototype = {
            "rule_id": 0,
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
        r = cur.fetchone()
        alphabet_id = r['alphabet_id']
        if not accent_id:
            accent_id = r['accent_id']
        corpus_id = r['corpus_id']
        dialect_root_id = r['dialect_root_id']
        dialect_alt_id = r['dialect_alt_id']
        use_frequency = r['use_frequency']

        cur.execute("SELECT id,label FROM rule;")
        rule_dict = {r['id']:r['label'] for r in cur.fetchall()}

        sample = {}

        # Load all sample data into memory at once (should be fine...)
        cur.execute(cmd_select_example_data, {"sample_id": sample_id})
        SAMPLE_TBL = cur.fetchall()
        for R in SAMPLE_TBL:
# DICT
#            dialect = R['dialect']
#            word = R['word']
#            if not dialect in sample:
#                sample[dialect] = {}
#            if not word in sample[dialect]:
#                sample[dialect][word] = {}
# LIST
            if not R['dialect'] in sample:
                sample[R['dialect']] = []

            RDICT = {}
            RDICT['dialect'] = R['dialect']
            RDICT['word'] = R['word']
            RDICT['freq'] = R['frequency']
            RDICT['orth_code'] = R['orthcode']
            RDICT['phon_code'] = R['phoncode']

            WHERE = {'sample_id': sample_id, 'word_id':R['word_id'], 'dialect_id': R['dialect_id'], 'orthography_id': R['orthography_id'], 'alphabet_id': alphabet_id}
            cur.execute(cmd_select_orthography_representation, WHERE)
            x = []
            for r in cur.fetchall():
                try:
                    x[r['grapheme_unit']].append(r['orthrep_value'])
                except IndexError:
                    for i in range(len(x),r['grapheme_unit']+1):
                        x.append([])
                    x[r['grapheme_unit']].append(r['orthrep_value'])
            RDICT['orth'] = x

            WHERE = {'sample_id': sample_id, 'word_id':R['word_id'], 'dialect_id': R['dialect_id'], 'phonology_id': R['phonology_id'], 'accent_id': accent_id}
            cur.execute(cmd_select_phonology_representation, WHERE)
            x = []
            for r in cur.fetchall():
                try:
                    x[r['phoneme_unit']].append(r['phonrep_value'])
                except IndexError:
                    for i in range(len(x),r['phoneme_unit']+1):
                        x.append([])
                    x[r['phoneme_unit']].append(r['phonrep_value'])
            RDICT['phon'] = x

            WHERE = {'sample_id': sample_id, 'dialect_id':R['dialect_id'], 'word_id': R['word_id']}
            cur.execute(cmd_select_semantic_representation, WHERE)
            RDICT['sem'] = [r['semrep_value'] for r in cur.fetchall()]
            sample[R['dialect']].append(dict(RDICT))

    return sample
