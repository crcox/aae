WORDS <- function(db) {
  query <- "SELECT word FROM word";
  return(dbGetQuery(db,query));
}

WORDSvec <- function(db) {
  return(WORDS(db)[[1]]);
}

PHONREP <- function(db, words, languages='*') {
  queryVec <- c(
    "SELECT word.word,language.label,phoneme.phoneme,phonrep.value",
    "FROM phonmap",
    "JOIN phonology ON phonmap.phonology_id  = phonology.id",
    "JOIN phonrep   ON phonmap.phoneme_id    = phonrep.phoneme_id",
    "JOIN phoneme   ON phonmap.phoneme_id    = phoneme.id",
    "JOIN word      ON phonology.word_id     = word.id",
    "JOIN language  ON phonology.language_id = language.id"
  );
  
  wstr <- paste(sprintf("\"%s\"", words), sep = " ", collapse = ",")
  if (words[1]=='*') {whereWord = ''}
  else if (length(words)>1) {whereWord <- sprintf("WHERE word.word IN (%s)", wstr);}
  else {whereWord <- sprintf("WHERE word.word == %s", wstr);}
  queryVec <- append(queryVec, whereWord)
  
  lstr <- paste(sprintf("\"%s\"", languages), sep = " ", collapse = ",")
  if (languages[1]=='*') {whereLang = ''}
  else if (length(languages)>1) {whereLang <- sprintf("AND WHERE language.label IN (%s)", lstr);}
  else {whereLang <- sprintf("AND language.label == %s", lstr);}
  queryVec <- append(queryVec, whereLang)
  
  query <- paste(queryVec, sep = " ", collapse = " ");
  query <- gsub("\\s+", " ", query); # strip extra whitespace
  return(dbGetQuery(db,query));
}