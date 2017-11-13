library(RSQLite)
library(dplyr)
library(ggplot2)

## Establish connection to db
stimDB <- dbConnect(SQLite(), "./database/aae2.db");
dbGetInfo(stimDB)
dbIsValid(stimDB)
dbListTables(stimDB)
if (dbExistsTable(stimDB, "word")) {
  dbListFields(stimDB, "word")  
}

## Load results
d <- rbind(
  read.csv('models/BothWays/250/AAE/phase01_MFHC.csv', header=F),
  read.csv('models/BothWays/250/SAE/phase01_MFHC.csv', header=F)
)
nl <- rbind(
  read.csv('models/BothWays/250/AAE/phase01_MFHC_nlines.csv', header=F),
  read.csv('models/BothWays/250/SAE/phase01_MFHC_nlines.csv', header=F)
)
nl$L1 <- rep(c("AAE","SAE"), c(25,21))
d$iteration = 0;
d$iteration[d$L1 == "AAE"] <- rep(seq(1,25), nl$V1[nl$L1 == "AAE"])
d$iteration[d$L1 == "SAE"] <- rep(seq(1,21), nl$V1[nl$L1 == "SAE"])

names(d) <-
  c("iteration","epoch","groupnumber","grouplabel","index","L1",
    "word","input","output","miss","falsealarm","hit","correctrejection")
head(d)

## Compute sensitivity
nt <-d$hit+d$miss
nf <-d$falsealarm+d$correctrejection
d$sens <- (d$hit/nt) - (d$falsealarm/nf)
rm(nt, nf)

## Extract word list
words <- as.character(unique(d$word))

## Phoneme frequency by condition
phonology <- PHONREP(stimDB, words = words, languages = '*');
phonology <- phonology %>%
  group_by(word,label,phoneme) %>%
  summarize() %>%
  group_by(word,label) %>%
  mutate(
    index=1:n(),
    phoneme2=c(phoneme[2:n()],'-')
  )
phonemeFreq <- xtabs(~as.factor(phoneme)+index,data=phonology)

bigramFreq <- xtabs(~as.factor(phoneme)+as.factor(phoneme2),data=phonology)

phonemeProb <- t(t(phonemeFreq) / colSums(phonemeFreq))
bigramProb <- t(t(bigramFreq) / colSums(bigramFreq))

phonology$freq <- mapply(function(x,y) phonemeFreq[x,y], phonology$phoneme, phonology$index)
phonology$prob <- mapply(function(x,y) phonemeProb[x,y], phonology$phoneme, phonology$index)

## Words that are not perfectly learned by epoch
countNotLearned <- d %>%
  group_by(epoch, L1, grouplabel, input, word) %>%
  summarize(learned=all(sens==1)) %>%
  filter(!learned) %>%
  group_by(epoch,L1,grouplabel,input) %>%
  summarize(notLearned=n())

notLearned <- d %>%
  group_by(epoch, L1, word, grouplabel,input) %>%
  summarize(learned=all(sens==1)) %>%
  filter(!learned)

countPhonRep <- PHONREP(stimDB, words = words, languages = '*') %>%
  group_by(word,label) %>% summarize(n=sum(value==1)) %>% ungroup() %>%
  rename(L1=label) %>% mutate(word=as.factor(word),L1=as.factor(L1))

countPhoneme <- PHONREP(stimDB, words = words, languages = '*') %>%
  group_by(word,label,phoneme) %>% summarize() %>%
  group_by(word,label) %>% summarize(n=sum(phoneme!='-')) %>% ungroup() %>%
  rename(L1=label) %>% mutate(word=as.factor(word),L1=as.factor(L1))

wordsWithNPhonemes <- countPhoneme %>% group_by(L1,n) %>% summarize(wordsWithNPhonemes=n()) %>% ungroup() %>% mutate(L1=as.factor(L1))
wordsWithNPhonRep <- countPhonRep %>% group_by(L1,n) %>% summarize(wordsWithNPhonRep=n()) %>% ungroup() %>% mutate(L1=as.factor(L1))

ggplot(countNotLearned, aes(x=epoch, y=notLearned, color=L1)) + geom_line() + facet_grid(input~grouplabel)

tbl <- left_join(notLearned,countPhoneme) %>%
  group_by(epoch,L1,grouplabel,input,n) %>%
  summarize(notLearned=n())

tbl <- left_join(tbl, wordsWithNPhonemes)

ggplot(filter(tbl,L1=="AAE"), aes(x=epoch, y=notLearned/wordsWithNPhonemes, group=n, color=n)) + geom_line() + facet_grid(input~grouplabel) + ggtitle("AAE")
ggplot(filter(tbl,L1=="SAE"), aes(x=epoch, y=notLearned/wordsWithNPhonemes, group=n, color=n)) + geom_line() + facet_grid(input~grouplabel) + ggtitle("SAE")

## Visualize words
notLearned$r <- runif(nrow(notLearned))
ggplot(filter(notLearned,input=="sem",grouplabel=="PhonOutput", L1=="SAE",epoch>60000), aes(x=epoch,y = r)) + geom_text(aes(label=word), position='jitter')



## Disconnect from db
dbDisconnect(stimDB)
