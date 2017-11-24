library(jsonlite)
library(dplyr)
library(ggplot2)
setwd('AAE/000')

d <- read.csv('1/phase01_ErrAccRT.csv',header=F)
save(d,file='1/phase01_ErrAccRT.Rdat')
load('1/phase01_ErrAccRT.Rdat')

head(d)
names(d) <- c('epoch','GroupNo','GroupName','ExNo','Key','ExName','InputType','OutputType','V9','V10','V11','Proportion')

STIM <- fromJSON('../stimuli/AAE/json/words_pruned.json')
HOMO <- fromJSON('../stimuli/AAE/json/homo.json')
# Find first used phon slot
P <- STIM[[1]]$phon # any stim will do
m <- match(TRUE,sapply(P,length)>0)
n <- match(FALSE,sapply(P[m:length(P)],length)>0) - m
# Trim phon-codes that are the homophone keys
names(HOMO) <- substr(names(HOMO),start=m,stop=n)

wordInfo <- data.frame(ExName=names(STIM),Homo=FALSE, CCR=FALSE, PVR=FALSE, DEV=FALSE)
for (i in 1:length(STIM)) {
  S = STIM[[i]]
  phon_code = paste(S$phon_code, collapse='')
  wordInfo$Homo[i] <- !is.null(HOMO[[phon_code]])
  wordInfo$CCR[i] <- S$consonant_cluster_reduction
  wordInfo$PVR[i] <- S$postvocalic_reduction
  wordInfo$DEV[i] <- S$devoiced
}

wordInfo$Changes <- bin2factor(wordInfo[,c('DEV','PVR','CCR')])
wordInfo$Homo <- as.factor(wordInfo$Homo)

d <- left_join(d,wordInfo)

ggplot(filter(d,(epoch %% 1e5)==0), aes(x=epoch,y=Proportion,color=Changes)) + geom_point() + coord_cartesian(ylim=c(0,0.05))

ggplot(filter(d,(epoch %% 1e5)==0), aes(x=epoch,y=Proportion,color=Changes)) + stat_summary(fun.y=mean,geom="point") + coord_cartesian(ylim=c(0,0.01))

ggplot(filter(d,(epoch %% 1e5)==0), aes(x=epoch,y=Proportion,color=Homo)) + stat_summary(fun.y=mean,geom="point") + coord_cartesian(ylim=c(0,0.01))

