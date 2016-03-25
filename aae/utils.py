def prune_representations(SAMPLE):
    phon_UnitUsed = []
    orth_UnitUsed = []
    # Identify which phon units are used
    for dialectLabel, DIALECT in SAMPLE.items():
        for word, EXAMPLE in DIALECT.items():
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
    for dialectLabel, DIALECT in SAMPLE.items():
        for word, EXAMPLE in DIALECT.items():
            phon_code = ''
            for i,phon in enumerate(EXAMPLE['phon']):
                pp = [x for x,y in zip(phon, phon_UnitUsed[i]) if y]
                SAMPLE[dialectLabel][word]['phon'][i] = pp
                if pp:
                    phon_code += EXAMPLE['phon_code'][i]
            SAMPLE[dialectLabel][word]['phon_code'] = phon_code

            orth_code = ''
            for i,orth in enumerate(EXAMPLE['orth']):
                pp = [x for x,y in zip(orth, orth_UnitUsed[i]) if y]
                SAMPLE[dialectLabel][word]['orth'][i] = pp
                if pp:
                    orth_code += EXAMPLE['orth_code'][i]
            SAMPLE[dialectLabel][word]['orth_code'] = orth_code

            sem = SAMPLE[dialectLabel][word]['sem']
            SAMPLE[dialectLabel][word]['sem'] = [x for x,y in zip(sem,sem_UnitUsed) if y]

    return SAMPLE
