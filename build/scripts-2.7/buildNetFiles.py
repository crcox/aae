#!/home/chris/.pyenv/versions/aae/bin/python
import argparse
import os
import pkg_resources
import sqlite3
import json
import yaml
import aae.sql.select
import aae.utils
import lensapi.examples
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
args = p.parse_args()

if args.database:
    DATABASE = args.database
else:
    DATABASE = pkg_resources.resource_filename(resource_package,'database/main.db')

PATH_TO_JSON = args.config
EX_FILENAME = args.output
IN_FILENAME = os.path.join(os.path.dirname(EX_FILENAME),'network.in')
TRAINSCRIPT_FILENAME = os.path.join(os.path.dirname(EX_FILENAME),'trainscript.tcl')

# Load instructions
with open(PATH_TO_JSON,'r') as f:
    CONFIG = json.load(f)

DIALECT_SUBSET = []
if args.dialect:
    DIALECT_SUBSET = args.dialect
else:
    if CONFIG['TrainingMethod'] in ['AAE','SAE','reading_AAE','reading_SAE']:
        DIALECT_SUBSET = CONFIG['TrainingMethod']

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
trainscript_template = Template(trainscript_template_string)

if 'warmstart' in CONFIG and CONFIG['warmstart']:
    NetInfoFile = 'network/{s:s}_warmstart.yaml'.format(s=CONFIG['netname'])
else:
    NetInfoFile = 'network/{s:s}.yaml'.format(s=CONFIG['netname'])
with pkg_resources.resource_stream('aae',NetInfoFile) as f:
    NETINFO = yaml.load(f)

NETINFO['netname'] = CONFIG['netname']
NETINFO['intervals'] = CONFIG['intervals']
NETINFO['ticksPerInterval'] = CONFIG['ticksPerInterval']
NETINFO['netType'] = CONFIG['netType']

if args.sample_id:
    SAMPLE_ID = args.sample_id
else:
    SAMPLE_ID = CONFIG['sample_id']

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
conn = sqlite3.connect(DATABASE)
conn.row_factory = sqlite3.Row
SAMPLE = aae.sql.select.sample(conn, SAMPLE_ID, ACCENT_ID)
conn.close()

if DIALECT_SUBSET:
    SAMPLE = dict((dialectLabel, dialectExamples)
            for dialectLabel,dialectExamples in SAMPLE.items()
            if dialectLabel in DIALECT_SUBSET)

SAMPLE = aae.utils.prune_representations(SAMPLE)

# Add "warmstart" data into the SAMPLE structures.
if 'warmstart' in NETINFO:
    WarmCfg = NETINFO['warmstart']
    if all(True if k in WarmCfg.keys() else False for k in ['knn','ratio']):
        print "knn and ratio cannot both be specified."
        raise ValueError
    DIST = lensapi.examples.stimdist(SAMPLE,WarmCfg['type'],method=WarmCfg['distmethod'])
    try:
        SAMPLE = lensapi.examples.warmstart(SAMPLE,DIST,WarmCfg['type'],WarmCfg['name'],knn=WarmCfg['knn'])
    except KeyError:
        SAMPLE = lensapi.examples.warmstart(SAMPLE,DIST,WarmCfg['type'],WarmCfg['name'],ratio=WarmCfg['ratio'])

# Build and write representations
with open(EX_FILENAME,'w') as f:
    lensapi.examples.writeheader(f, NETINFO['header'])
    for dialectLabel, Dialect in SAMPLE.items():
        if FLAG_CONTEXT:
            context = dialectLabel
        else:
            context = None

        for eventLabel, events in NETINFO['events'].items():
            # Loop over words and build/write examples
            Words = sorted(Dialect.keys())
            for word in Words:
                EXAMPLE = Dialect[word]
                name = '{w}_{t}_{k}'.format(w=word,t=eventLabel,k=dialectLabel)
                inputs = lensapi.examples.buildinput(EXAMPLE,events,NETINFO['input'],context,ISET)
                targets = lensapi.examples.buildtarget(EXAMPLE,events,NETINFO['target'],context,TSET)
                if CONFIG['frequency']:
                    freq = CONFIG['frequency']
                else:
                    freq = 1 # everything equally probable
                lensapi.examples.writeex(f,name,freq,inputs,targets)

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
                Words = sorted(Dialect.keys())
                for word in Words:
                    EXAMPLE = Dialect[word]
                    name = '{w}_{t}_{k}'.format(w=word,t=eventLabel,k=dialectLabel)
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
trainscript_text = trainscript_template.render(CONFIG=CONFIG,NETINFO=NETINFO)
with open(TRAINSCRIPT_FILENAME,'w') as f:
    f.write(trainscript_text.strip())
