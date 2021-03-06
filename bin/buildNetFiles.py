#!/usr/bin/env python
from __future__ import absolute_import, division, print_function
import argparse
import os
import pkg_resources
import sqlite3
import json
import yaml
import aae.sql.select
import aae.utils
import lensapi.examples
import shutil
import os
import os.path
import timeit
import pickle
from mako.template import Template
# Reminders about Lens example files:
# - Files begin with a header that sets defaults.
# - The header is terminated with a semi-colon.
# - Each ``trial'' can be composed of many events.
# - In this model, there are three events:
#   1. Presentation
#   2. Settling---letting the recurrent dynamics happen
#   3. Evaluation---the targets are presented, and error assessed.
# - Each event lasts two ticks, so a full trial is 6 ticks.
resource_package = 'aae'

resource_path_network = os.path.join('template','network.mako')
network_template_string = pkg_resources.resource_string(resource_package, resource_path_network)
network_template = Template(network_template_string)

p = argparse.ArgumentParser()
p.add_argument('-D','--database',type=str,default='',help="Supply a path to a sqlite database file. Otherwise, the default database for your installation is used. See the README for how to install a default database.")
p.add_argument('config')
p.add_argument('-d','--dialect',type=str,nargs='+',default=[])
p.add_argument('-a','--accent',type=str,nargs='+',default=[])
p.add_argument('-o','--output',type=str,default='train.ex')
p.add_argument('-s','--sample_id',type=str,default=None)
p.add_argument('-S','--sequential',action="store_true")
p.add_argument('-J','--jitter',action="store_true")
p.add_argument('-t','--test_sample_id',type=str,default=None)
args = p.parse_args()

CACHE_SAMPLE = True
PATH_TO_JSON = args.config
OUTDIR = os.path.dirname(PATH_TO_JSON)
EX_DIR = os.path.join(OUTDIR, 'ex')
EX_FILENAME = os.path.join(EX_DIR, args.output)
TEST_EX_FILENAME = os.path.join(EX_DIR, 'test.ex')
IN_FILENAME = os.path.join(OUTDIR,'network.in')
TRAINSCRIPT_FILENAME = os.path.join(OUTDIR,'trainscript.tcl')

# Load instructions
with open(PATH_TO_JSON,'r') as f:
    CONFIG = json.load(f)

if args.database:
    DATABASE = args.database
elif 'database' in CONFIG:
    DATABASE = CONFIG['database']
else:
    DATABASE = pkg_resources.resource_filename(resource_package,'database/initial.db')

if args.jitter:
    JITTER = args.jitter
elif 'database' in CONFIG:
    JITTER = CONFIG['jitter']
else:
    JITTER = False

dbname = os.path.basename(DATABASE)

SEQUENTIAL = args.sequential

DIALECT_SUBSET = []
if args.dialect:
    DIALECT_SUBSET = args.dialect
else:
    if 'AAE' in CONFIG['TrainingMethod']:
        DIALECT_SUBSET = 'AAE'
    elif 'SAE' in CONFIG['TrainingMethod']:
        DIALECT_SUBSET = 'SAE'

ACCENT_ID = []
if args.accent:
    ACCENT_ID = args.accent
else:
    ACCENT_ID = CONFIG['accent']

trainscript_template_filename = "trainscript_{x:s}.mako".format(x=CONFIG['TrainingMethod'])
#if CONFIG['TrainingMethod'] == 'blocked':
#    trainscript_template_filename = "trainscript_{x:s}.mako".format(x='blocked')
#else:
#    trainscript_template_filename = "trainscript_{x:s}.mako".format(x='interleaved')

resource_path_trainscript = os.path.join('template',trainscript_template_filename)
trainscript_template_string = pkg_resources.resource_string(resource_package, resource_path_trainscript)
if str(trainscript_template_string.strip(),'utf-8') in [ 'trainscript_isolated.mako', 'trainscript_isolated_generalize.mako', 'trainscript_isolated_sequential.mako', 'trainscript_isolated_candide.mako']:
    trainscript_template_filename = str(trainscript_template_string.strip(),'utf-8')
    resource_path_trainscript = os.path.join('template',trainscript_template_filename)
    trainscript_template_string = pkg_resources.resource_string(resource_package, resource_path_trainscript)

trainscript_template = Template(trainscript_template_string)


if 'warmstart' in CONFIG and CONFIG['warmstart']:
    # NetInfoFile = 'network/{s:s}_warmstart.yaml'.format(s=CONFIG['NetworkArchitecture'])
    NetInfoFile = 'network/{s:s}.yaml'.format(s=CONFIG['NetworkArchitecture'])
else:
    NetInfoFile = 'network/{s:s}.yaml'.format(s=CONFIG['NetworkArchitecture'])

with pkg_resources.resource_stream('aae',NetInfoFile) as f:
    NETINFO = yaml.load(f)

for k in CONFIG.keys():
    NETINFO[k] = CONFIG[k]

if args.sample_id:
    SAMPLE_ID = args.sample_id
else:
    SAMPLE_ID = CONFIG['sample_id']

if args.test_sample_id:
    TEST_SAMPLE_ID = args.test_sample_id
elif 'test_sample_id' in CONFIG:
    TEST_SAMPLE_ID = CONFIG['test_sample_id']
else:
    TEST_SAMPLE_ID=SAMPLE_ID

FLAG_CONTEXT = CONFIG['context']

_tmp_list = []
for value in NETINFO['input'].values():
    if isinstance(value, dict):
        _tmp_list.extend(value.keys())
    else:
        _tmp_list.append(value)
ISET = sorted(list(set(_tmp_list)))

_tmp_list = []
for value in NETINFO['target'].values():
    if isinstance(value, dict):
        _tmp_list.extend(value.keys())
    else:
        _tmp_list.append(value)
TSET = sorted(list(set(_tmp_list)))

# Load sample data
start = timeit.default_timer()
SAMPLE_READ_FROM_CACHE = False
TEST_SAMPLE_READ_FROM_CACHE = False
if CACHE_SAMPLE:
    dbpath = os.path.dirname(DATABASE)
    cached_sample_filename = "{dbpath:s}/{dbname:s}_sampleID-{sampleID:04d}.pkl".format(dbpath=dbpath,dbname=dbname, sampleID=SAMPLE_ID)
    if os.path.isfile(cached_sample_filename):
        with open(cached_sample_filename,'rb') as f:
            SAMPLE = pickle.load(f)
        SAMPLE_READ_FROM_CACHE = True

    cached_sample_filename = "{dbpath:s}/{dbname:s}_sampleID-{sampleID:04d}.pkl".format(dbpath=dbpath,dbname=dbname, sampleID=TEST_SAMPLE_ID)
    if os.path.isfile(cached_sample_filename):
        with open(cached_sample_filename,'rb') as f:
            TEST_SAMPLE = pickle.load(f)
        TEST_SAMPLE_READ_FROM_CACHE = True

if not SAMPLE_READ_FROM_CACHE or not TEST_SAMPLE_READ_FROM_CACHE:
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    if not SAMPLE_READ_FROM_CACHE:
        SAMPLE = aae.sql.select.sample(conn, SAMPLE_ID, ACCENT_ID)
    if not TEST_SAMPLE_ID == SAMPLE_ID:
        if not TEST_SAMPLE_READ_FROM_CACHE:
            TEST_SAMPLE = aae.sql.select.sample(conn, TEST_SAMPLE_ID, ACCENT_ID)

    conn.close()

    if DIALECT_SUBSET:
        if not SAMPLE_READ_FROM_CACHE:
            SAMPLE = dict((dialectLabel, dialectExamples)
                    for dialectLabel,dialectExamples in SAMPLE.items()
                    if dialectLabel in DIALECT_SUBSET)

        if not TEST_SAMPLE_ID == SAMPLE_ID:
            if not TEST_SAMPLE_READ_FROM_CACHE:
                TEST_SAMPLE = dict((dialectLabel, dialectExamples)
                        for dialectLabel,dialectExamples in TEST_SAMPLE.items()
                        if dialectLabel in DIALECT_SUBSET)

    if TEST_SAMPLE_ID == SAMPLE_ID:
        if not SAMPLE_READ_FROM_CACHE:
            if JITTER:
                SAMPLE = aae.utils.jitter_representations(SAMPLE,12)
            SAMPLE = aae.utils.prune_representations(SAMPLE)
        TEST_SAMPLE = SAMPLE
    else:
        if not SAMPLE_READ_FROM_CACHE or not TEST_SAMPLE_READ_FROM_CACHE:
            if JITTER:
                [SAMPLE,TEST_SAMPLE] = aae.utils.jitter_representations(SAMPLE,12,TEST_SAMPLE)
            SAMPLE,TEST_SAMPLE = aae.utils.prune_representations([SAMPLE,TEST_SAMPLE])

    # Add "warmstart" data into the SAMPLE structures.
    if 'warmstart' in NETINFO and NETINFO['warmstart']:
        WarmCfg = NETINFO['warmstart']
        if all(True if k in WarmCfg.keys() else False for k in ['knn','ratio']):
            print("knn and ratio cannot both be specified.")
            raise ValueError
        if not SAMPLE_READ_FROM_CACHE:
            DIST = lensapi.examples.stimdist(SAMPLE,WarmCfg['type'],method=WarmCfg['distmethod'])
            try:
                SAMPLE = lensapi.examples.warmstart(SAMPLE,DIST,WarmCfg['type'],WarmCfg['name'],knn=WarmCfg['knn'])
            except KeyError:
                SAMPLE = lensapi.examples.warmstart(SAMPLE,DIST,WarmCfg['type'],WarmCfg['name'],ratio=WarmCfg['ratio'])

        if not TEST_SAMPLE_ID == SAMPLE_ID:
            if not TEST_SAMPLE_READ_FROM_CACHE:
                DIST = lensapi.examples.stimdist(TEST_SAMPLE,WarmCfg['type'],method=WarmCfg['distmethod'])
                try:
                    TEST_SAMPLE = lensapi.examples.warmstart(TEST_SAMPLE,DIST,WarmCfg['type'],WarmCfg['name'],knn=WarmCfg['knn'])
                except KeyError:
                    TEST_SAMPLE = lensapi.examples.warmstart(TEST_SAMPLE,DIST,WarmCfg['type'],WarmCfg['name'],ratio=WarmCfg['ratio'])

if CACHE_SAMPLE and not SAMPLE_READ_FROM_CACHE:
    dbpath = os.path.dirname(DATABASE)
    cached_sample_filename = "{dbpath:s}/{dbname:s}_sampleID-{sampleID:04d}.pkl".format(dbpath=dbpath,dbname=dbname, sampleID=SAMPLE_ID)
    if not os.path.isfile(cached_sample_filename):
        with open(cached_sample_filename, 'wb') as f:
            pickle.dump(SAMPLE, f)

if CACHE_SAMPLE and not TEST_SAMPLE_READ_FROM_CACHE:
    cached_sample_filename = "{dbpath:s}/{dbname:s}_sampleID-{sampleID:04d}.pkl".format(dbpath=dbpath,dbname=dbname, sampleID=TEST_SAMPLE_ID)
    if not os.path.isfile(cached_sample_filename):
        with open(cached_sample_filename, 'wb') as f:
            pickle.dump(TEST_SAMPLE, f)

end = timeit.default_timer()
print("Time to load and preprocess sample: {elapsed:.3f}".format(elapsed=end - start))

# Build and write representations
if not os.path.isdir(EX_DIR):
    os.mkdir(EX_DIR)

start = timeit.default_timer()
with open(EX_FILENAME,'w') as f:
    lensapi.examples.writeheader(f, NETINFO['header'])
    for dialectLabel, Dialect in SAMPLE.items():
        if FLAG_CONTEXT:
            context = dialectLabel
        else:
            context = None

        for eventLabel, events in NETINFO['events'].items():
            # Loop over words and build/write examples
            # if SORT_EXAMPLES_ALPHABETICALLY:
            #     Words = sorted(Dialect.keys())
            # else:
            #     Words = Dialect.keys()

            for EXAMPLE in Dialect:
                name = '{w}_{t}_{k}'.format(w=EXAMPLE['word'],t=eventLabel,k=dialectLabel)
                inputs = lensapi.examples.buildinput(EXAMPLE,events,NETINFO['input'],context,ISET)
                targets = lensapi.examples.buildtarget(EXAMPLE,events,NETINFO['target'],context,TSET)
                if CONFIG['frequency']:
                    freq = CONFIG['frequency']
                else:
                    freq = 1 # everything equally probable
                lensapi.examples.writeex(f,name,freq,inputs,targets)

end = timeit.default_timer()
print("Time to write training set: {elapsed:.3f}".format(elapsed=end - start))
if TEST_SAMPLE_ID == SAMPLE_ID:
    shutil.copyfile(EX_FILENAME,TEST_EX_FILENAME)
else:
    start = timeit.default_timer()
    with open(TEST_EX_FILENAME,'w') as f:
        lensapi.examples.writeheader(f, NETINFO['header'])
        for dialectLabel, Dialect in TEST_SAMPLE.items():
            if FLAG_CONTEXT:
                context = dialectLabel
            else:
                context = None

            for eventLabel, events in NETINFO['events'].items():
                # Loop over words and build/write examples
                # Words = sorted(Dialect.keys())
                for EXAMPLE in Dialect:
                    name = '{w}_{t}_{k}'.format(w=EXAMPLE['word'],t=eventLabel,k=dialectLabel)
                    inputs = lensapi.examples.buildinput(EXAMPLE,events,NETINFO['input'],context,ISET)
                    targets = lensapi.examples.buildtarget(EXAMPLE,events,NETINFO['target'],context,TSET)
                    if CONFIG['frequency']:
                        freq = CONFIG['frequency']
                    else:
                        freq = 1 # everything equally probable
                    lensapi.examples.writeex(f,name,freq,inputs,targets)

    end = timeit.default_timer()
    print("Time to write testing set: {elapsed:.3f}".format(elapsed=end - start))

if CONFIG['TrainingMethod'].lower() == 'blocked':
    for dialectLabel, Dialect in SAMPLE.items():
        with open("{d}.ex".format(d=dialectLabel.lower()),'w') as f:
            lensapi.examples.writeheader(f, NETINFO['header'])
            if FLAG_CONTEXT:
                context = dialectLabel
            else:
                context = None

            for eventLabel, events in NETINFO['events'].items():
                # Loop over words and build/write examples
                # Words = sorted(Dialect.keys())
                for EXAMPLE in Dialect:
                    name = '{w}_{t}_{k}'.format(w=EXAMPLE['word'],t=eventLabel,k=dialectLabel)
                    inputs = lensapi.examples.buildinput(EXAMPLE,events,NETINFO['input'],context,ISET)
                    targets = lensapi.examples.buildtarget(EXAMPLE,events,NETINFO['target'],context,TSET)
                    if CONFIG['frequency']:
                        freq = CONFIG['frequency']
                    else:
                        freq = 1 # everything equally probable
                    lensapi.examples.writeex(f,name,freq,inputs,targets)

# Write Network file
LayerNames = [layer['name'] for layer in NETINFO['layers']]
for inputLabel in ISET:
    layername = '{i}Input'.format(i=inputLabel.title())
    iLayer = LayerNames.index(layername)
    try:
        rep = [u for sublist in EXAMPLE[inputLabel] for u in sublist]
    except:
        rep = EXAMPLE[inputLabel]

    NETINFO['layers'][iLayer]['nunits'] = len(rep)

for inputLabel in TSET:
    layername = '{i}Output'.format(i=inputLabel.title())
    iLayer = LayerNames.index(layername)
    try:
        rep = [u for sublist in EXAMPLE[inputLabel] for u in sublist]
    except:
        rep = EXAMPLE[inputLabel]

    NETINFO['layers'][iLayer]['nunits'] = len(rep)

network_text = network_template.render(NetInfo=NETINFO)
with open(IN_FILENAME,'w') as f:
    f.write(network_text.strip())

# Write Trainscript
from mako import exceptions

try:
    trainscript_text = trainscript_template.render(CONFIG=CONFIG,NETINFO=NETINFO)
except:
    with open('Mako_Error.html','wb') as f:
        f.write(exceptions.html_error_template().render())

with open(TRAINSCRIPT_FILENAME,'w') as f:
    f.write(trainscript_text)
