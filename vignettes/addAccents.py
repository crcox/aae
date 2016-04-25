import sqlite3
import aae
import aae.sql
from aae.accents import weak as WEAK_MAP
from aae.accents import strong as STRONG_MAP
conn = sqlite3.connect('../aae/database/main.db')
conn.row_factory = sqlite3.Row

aae.sql.insert.accent(conn, "weak", "Vowels altered.", phonmap=WEAK_MAP)
aae.sql.insert.accent(conn, "strong", "Vowels and consonants altered.", phonmap=STRONG_MAP)
