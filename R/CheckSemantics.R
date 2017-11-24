SEM <- list(
  deep=matrix(rep(0, 500*200), nrow=500,ncol=200),
  shallow=matrix(rep(0, 500*200), nrow=500,ncol=200)
)

for (i in seq(1,500)) {
  SEM$deep[i,] <- STIM$deep[[i]]$sem
  SEM$shallow[i,] <- STIM$shallow[[i]]$sem
}

rownames(SEM$deep) <- names(STIM$deep)
rownames(SEM$shallow) <- names(STIM$shallow)

SEMdist <- list(
  deep=dist(SEM$deep),
  shallow=dist(SEM$shallow)
)

tmp <- t(apply(as.matrix(SEMdist$deep), 1, function(x) order(order(x))))
tmpd <- apply(tmp, 1, function(x) which(x>1 & x<12))

tmp <- t(apply(as.matrix(SEMdist$shallow), 1, function(x) order(order(x))))
tmps <- apply(tmp, 1, function(x) which(x>1 & x<12))

x <- rep(0,1000)
Xs <- as.matrix(SEMdist$shallow)
Xd <- as.matrix(SEMdist$deep)
for ( i in seq(1,500) ) {
  ix <- tmps[,i]
  x[i] <- mean(Xs[ix,i])
  
  j <- i + 500
  ix <- tmpd[,i]
  x[j] <- mean(Xd[ix,i])
}
image(tmp)

SEMdistDF <- list(
  deep=as.data.frame(as.matrix(SEMdist$deep)),
  shallow=as.data.frame(as.matrix(SEMdist$shallow))
)
str(SEMdistDF$deep)
SEMdistDF$deep %>% 