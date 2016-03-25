def prune_representations(SAMPLE):
    phon_UnitUsed = []
    orth_UnitUsed = []
    sem_UnitUsed = []
    # Identify which phon units are used
    for dialectLabel, DIALECT in SAMPLE.items():
        for word, EXAMPLE in DIALECT.items():
            if 'orth' in EXAMPLE:
                try:
                    orth_UnitUsed = [x|y for x,y in zip(EXAMPLE['orth'],orth_UnitUsed)]
                except IndexError:
                    # Should only happen first time slot is encountered
                    orth_UnitUsed = orth

            if 'phon' in EXAMPLE:
                try:
                    phon_UnitUsed = [x|y for x,y in zip(EXAMPLE['phon'],phon_UnitUsed)]
                except IndexError:
                    # Should only happen first time slot is encountered
                    phon_UnitUsed = phon

            if 'sem' in EXAMPLE:
                try:
                    sem_UnitUsed = [x|y for x,y in zip(EXAMPLE['sem'],sem_UnitUsed)]
                except IndexError:
                    # Should only happen first time slot is encountered
                    sem_UnitUsed = sem

    # Prune representations accordingly
    for dialectLabel, DIALECT in SAMPLE.items():
        for word, EXAMPLE in DIALECT.items():
            orth= SAMPLE[dialectLabel][word]['orth']
            SAMPLE[dialectLabel][word]['orth'] = [x for x,y in zip(orth,orth_UnitUsed) if y]

            phon = SAMPLE[dialectLabel][word]['phon']
            SAMPLE[dialectLabel][word]['phon'] = [x for x,y in zip(phon,phon_UnitUsed) if y]

            sem = SAMPLE[dialectLabel][word]['sem']
            SAMPLE[dialectLabel][word]['sem'] = [x for x,y in zip(sem,sem_UnitUsed) if y]

    return SAMPLE
