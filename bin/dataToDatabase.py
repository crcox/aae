#!/usr/bin/env python
import argparse
import os
import pkg_resources
import sqlite3
import json
import aae.sql.select
import aae.sql.insert
import aae.utils
# Reminders about Lens example files:
# - Files begin with a header that set defaults.
# - The header is terminated with a semi-colon.
# - Each ``trial'' can be composed of many events.
# - In this model, there are three events:
#   1. Presentation
#   2. Settling---letting the recurrent dynamics happen
#   3. Evaluation---the targets are presented, and error assessed.
# - Each event lasts two ticks, so a full trial is 6 ticks.
resource_package = 'aae'

p = argparse.ArgumentParser()
p.add_argument('-D','--database',type=str,default='')
p.add_argument('config')
p.add_argument('data')
p.add_argument('-o','--output',type=str,default='train.ex')
p.add_argument('-s','--sample_id',type=str,default=None)
args = p.parse_args()

if args.database:
    DATABASE = args.database
else:
    DATABASE = pkg_resources.resource_filename(resource_package,'database/main.db')

PATH_TO_JSON = args.config
PATH_TO_DATA = args.data

# Load instructions
with open(PATH_TO_JSON,'r') as f:
    CONFIG = json.load(f)

exp_fields = [
    "sample_id",
    "netname",
    "intervals",
    "ticksPerInterval",
    "netType",
    "context",
    "disambiguateHomophones",
    "frequency",
    "warmstart",
    "testGroupCrit",
    "targetRadius",
    "UpdatesPerCall",
    "weightDecay",
    "batchSize",
    "learningRate",
    "momentum",
    "reportInterval",
    "SpikeThreshold",
    "SpikeThresholdStepSize",
    "TestEpoch",
    "ErrorCriterion",
    "TrainingMethod",
    "iteration"
]
EXPERIMENT_INFO = {k:v for k,v in CONFIG.items() if k in exp_fields}

SAMPLE_ID = EXPERIMENT_INFO['sample_id']

# Load sample data
cmd_select_corpus_id = "SELECT corpus_id FROM sample WHERE id=:sample_id;"
cmd_select_word_id = "SELECT id FROM word WHERE word=:word AND corpus_id=:corpus_id;"
cmd_select_words = "SELECT word.id as id,word FROM word JOIN sample_has_example ON word.id=sample_has_example.word_id WHERE sample_has_example.sample_id=:sample_id;"
cmd_insert_performance = "INSERT INTO performance (experiment_id,sample_id,word_id,dialect_id,update_count,inputlayer,outputlayer,hit,miss,falsealarm,correctrejection) VALUES (?,?,?,?,?,?,?,?,?,?,?);"
cmd_insert_experiment = "INSERT INTO experiment (sample_id,netname,intervals,ticksPerInterval,netType,context,disambiguateHomophones,frequency,warmstart,testGroupCrit,targetRadius,UpdatesPerCall,weightDecay,batchSize,learningRate,momentum,reportInterval,SpikeThreshold,SpikeThresholdStepSize,TestEpoch,ErrorCriterion,TrainingMethod,iteration) VALUES (:sample_id,:netname,:intervals,:ticksPerInterval,:netType,:context,:disambiguateHomophones,:frequency,:warmstart,:testGroupCrit,:targetRadius,:UpdatesPerCall,:weightDecay,:batchSize,:learningRate,:momentum,:reportInterval,:SpikeThreshold,:SpikeThresholdStepSize,:TestEpoch,:ErrorCriterion,:TrainingMethod,:iteration);"
conn = sqlite3.connect(DATABASE)
conn.row_factory = sqlite3.Row
with conn:
    cur = conn.cursor()
    cur.execute(cmd_insert_experiment, EXPERIMENT_INFO)
    cur.execute("SELECT id FROM experiment WHERE rowid=:rowid;", {'rowid': cur.lastrowid})
    r = cur.fetchone()
    EXPERIMENT_ID = r['id']

with conn:
    cur = conn.cursor()
    cur.execute(cmd_select_corpus_id, {'sample_id': SAMPLE_ID})
    r = cur.fetchone()
    CORPUS_ID = r['corpus_id']

with conn:
    cur = conn.cursor()
    cur.execute(cmd_select_words, {'sample_id': SAMPLE_ID})
    R = cur.fetchall()

Word_ID_Lookup = {r['word']:r['id'] for r in R}


EXPERIMENT_DATA = []
print "Loading data..."
with open(PATH_TO_DATA,'r') as DATA:
    dialect_previous = ''
    for line in DATA:
        row = line.strip().split(',')
        update_count = row[0]
        inputlayer = row[6]
        outputlayer = row[2].replace("Output","").lower()
        if dialect_previous != row[4]:
            dialect_id = aae.sql.select.dialect_id(conn, row[4])

        dialect_previous = row[4]
        word_id = Word_ID_Lookup[row[5]]

        misses = row[8]
        falsepositives = row[9]
        hits = row[10]
        truenegatives = row[11]

        data_row = (
            EXPERIMENT_ID,
            SAMPLE_ID,
            word_id,
            dialect_id,
            update_count,
            inputlayer,
            outputlayer,
            hits,
            misses,
            falsepositives,
            truenegatives
        )
        EXPERIMENT_DATA.append(data_row)

print "Writing database..."
with conn:
    cur = conn.cursor()
    cur.executemany(cmd_insert_performance, EXPERIMENT_DATA)
