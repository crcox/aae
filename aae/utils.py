def prune_representations(SAMPLES):
    phon_UnitUsed = []
    orth_UnitUsed = []
    # Identify which phon units are used
    if isinstance(SAMPLES,dict):
        SAMPLES=[SAMPLES]
    for SAMPLE in SAMPLES:
        for dialectLabel, DIALECT in SAMPLE.items():
            for EXAMPLE in DIALECT:
                word = EXAMPLE['word']
                if 'phon' in EXAMPLE:
                    for i,phon in enumerate(EXAMPLE['phon']):
                        try:
                            phon_UnitUsed[i] = [x|y for x,y in zip(phon,phon_UnitUsed[i])]
                        except IndexError:
                            # Should only happen first time slot is encountered
                            phon_UnitUsed.append(phon)

                if 'orth' in EXAMPLE:
                    for i,orth in enumerate(EXAMPLE['orth']):
                        try:
                            orth_UnitUsed[i] = [x|y for x,y in zip(orth,orth_UnitUsed[i])]
                        except IndexError:
                            # Should only happen first time slot is encountered
                            orth_UnitUsed.append(orth)

                if 'sem' in EXAMPLE:
                    try:
                        sem_UnitUsed = [x|y for x,y in zip(EXAMPLE['sem'],sem_UnitUsed)]
                    except UnboundLocalError:
                        # Should only happen first time slot is encountered
                        sem_UnitUsed = EXAMPLE['sem']

    # Prune representations accordingly
    for k,SAMPLE in enumerate(SAMPLES):
        for dialectLabel, DIALECT in SAMPLE.items():
            for j,EXAMPLE in enumerate(DIALECT):
                word = EXAMPLE['word']
                phon_code = ''
                for i,phon in enumerate(EXAMPLE['phon']):
                    pp = [x for x,y in zip(phon, phon_UnitUsed[i]) if y]
                    SAMPLE[dialectLabel][j]['phon'][i] = pp
                    if pp:
                        phon_code += EXAMPLE['phon_code'][i]
                SAMPLE[dialectLabel][j]['phon_code'] = phon_code

                orth_code = ''
                for i,orth in enumerate(EXAMPLE['orth']):
                    pp = [x for x,y in zip(orth, orth_UnitUsed[i]) if y]
                    SAMPLE[dialectLabel][j]['orth'][i] = pp
                    if pp:
                        orth_code += EXAMPLE['orth_code'][i]
                SAMPLE[dialectLabel][j]['orth_code'] = orth_code

                sem = SAMPLE[dialectLabel][j]['sem']
                SAMPLE[dialectLabel][j]['sem'] = [x for x,y in zip(sem,sem_UnitUsed) if y]

        SAMPLES[k] = SAMPLE

    return SAMPLES

def jitter_representations(SAMPLE,slots,TEST_SAMPLE=[]):
    for dialectLabel, DIALECT in SAMPLE.items():
        for EXAMPLE in DIALECT:
            word = EXAMPLE['word']
            if 'phon' in EXAMPLE:
                for i,phon in enumerate(EXAMPLE['phon']):
                    try:
                        phon_UnitUsed[i] = [x|y for x,y in zip(phon,phon_UnitUsed[i])]
                    except IndexError:
                        # Should only happen first time slot is encountered
                        phon_UnitUsed.append(phon)

            if 'orth' in EXAMPLE:
                for i,orth in enumerate(EXAMPLE['orth']):
                    try:
                        orth_UnitUsed[i] = [x|y for x,y in zip(orth,orth_UnitUsed[i])]
                    except IndexError:
                        # Should only happen first time slot is encountered
                        orth_UnitUsed.append(orth)

            if 'sem' in EXAMPLE:
                try:
                    sem_UnitUsed = [x|y for x,y in zip(EXAMPLE['sem'],sem_UnitUsed)]
                except UnboundLocalError:
                    # Should only happen first time slot is encountered
                    sem_UnitUsed = EXAMPLE['sem']

    # Prune representations accordingly
    for k,SAMPLE in enumerate(SAMPLES):
        for dialectLabel, DIALECT in SAMPLE.items():
            for j,EXAMPLE in enumerate(DIALECT):
                word = EXAMPLE['word']
                phon_code = ''
                for i,phon in enumerate(EXAMPLE['phon']):
                    pp = [x for x,y in zip(phon, phon_UnitUsed[i]) if y]
                    SAMPLE[dialectLabel][j]['phon'][i] = pp
                    if pp:
                        phon_code += EXAMPLE['phon_code'][i]
                SAMPLE[dialectLabel][j]['phon_code'] = phon_code

                orth_code = ''
                for i,orth in enumerate(EXAMPLE['orth']):
                    pp = [x for x,y in zip(orth, orth_UnitUsed[i]) if y]
                    SAMPLE[dialectLabel][j]['orth'][i] = pp
                    if pp:
                        orth_code += EXAMPLE['orth_code'][i]
                SAMPLE[dialectLabel][j]['orth_code'] = orth_code

                sem = SAMPLE[dialectLabel][j]['sem']
                SAMPLE[dialectLabel][j]['sem'] = [x for x,y in zip(sem,sem_UnitUsed) if y]

        SAMPLES[k] = SAMPLE

    return SAMPLES
