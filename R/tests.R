library(jsonlite)
library(plyr);library(dplyr)
library(ggplot2)
library(reshape2)

source('R/bin2factor.R')
source('R/bin2ind.R')

root <- file.path('models')
models <- c("AAE_deep_phonWS2sem","AAE_shallow_phonWS2sem","SAE_deep_phonWS2sem","SAE_shallow_phonWS2sem")
tests <- c(file.path("dialect","weak"), file.path("dialect","strong"), file.path("language"))

MList <- list()
for ( m in models ) {
  print(m)
  mpath <- file.path(root,m)
  MList[[m]] <- list()
  for ( t in tests ) {
    tpath <- file.path(mpath,"TESTS",t)
    MList[[m]][[t]] <- list()
    for ( i in 1:10 ) {
      dpath <- file.path(tpath,sprintf('%03d',i-1),'phase01_ErrAccRT.csv')
      if ( file.exists(dpath) ) {
        d <- read.csv(dpath, header=F)  
      } else {
        warning(dpath, " does not exist.")
        next
      }
      
      names(d) <- c('epoch','GroupNo','GroupName','ExNo','Key','ExName','InputType','OutputType','RT','ErrRT','Acc','Proportion')
      d$model <- m
      d$iter <- i
      d$parent <- strsplit(m,split='_')[[1]][1]
      d$depth <- strsplit(m,split='_')[[1]][2]
      d$test <- t
      MList[[m]][[t]][[i]] <- d
      rm(d)
    }
  }
} 

warnings()

# Nested list to data.frame
MDF <- ldply(do.call(c, unlist(MList, recursive=FALSE)))
MDF$.id <- NULL
as.tbl(MDF)

MTbl <- MDF %>%
  group_by(model,test,iter) %>%
  filter(epoch==min(epoch)) %>%
  ungroup() %>%
  group_by(epoch,parent,depth,test) %>%
  summarize(Acc=mean(Acc))

png('test_acc.png', height=1000, width=1500, res=150)
ggplot(MTbl, aes(x=test, y=Acc, fill=depth)) + geom_bar(stat='identity', position='dodge') + coord_cartesian(ylim=c(.8,.9)) + facet_wrap("parent") + theme_bw(base_size = 18)
dev.off()
