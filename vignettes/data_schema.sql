PRAGMA synchronous = OFF;
PRAGMA journal_mode = MEMORY;
BEGIN TRANSACTION;
CREATE TABLE "version" (
  "id" INTEGER,
  "label" TEXT NOT NULL,
  "git_url" TEXT DEFAULT NULL,
  "git_commit" TEXT DEFAULT NULL,
  PRIMARY KEY ("id")
);
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
CREATE TABLE "epoch" (
  "id" INTEGER,
  "index" TEXT DEFAULT NULL,
  "updates" TEXT DEFAULT NULL,
  "job_id" INTEGER NOT NULL,
  "job_experiment_id" INTEGER NOT NULL,
  "job_experiment_project_id" INTEGER NOT NULL,
  PRIMARY KEY ("id")
  CONSTRAINT "fk_epoch_job1" FOREIGN KEY ("job_id", "job_experiment_id", "job_experiment_project_id") REFERENCES "job" ("id", "experiment_id", "experiment_project_id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "examplemethod" (
  "id" INTEGER,
  "frequency" INTEGER NOT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "experiment" (
  "id" INTEGER,
  "repeat" INTEGER,
  "label" TEXT NOT NULL,
  "description" TEXT DEFAULT NULL,
  "project_id" INTEGER NOT NULL,
  "sample_id" INTEGER NOT NULL,
  "examplemethod_id" INTEGER NOT NULL,
  "network_id" INTEGER NOT NULL,
  "trainscript_id" INTEGER NOT NULL,
  "version_id" INTEGER NOT NULL,
  PRIMARY KEY ("id")
  CONSTRAINT "fk_experiment_project1" FOREIGN KEY ("project_id") REFERENCES "project" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_experiment_sample1" FOREIGN KEY ("sample_id") REFERENCES "sample" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_experiment_examplemethod1" FOREIGN KEY ("examplemethod_id") REFERENCES "examplemethod" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_experiment_network1" FOREIGN KEY ("network_id") REFERENCES "network" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_experiment_trainscript1" FOREIGN KEY ("trainscript_id") REFERENCES "trainscript" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_experiment_version1" FOREIGN KEY ("version_id") REFERENCES "version" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "job" (
  "id" INTEGER,
  "experiment_id" INTEGER NOT NULL,
  "experiment_project_id" INTEGER NOT NULL,
  "time_start" datetime DEFAULT NULL,
  "time_end" datetime DEFAULT NULL,
  "exit_status" INTEGER DEFAULT NULL,
  PRIMARY KEY ("id","experiment_id","experiment_project_id")
  CONSTRAINT "fk_job_experiment1" FOREIGN KEY ("experiment_id", "experiment_project_id") REFERENCES "experiment" ("id", "project_id") ON DELETE NO ACTION ON UPDATE NO ACTION
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
CREATE TABLE "network" (
  "id" INTEGER,
  "label" TEXT NOT NULL,
  "description" TEXT DEFAULT NULL,
  "path_to_in" TEXT DEFAULT NULL,
  "path_to_yaml" TEXT DEFAULT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "performance" (
  "id" INTEGER,
  "hit" INTEGER DEFAULT NULL,
  "miss" INTEGER DEFAULT NULL,
  "falsealarm" INTEGER DEFAULT NULL,
  "correctrejection" INTEGER DEFAULT NULL,
  "epoch_id" INTEGER NOT NULL,
  "epoch_job_id" INTEGER NOT NULL,
  "epoch_job_experiment_id" INTEGER NOT NULL,
  "epoch_job_experiment_project_id" INTEGER NOT NULL,
  PRIMARY KEY ("id")
  CONSTRAINT "fk_performance_epoch1" FOREIGN KEY ("epoch_id", "epoch_job_id", "epoch_job_experiment_id", "epoch_job_experiment_project_id") REFERENCES "epoch" ("id", "job_id", "job_experiment_id", "job_experiment_project_id") ON DELETE NO ACTION ON UPDATE NO ACTION
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
  CONSTRAINT "fk_phonology_has_phoneme_phoneme1" FOREIGN KEY ("phoneme_id") REFERENCES "grapheme" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
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
CREATE TABLE "project" (
  "id" INTEGER,
  "label" TEXT NOT NULL,
  "description" TEXT DEFAULT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "rule" (
  "id" INTEGER,
  "label" TEXT NOT NULL,
  "description" TEXT DEFAULT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "sample" (
  "id" INTEGER,
  "dialect_root_id" INTEGER NOT NULL,
  "dialect_alt_id" INTEGER NOT NULL,
  "accent_id" INTEGER NOT NULL,
  "n" INTEGER NOT NULL,
  "n_root_homophones" INTEGER NOT NULL,
  "n_root_homophonic_words" INTEGER NOT NULL,
  "n_alt_homophones" INTEGER NOT NULL,
  "n_alt_homophonic_words" INTEGER NOT NULL,
  "n_diff_root_alt" INTEGER NOT NULL,
  "p_rule_applied" double DEFAULT NULL,
  "child_of" INTEGER DEFAULT NULL,
  PRIMARY KEY ("id")
  CONSTRAINT "fk_sample_dialect1" FOREIGN KEY ("dialect_root_id", "dialect_alt_id") REFERENCES "dialect" ("id", "id") ON DELETE NO ACTION ON UPDATE NO ACTION
  CONSTRAINT "fk_sample_accent1" FOREIGN KEY ("accent_id") REFERENCES "accent" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "semrep" (
  "corpus_id" INTEGER NOT NULL,
  "word_id" INTEGER NOT NULL,
  "unit" INTEGER NOT NULL,
  "value" INTEGER NOT NULL,
  PRIMARY KEY ("corpus_id","word_id","unit")
  CONSTRAINT "fk_semrep_word1" FOREIGN KEY ("word_id", "corpus_id") REFERENCES "word" ("id", "corpus_id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "trainscript" (
  "id" INTEGER,
  "label" TEXT NOT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "weight" (
  "id" INTEGER,
  "basename" TEXT NOT NULL,
  "epoch_id" INTEGER NOT NULL,
  "epoch_job_id" INTEGER NOT NULL,
  "epoch_job_experiment_id" INTEGER NOT NULL,
  "epoch_job_experiment_project_id" INTEGER NOT NULL,
  PRIMARY KEY ("id")
  CONSTRAINT "fk_weight_epoch1" FOREIGN KEY ("epoch_id", "epoch_job_id", "epoch_job_experiment_id", "epoch_job_experiment_project_id") REFERENCES "epoch" ("id", "job_id", "job_experiment_id", "job_experiment_project_id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE "word" (
  "id" INTEGER,
  "word" TEXT NOT NULL,
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
CREATE INDEX "phonrep_fk_phonrep_phoneme1_idx" ON "phonrep" ("phoneme_id");
CREATE INDEX "phonrep_fk_phonrep_accent1_idx" ON "phonrep" ("accent_id");
CREATE INDEX "job_fk_job_experiment1_idx" ON "job" ("experiment_id","experiment_project_id");
CREATE INDEX "performance_fk_performance_epoch1_idx" ON "performance" ("epoch_id","epoch_job_id","epoch_job_experiment_id","epoch_job_experiment_project_id");
CREATE INDEX "epoch_fk_epoch_job1_idx" ON "epoch" ("job_id","job_experiment_id","job_experiment_project_id");
CREATE INDEX "weight_fk_weight_epoch1_idx" ON "weight" ("epoch_id","epoch_job_id","epoch_job_experiment_id","epoch_job_experiment_project_id");
CREATE INDEX "sample_has_example_fk_sample_has_example_sample1_idx" ON "sample_has_example" ("sample_id");
CREATE INDEX "sample_has_example_fk_sample_has_example_word1_idx" ON "sample_has_example" ("word_id");
CREATE INDEX "experiment_fk_experiment_project1_idx" ON "experiment" ("project_id");
CREATE INDEX "experiment_fk_experiment_trainscript1_idx" ON "experiment" ("trainscript_id");
CREATE INDEX "experiment_fk_experiment_version1_idx" ON "experiment" ("version_id");
CREATE INDEX "dialect_has_rule_fk_dialect_has_rule_rule1_idx" ON "dialect_has_rule" ("rule_id");
CREATE INDEX "dialect_has_rule_fk_dialect_has_rule_dialect_idx" ON "dialect_has_rule" ("dialect_id");
CREATE INDEX "word_fk_word_corpus1_idx" ON "word" ("corpus_id");
CREATE INDEX "phonology_has_rule_fk_phonology_has_rule_rule1_idx" ON "phonology_has_rule" ("rule_id");
CREATE INDEX "phonology_has_rule_fk_phonology_has_rule_phonology1_idx" ON "phonology_has_rule" ("phonology_id","word_id","dialect_id");
CREATE INDEX "phonology_has_rule_fk_phonology_has_rule_phonology1" ON "phonology_has_rule" ("phonology_id","dialect_id");
END TRANSACTION;