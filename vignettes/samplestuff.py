#!/usr/bin/env python
import os,json,pickle,sys
import sqlite3
import string
import aae
import aae.sql
import timeit
from aae.accents import standard as PHON_MAP
from aae.semantics import standard_3k as SEM_MAP

db_name = "./aae_base.db"
conn = sqlite3.connect(db_name)
conn.row_factory = sqlite3.Row
#print "insert and generate"
#starttime = timeit.default_timer()
#aae.sql.insert.sample(conn,
#    corpus="3k",
#    dialect_root="SAE",
#    dialect_alt="AAE",
#    accent="standard",
#    alphabet="orthogonal",
#    n=500,
#    ndiff=250,
#    nhomo_root=20)
#print timeit.default_timer() - starttime
#
### A sample can be explicitly defined.
#with open("original_stimlist_500_250.txt", "r") as f:
#    stimlist=[x.strip() for x in f.readlines()]
#
## If building from a pre-defined list of words, counts will be derived and so
## you do not have to specify them. Also, note that the return value for the
## function is the sample id of the newly-added sample. This can be used to
## facilitate generating child samples.
#print "insert from list"
#starttime = timeit.default_timer()
#aae.sql.insert.sample(conn,
#    corpus="3k",
#    dialect_root="SAE",
#    dialect_alt="AAE",
#    accent="standard",
#    alphabet="orthogonal",
#    list_stim=stimlist)
#print timeit.default_timer() - starttime
#
## A child sample inherits everything from the parent, but with rules for
## obtaining alternate pronunciations applied only a specified proportion of the
## time. Allows for the number of differences between dialects in the sample to
## be manipulated holding everything else constant.
#print "insert child"
#starttime = timeit.default_timer()
#aae.sql.insert.childsample(conn, 2, 0.75)
#print timeit.default_timer() - starttime

print "select sample"
starttime = timeit.default_timer()
aae.sql.select.sample(conn, 1)
print timeit.default_timer() - starttime

conn.close()
