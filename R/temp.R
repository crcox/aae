library(jsonlite)
library(plyr);library(dplyr)
library(ggplot2)

source('R/bin2factor.R')
source('R/bin2ind.R')

root <- file.path('models')
models <- c("AAE_deep_phonWS2sem","AAE_shallow_phonWS2sem","SAE_deep_phonWS2sem","SAE_shallow_phonWS2sem")

MList <- list()
for ( m in models ) {
  print(m)
  mpath <- file.path(root,m)
  MList[[m]] <- list()
  for ( i in 1:10 ) {
    dpath <- file.path(mpath,'TRAINING',sprintf('%03d',i-1),'phase01_ErrAccRT.csv')
    if ( file.exists(dpath) ) {
      d <- read.csv(dpath, header=F)  
    } else {
      warning(dpath, " does not exist.")
    }
    
    names(d) <- c('epoch','GroupNo','GroupName','ExNo','Key','ExName','InputType','OutputType','RT','ErrRT','Acc','Proportion')
    d$model <- m
    d$iter <- i
    d$depth <- strsplit(m,split='_')[[1]][2]
    print(ncol(d))
    MList[[m]][[i]] <- d
    rm(d)
  }
}
# 
Mdf <- rbind(
  MList[["AAE_deep_phonWS2sem"]][[1]],
  MList[["AAE_deep_phonWS2sem"]][[2]],
  MList[["AAE_deep_phonWS2sem"]][[3]],
  MList[["AAE_deep_phonWS2sem"]][[4]],
  MList[["AAE_deep_phonWS2sem"]][[5]],
  MList[["AAE_deep_phonWS2sem"]][[6]],
  MList[["AAE_deep_phonWS2sem"]][[7]],
  MList[["AAE_deep_phonWS2sem"]][[8]],
  MList[["AAE_deep_phonWS2sem"]][[9]],
  MList[["AAE_deep_phonWS2sem"]][[10]],
  MList[["AAE_shallow_phonWS2sem"]][[1]],
  MList[["AAE_shallow_phonWS2sem"]][[2]],
  MList[["AAE_shallow_phonWS2sem"]][[3]],
  MList[["AAE_shallow_phonWS2sem"]][[4]],
  MList[["AAE_shallow_phonWS2sem"]][[5]],
  MList[["AAE_shallow_phonWS2sem"]][[6]],
  MList[["AAE_shallow_phonWS2sem"]][[7]],
  MList[["AAE_shallow_phonWS2sem"]][[8]],
  MList[["AAE_shallow_phonWS2sem"]][[9]],
  MList[["AAE_shallow_phonWS2sem"]][[10]],
  MList[["SAE_shallow_phonWS2sem"]][[1]],
  MList[["SAE_shallow_phonWS2sem"]][[2]],
  MList[["SAE_shallow_phonWS2sem"]][[3]],
  MList[["SAE_shallow_phonWS2sem"]][[4]],
  MList[["SAE_shallow_phonWS2sem"]][[5]],
  MList[["SAE_shallow_phonWS2sem"]][[6]],
  MList[["SAE_shallow_phonWS2sem"]][[7]],
  MList[["SAE_shallow_phonWS2sem"]][[8]],
  MList[["SAE_shallow_phonWS2sem"]][[9]],
  MList[["SAE_shallow_phonWS2sem"]][[10]],
  MList[["SAE_deep_phonWS2sem"]][[1]],
  MList[["SAE_deep_phonWS2sem"]][[2]],
  MList[["SAE_deep_phonWS2sem"]][[3]],
  MList[["SAE_deep_phonWS2sem"]][[4]],
  MList[["SAE_deep_phonWS2sem"]][[5]],
  MList[["SAE_deep_phonWS2sem"]][[6]],
  MList[["SAE_deep_phonWS2sem"]][[7]],
  MList[["SAE_deep_phonWS2sem"]][[8]],
  MList[["SAE_deep_phonWS2sem"]][[9]],
  MList[["SAE_deep_phonWS2sem"]][[10]]
)

# MDF <- ldply(do.call(c, unlist(MList, recursive=FALSE)))
# MDF$.id <- NULL
Mdf$depth <- as.factor(as.character(Mdf$depth))
Mdf$ExName <- as.factor(as.character(Mdf$ExName))

STIM <- list(
  shallow=fromJSON('stimuli/AAE_shallow/json/words_pruned.json'),
  deep=fromJSON('stimuli/AAE_deep/json/words_pruned.json')
)

HOMO <- list(
  shallow=fromJSON('stimuli/AAE_shallow/json/homo.json'),
  deep=fromJSON('stimuli/AAE_deep/json/homo.json')
)
# Find first used phon slot
P <- STIM$deep[[1]]$phon # any stim will do
m <- match(TRUE,sapply(P,length)>0)
n <- match(FALSE,sapply(P[m:length(P)],length)>0) - m
# Trim phon-codes that are the homophone keys
names(HOMO$deep) <- substr(names(HOMO$deep),start=m,stop=n)
names(HOMO$deep) <- substr(names(HOMO$deep),start=m,stop=n)

P <- STIM$shallow[[1]]$phon # any stim will do
m <- match(TRUE,sapply(P,length)>0)
n <- match(FALSE,sapply(P[m:length(P)],length)>0) - m
# Trim phon-codes that are the homophone keys
names(HOMO$shallow) <- substr(names(HOMO$shallow),start=m,stop=n)
names(HOMO$shallow) <- substr(names(HOMO$shallow),start=m,stop=n)

wordInfo <- data.frame(ExName=c(names(STIM$deep),names(STIM$shallow)),Homo=FALSE, CCR=FALSE, PVR=FALSE, DEV=FALSE)
for (i in 1:length(STIM$deep)) {
  S = STIM$deep[[i]]
  phon_code = paste(S$phon_code, collapse='')
  wordInfo$Homo[i] <- !is.null(HOMO$deep[[phon_code]])
  wordInfo$CCR[i] <- S$consonant_cluster_reduction
  wordInfo$PVR[i] <- S$postvocalic_reduction
  wordInfo$DEV[i] <- S$devoiced
  wordInfo$depth[i] <- 'deep'
}
for (i in 1:length(STIM$shallow)) {
  j = i + length(STIM$deep)
  S = STIM$shallow[[i]]
  phon_code = paste(S$phon_code, collapse='')
  wordInfo$Homo[j] <- !is.null(HOMO$shallow[[phon_code]])
  wordInfo$CCR[j] <- S$consonant_cluster_reduction
  wordInfo$PVR[j] <- S$postvocalic_reduction
  wordInfo$DEV[j] <- S$devoiced
  wordInfo$depth[i] <- 'shallow'
}
wordInfo$depth <- as.factor(as.character(wordInfo$depth))
wordInfo$ExName <- as.factor(as.character(wordInfo$ExName))


wordInfo$Changes <- bin2factor(wordInfo[,c('DEV','PVR','CCR')])
wordInfo$Homo <- as.factor(wordInfo$Homo)

tmp <- left_join(Mdf,wordInfo)
as.tbl(tmp)
as.tbl(Mdf)

MTbl <- Mdf %>% group_by(model,epoch, iter) %>% 
  summarize(Acc=mean(Acc)) %>%
  ungroup() %>% group_by(model,epoch) %>%
  summarize(SEErr=sd(Acc)/sqrt(n()),Acc=mean(Acc),MedianAcc=median(Acc)) %>%
#   group_by(model) %>% filter(epoch==max(epoch))

MTbl
png("LearningCurve.png", width=1500, height=1000, res=150)
ggplot(filter(MTbl,epoch>0), aes(x=epoch,y=Acc,fill=model)) +
  geom_ribbon(aes(ymin=Acc-SEErr,ymax=Acc+SEErr),alpha=0.3) +
  geom_line(aes(color=model)) +
  theme_bw(base_size = 18) + ggtitle("Model accuracy by training cycle")
dev.off()

MTTD <- Mdf %>% group_by(model, iter) %>% 
  summarize(n=n()) %>%
  group_by(model) %>% 
  summarize(stderr=sd(n)/sqrt(n()), n=mean(n))
  
MTTD$language <- factor(c(1,1,2,2), levels=c(1,2), labels=c('AAE','SAE'))
MTTD$depth <- factor(c(1,2,1,2), levels=c(1,2), labels=c('deep','shallow'))
png('time_to_done.png', height=1000, width=800, res=150)
ggplot(MTTD, aes(x=depth, y=n, fill=language)) + geom_bar(stat='identity', position='dodge') + ggtitle('Number of train cycles to criterion') +theme_bw(base_size = 18)
dev.off()

ggplot(filter(d,(epoch %% 1e5)==0), aes(x=epoch,y=Proportion,color=Changes)) + stat_summary(fun.y=mean,geom="point") + coord_cartesian(ylim=c(0,0.01))

ggplot(filter(d,(epoch %% 1e5)==0), aes(x=epoch,y=Proportion,color=Homo)) + stat_summary(fun.y=mean,geom="point") + coord_cartesian(ylim=c(0,0.01))
