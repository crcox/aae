PRAGMA synchronous = OFF;
PRAGMA journal_mode = MEMORY;
PRAGMA cache_size = 40000;
BEGIN TRANSACTION;
CREATE TABLE "corpus" (
  "id" INTEGER,
  "label" TEXT NOT NULL,
  "description" TEXT DEFAULT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "accent" (
  "id" INTEGER,
  "label" TEXT NOT NULL,
  "description" TEXT DEFAULT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "alphabet" (
  "id" INTEGER,
  "label" TEXT NOT NULL,
  "description" TEXT DEFAULT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "examplemethod" (
  "id" INTEGER,
  "frequency" INTEGER NOT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "experiment" (
  "id" INTEGER,
  "sample_id" INTEGER NOT NULL,
  "netname" TEXT NOT NULL,
  "intervals" INTEGER NOT NULL,
  "ticksPerInterval" INTEGER NOT NULL,
  "netType" TEXT NOT NULL,
  "context" INTEGER NOT NULL,
  "disambiguateHomophones" INTEGER NOT NULL,
  "frequency" INTEGER NOT NULL,
  "warmstart" INTEGER NOT NULL,
  "testGroupCrit" FLOAT NOT NULL,
  "targetRadius" FLOAT NOT NULL,
  "UpdatesPerCall" INTEGER NOT NULL,
  "weightDecay" FLOAT NOT NULL,
  "batchSize" INTEGER NOT NULL,
  "learningRate" FLOAT NOT NULL,
  "momentum" FLOAT NOT NULL,
  "reportInterval" INTEGER NOT NULL,
  "SpikeThreshold" FLOAT NOT NULL,
  "SpikeThresholdStepSize" FLOAT NOT NULL,
  "TestEpoch" INTEGER NOT NULL,
  "ErrorCriterion" FLOAT NOT NULL,
  PRIMARY KEY ("id")
  CONSTRAINT "fk_experiment_sample1" FOREIGN KEY ("sample_id") REFERENCES "sample" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "dialect" (
  "id" INTEGER,
  "label" TEXT NOT NULL,
  "description" TEXT DEFAULT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "dialect_has_rule" (
  "dialect_id" INTEGER NOT NULL,
  "rule_id" INTEGER NOT NULL,
  PRIMARY KEY ("dialect_id","rule_id")
  CONSTRAINT "fk_dialect_has_rule_dialect" FOREIGN KEY ("dialect_id") REFERENCES "dialect" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_dialect_has_rule_rule3" FOREIGN KEY ("rule_id") REFERENCES "rule" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "performance" (
  "id" INTEGER,
  "experiment_id" INTEGER NOT NULL,
  "sample_id" INTEGER NOT NULL,
  "word_id" INTEGER NOT NULL,
  "dialect_id" INTEGER NOT NULL,
  "update_count" INTEGER NOT NULL,
  "inputlayer" TEXT NOT NULL,
  "outputlayer" TEXT NOT NULL,
  "hit" INTEGER DEFAULT NULL,
  "miss" INTEGER DEFAULT NULL,
  "falsealarm" INTEGER DEFAULT NULL,
  "correctrejection" INTEGER DEFAULT NULL,
  PRIMARY KEY ("id")
  CONSTRAINT "fk_performance_experiment1" FOREIGN KEY ("experiment_id") REFERENCES "experiment" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_performance_sample1" FOREIGN KEY ("sample_id") REFERENCES "sample" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_performance_word1" FOREIGN KEY ("word_id") REFERENCES "word" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_performance_dialect1" FOREIGN KEY ("dialect_id") REFERENCES "dialect" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "phoneme" (
  "id" INTEGER,
  "phoneme" TEXT NOT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "phonology" (
  "id" INTEGER,
  "phoncode" TEXT NOT NULL UNIQUE,
  PRIMARY KEY ("id")
);
CREATE TABLE "word_has_phonology" (
  "word_id" INTEGER NOT NULL,
  "dialect_id" INTEGER NOT NULL,
  "phonology_id" INTEGER NOT NULL,
  CONSTRAINT "fk_word_has_phonology_word1" FOREIGN KEY ("word_id") REFERENCES "word" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_dialect_has_phonology_dialect1" FOREIGN KEY ("dialect_id") REFERENCES "dialect" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_word_has_phonology_phonology1" FOREIGN KEY ("phonology_id") REFERENCES "phonology" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "dialect_has_phonology" (
  "dialect_id" INTEGER NOT NULL,
  "phonology_id" INTEGER NOT NULL,
  PRIMARY KEY ("dialect_id","phonology_id")
  CONSTRAINT "fk_dialect_has_phonology_dialect1" FOREIGN KEY ("dialect_id") REFERENCES "dialect" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_dialect_has_phonology_phonology1" FOREIGN KEY ("phonology_id") REFERENCES "phonology" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "phonology_has_phoneme" (
  "phonology_id" INTEGER NOT NULL,
  "phoneme_id" INTEGER NOT NULL,
  "unit" INTEGER NOT NULL,
  PRIMARY KEY ("phonology_id","phoneme_id","unit")
  CONSTRAINT "fk_phonology_has_phoneme_phonology1" FOREIGN KEY ("phonology_id") REFERENCES "phonology" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_phonology_has_phoneme_phoneme1" FOREIGN KEY ("phoneme_id") REFERENCES "phoneme" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "phonology_has_rule" (
  "dialect_id" INTEGER NOT NULL,
  "word_id" INTEGER NOT NULL,
  "phonology_id" INTEGER NOT NULL,
  "rule_id" INTEGER NOT NULL,
  PRIMARY KEY ("phonology_id","word_id","dialect_id","rule_id")
  CONSTRAINT "fk_phonology_has_rule_phonology1" FOREIGN KEY ("phonology_id") REFERENCES "phonology" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_phonology_has_rule_word1" FOREIGN KEY ("word_id") REFERENCES "word" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_phonology_has_rule_dialect1" FOREIGN KEY ("dialect_id") REFERENCES "dialect" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_phonology_has_rule_rule1" FOREIGN KEY ("rule_id") REFERENCES "rule" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "phonrep" (
  "accent_id" INTEGER NOT NULL,
  "phoneme_id" INTEGER NOT NULL,
  "unit" INTEGER NOT NULL,
  "value" INTEGER NOT NULL,
  PRIMARY KEY ("accent_id", "phoneme_id", "unit")
  CONSTRAINT "fk_phonrep_phoneme1" FOREIGN KEY ("phoneme_id") REFERENCES "phoneme" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_phonrep_accent1" FOREIGN KEY ("accent_id") REFERENCES "accent" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "grapheme" (
  "id" INTEGER,
  "grapheme" TEXT DEFAULT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "orthography" (
  "id" INTEGER,
  "corpus_id" INTEGER NOT NULL,
  "word_id" INTEGER NOT NULL,
  "orthcode" TEXT NOT NULL,
  PRIMARY KEY ("id")
  CONSTRAINT "fk_orthography_corpus1" FOREIGN KEY ("corpus_id") REFERENCES "corpus" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_orthography_word1" FOREIGN KEY ("word_id") REFERENCES "word" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "orthography_has_grapheme" (
  "orthography_id" INTEGER NOT NULL,
  "grapheme_id" INTEGER NOT NULL,
  "unit" INTEGER NOT NULL,
  PRIMARY KEY ("orthography_id", "grapheme_id", "unit")
  CONSTRAINT "fk_orthography_has_grapheme_orthography1" FOREIGN KEY ("orthography_id") REFERENCES "orthography" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_orthography_has_grapheme_grapheme1" FOREIGN KEY ("grapheme_id") REFERENCES "grapheme" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "orthography_has_rule" (
  "orthography_id" INTEGER NOT NULL,
  "orthography_word_id" INTEGER NOT NULL,
  "orthography_word_corpus_id" INTEGER NOT NULL,
  "orthography_dialect_id" INTEGER NOT NULL,
  "rule_id" INTEGER NOT NULL,
  PRIMARY KEY ("orthography_id","orthography_word_id","orthography_word_corpus_id","orthography_dialect_id","rule_id")
  CONSTRAINT "fk_orthography_has_rule_orthography1" FOREIGN KEY ("orthography_id", "orthography_dialect_id") REFERENCES "orthography" ("id", "dialect_id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_orthography_has_rule_rule1" FOREIGN KEY ("rule_id") REFERENCES "rule" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "orthrep" (
  "alphabet_id" INTEGER NOT NULL,
  "grapheme_id" INTEGER NOT NULL,
  "unit" INTEGER NOT NULL,
  "value" INTEGER NOT NULL,
  PRIMARY KEY ("alphabet_id", "grapheme_id", "unit")
  CONSTRAINT "fk_orthrep_grapheme1" FOREIGN KEY ("grapheme_id") REFERENCES "grapheme" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_orthrep_alphabet1" FOREIGN KEY ("alphabet_id") REFERENCES "alphabet" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "rule" (
  "id" INTEGER,
  "label" TEXT NOT NULL,
  "description" TEXT DEFAULT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "sample" (
  "id" INTEGER,
  "accent_id" INTEGER NOT NULL,
  "alphabet_id" INTEGER NOT NULL,
  "corpus_id" INTEGER NOT NULL,
  "dialect_root_id" INTEGER NOT NULL,
  "dialect_alt_id" INTEGER NOT NULL,
  "n" INTEGER NOT NULL,
  "n_root_homophones" INTEGER NOT NULL,
  "n_root_homophonic_words" INTEGER NOT NULL,
  "n_alt_homophones" INTEGER NOT NULL,
  "n_alt_homophonic_words" INTEGER NOT NULL,
  "n_diff_root_alt" INTEGER NOT NULL,
  "p_rule_applied" double DEFAULT NULL,
  "use_frequency" INTEGER NOT NULL,
  "child_of" INTEGER DEFAULT NULL,
  "source" TEXT DEFAULT NULL,
  PRIMARY KEY ("id")
  CONSTRAINT "fk_sample_dialect1" FOREIGN KEY ("dialect_root_id", "dialect_alt_id") REFERENCES "dialect" ("id", "id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_sample_accent1" FOREIGN KEY ("accent_id") REFERENCES "accent" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "semrep" (
  "corpus_id" INTEGER NOT NULL,
  "word_id" INTEGER NOT NULL,
  "unit" INTEGER NOT NULL,
  "value" INTEGER NOT NULL,
  PRIMARY KEY ("corpus_id","word_id","unit")
  CONSTRAINT "fk_semrep_word1" FOREIGN KEY ("word_id") REFERENCES "word" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_semrep_corpus1" FOREIGN KEY ("corpus_id") REFERENCES "corpus" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "trainscript" (
  "id" INTEGER,
  "label" TEXT NOT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "word" (
  "id" INTEGER,
  "word" TEXT NOT NULL,
  "frequency" INTEGER DEFAULT 1,
  "corpus_id" INTEGER NOT NULL,
  CONSTRAINT "pk_word" PRIMARY KEY ("id"),
  CONSTRAINT "fk_word_corpus1" FOREIGN KEY ("corpus_id") REFERENCES "corpus" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "sample_has_example" (
  "sample_id" INTEGER NOT NULL,
  "word_id" INTEGER NOT NULL,
  "phonology_id" INTEGER NOT NULL,
  "orthography_id" INTEGER NOT NULL,
  "dialect_id" INTEGER NOT NULL,
  PRIMARY KEY ("sample_id", "word_id", "dialect_id")
  CONSTRAINT "fk_sample_has_example_sample1" FOREIGN KEY ("sample_id") REFERENCES "sample" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_sample_has_example_word1" FOREIGN KEY ("word_id") REFERENCES "word" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
  CONSTRAINT "fk_sample_has_example_phonology1" FOREIGN KEY ("phonology_id") REFERENCES "phonology" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
  CONSTRAINT "fk_sample_has_example_orthography1" FOREIGN KEY ("orthography_id") REFERENCES "orthography" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
  CONSTRAINT "fk_sample_has_example_dialect1" FOREIGN KEY ("dialect_id") REFERENCES "dialect" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE VIEW example_data AS
    SELECT
      sample.sample_id AS sample_id,
      word.id AS word_id,
      word,
      frequency,
      dialect.id AS dialect_id,
      dialect.label AS dialect,
      orthography.id AS orthography_id,
      orthcode,
      phonology.id AS phonology_id,
      phoncode
    FROM sample_has_example AS sample
    JOIN word ON sample.word_id=word.id
    JOIN orthography ON sample.orthography_id=orthography.id
    JOIN phonology ON sample.phonology_id=phonology.id
    JOIN dialect ON sample.dialect_id=dialect.id;
CREATE VIEW orthography_representation AS
    SELECT
      sample.word_id AS word_id,
      sample.sample_id AS sample_id,
      sample.dialect_id AS dialect_id,
      orthography_has_grapheme.orthography_id AS orthography_id,
      orthography_has_grapheme.grapheme_id AS grapheme_id,
      orthography_has_grapheme.unit AS grapheme_unit,
      orthrep.unit AS orthrep_unit,
      orthrep.value AS orthrep_value,
      orthrep.alphabet_id AS alphabet_id
    FROM sample_has_example AS sample
    JOIN orthography_has_grapheme ON sample.orthography_id=orthography_has_grapheme.orthography_id
    JOIN orthrep ON orthography_has_grapheme.grapheme_id = orthrep.grapheme_id;
CREATE VIEW phonology_representation AS
    SELECT
      sample.word_id AS word_id,
      sample.sample_id AS sample_id,
      sample.dialect_id AS dialect_id,
      phonology_has_phoneme.phonology_id AS phonology_id,
      phonology_has_phoneme.phoneme_id AS phoneme_id,
      phonology_has_phoneme.unit AS phoneme_unit,
      phonrep.unit AS phonrep_unit,
      phonrep.value AS phonrep_value,
      phonrep.accent_id as accent_id
    FROM sample_has_example AS sample
    JOIN phonology_has_phoneme ON sample.phonology_id=phonology_has_phoneme.phonology_id
    JOIN phonrep ON phonology_has_phoneme.phoneme_id = phonrep.phoneme_id;
CREATE VIEW semantic_representation AS
    SELECT
      sample.dialect_id AS dialect_id,
      sample.sample_id AS sample_id,
      semrep.word_id AS word_id,
      unit AS semrep_unit,
      value AS semrep_value
  FROM sample_has_example AS sample
  JOIN semrep ON sample.word_id=semrep.word_id;
CREATE INDEX "phonrep_fk_phonrep_phoneme1_idx" ON "phonrep" ("phoneme_id");
CREATE INDEX "phonrep_fk_phonrep_accent1_idx" ON "phonrep" ("accent_id");
CREATE INDEX "semrep_fk_semrep_word1_idx" ON "semrep" ("word_id");
CREATE INDEX "sample_has_example_fk_sample_has_example_sample1_idx" ON "sample_has_example" ("sample_id");
CREATE INDEX "sample_has_example_fk_sample_has_example_word1_idx" ON "sample_has_example" ("word_id");
CREATE INDEX "dialect_has_rule_fk_dialect_has_rule_rule1_idx" ON "dialect_has_rule" ("rule_id");
CREATE INDEX "dialect_has_rule_fk_dialect_has_rule_dialect_idx" ON "dialect_has_rule" ("dialect_id");
CREATE INDEX "word_fk_word_corpus1_idx" ON "word" ("corpus_id");
CREATE INDEX "phonology_has_rule_fk_phonology_has_rule_rule1_idx" ON "phonology_has_rule" ("rule_id");
CREATE INDEX "phonology_has_rule_fk_phonology_has_rule_phonology1_idx" ON "phonology_has_rule" ("phonology_id","word_id","dialect_id");
CREATE INDEX "phonology_has_rule_fk_phonology_has_rule_phonology1" ON "phonology_has_rule" ("phonology_id","dialect_id");
END TRANSACTION;
