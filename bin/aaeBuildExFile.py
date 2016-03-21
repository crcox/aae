#!/usr/bin/env python

import pickle, yaml, sys, os, shutil
from lensapi import examples
# Reminders about Lens example files:
# - Files begin with a header that set defaults.
# - The header is terminated with a semi-colon.
# - Each ``trial'' can be composed of many events.
# - In this model, there are three events:
#   1. Presentation
#   2. Settling---letting the recurrent dynamics happen
#   3. Evaluation---the targets are presented, and error assessed.
# - Each event lasts two ticks, so a full trial is 6 ticks.

# Load instructions
pathToYAML = sys.argv[1]
with open(pathToYAML,'r') as f:
    ydat = [d for d in yaml.load_all(f) if not d is None]

print ydat

# Parse instructions into phases
#phases = []
#for cfg in ydat['phases']:
#    shared = ydat.copy()
#    del shared['phases']
#    shared.update(cfg)
#    phases.append(shared)
phases = ydat;

ISET = set([v.keys()[0] if isinstance(v,dict)
        else v
        for p in phases
        for v in p['input'].values()])

TSET = set([v.keys()[0] if isinstance(v,dict)
        else v
        for p in phases
        for v in p['target'].values()])

ISET = sorted(list(ISET))
TSET = sorted(list(TSET))

# Note whether any phase involves a context unit.
useContextUnit = any([cfg['context'] for cfg in phases])

# Load and organize the stimuli, and note the words used across all datasets.
STIM = {}
words = []
# Stimuli need to be keyed with the name of the dataset
for k,path in set([s for cfg in phases for s in cfg['stimuli'].items()]):
    with open(path,'rb') as f:
        STIM[k] = pickle.load(f)
    for w in STIM[k].keys():
        if not w in words:
            words.append(w)
words.sort()

# Add "warmstart" data into the STIM structures.
WarmCfg_prev = {}
for cfg in phases:
    try:
        WarmCfg = cfg['warmstart']
    except KeyError:
        continue
    if WarmCfg and not WarmCfg == WarmCfg_prev:
        if all([True if k in WarmCfg.keys() else False for k in ['knn','ratio']]):
            print "knn and ratio cannot both be specified."
            raise ValueError

        DIST = examples.stimdist(STIM,WarmCfg['type'],method=WarmCfg['distmethod'])

        try:
            STIM = examples.warmstart(STIM,DIST,WarmCfg['type'],WarmCfg['name'],knn=WarmCfg['knn'])
        except KeyError:
            STIM = examples.warmstart(STIM,DIST,WarmCfg['type'],WarmCfg['name'],ratio=WarmCfg['ratio'])

        WarmCfg_prev = WarmCfg



# Build and write representations
for pnum, cfg in enumerate(phases):
    fname = 'train.ex'

    if len(phases) > 1:
        pdir = 'phase{n:02d}'.format(n=pnum+1)
        fdir = os.path.join('ex',pdir)
    else:
        fdir = os.path.join('ex')

    try:
        os.makedirs(fdir)
    except OSError:
        pass
    fpath = os.path.join(fdir,fname)

    with open(fpath,'w') as f:
        examples.writeheader(f, cfg['header'])

        for key in cfg['stimuli'].keys():
            if useContextUnit:
                context = key
            else:
                context = None

            for template_key, events in cfg['events'].items():
                # Loop over words and build/write examples
                for w in words:
                    name = '{w}_{t}_{k}'.format(w=w,t=template_key,k=key)
                    WORD = STIM[key][w]
                    inputs = examples.buildinput(WORD,events,cfg['input'],context,ISET)
                    targets = examples.buildtarget(WORD,events,cfg['target'],context,TSET)
                    if cfg['frequency']:
                        freq = cfg['frequency']
                    else:
                        freq = 1 # everything equally probable
                    examples.writeex(f,name,freq,inputs,targets)

    # Since for the time being, these are always the same stimuli.
    shutil.copyfile(os.path.join(fdir,'train.ex'),os.path.join(fdir,'test.ex'))

# Write info about IO layers to a YAML file
IOLayers = []
for i in ISET:
    try:
        rep = [u for sublist in WORD[i] for u in sublist]
    except:
        rep = WORD[i]

    d = {
            'name': '{i}Input'.format(i=i.title()),
            'nunits': len(rep),
            'type': 'INPUT'
        }
    IOLayers.append(d)

if cfg['context']:
    d = {
            'name': 'Context',
            'nunits': 1,
            'type': 'INPUT'
        }
    IOLayers.append(d)

for i in TSET:
    try:
        rep = [u for sublist in WORD[i] for u in sublist]
    except:
        rep = WORD[i]

    d = {
            'name': '{i}Output'.format(i=i.title()),
            'nunits': len(rep),
            'type': 'OUTPUT',
			"errorType": "SUM_SQUARED",
            "criterion": "STANDARD_CRIT",
            "useHistory": True,
            "writeOutputs": True
        }
    IOLayers.append(d)

with open('iolayers.yaml','wb') as f:
    yaml.dump_all(IOLayers,f,default_flow_style=False, explicit_start=True)

# Archiving for reference
#try:
#    os.makedirs(os.path.join(ydat['expdir'],'yaml'))
#except OSError:
#    pass

#with open(os.path.join(ydat['expdir'],'yaml','examples.yaml'),'wb') as f:
#    yaml.dump(ydat,f,sort_keys=True, indent=2, separators=(',', ': '))
#with open('iolayers.yaml','wb') as f:
#    yaml.dump({'layers':IOLayers,'expdir':cfg['expdir']},f,sort_keys=True, indent=2, separators=(',', ': '))
