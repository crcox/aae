DROP TABLE "performance";
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
