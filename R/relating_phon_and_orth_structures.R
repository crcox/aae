word <- read.csv('raw/3k/words.csv', header=FALSE)[[1]]
phon <- as.matrix(read.csv('raw/3k/phon.csv', header=FALSE))
orth <- as.matrix(read.csv('raw/3k/orth.csv', header=FALSE))
rownames(phon) <- word
rownames(orth) <- word

DropUnusedColumns <- function(x) {
    z <- apply(x, 2, any)
    return(x[,z])
}

orth <- DropUnusedColumns(orth)
phon <- DropUnusedColumns(phon)

## Find samples where orthographic structure and phonological structure are
## correlated
n <- length(word)
highest_observed_correlation <- 0
most_similar_sample <- 0
d.phon <- as.matrix(dist(phon, method = "manhattan"))
d.orth <- as.matrix(dist(orth, method = "manhattan"))
sizes <- seq(100,1000,by=100)
RESULTS <- matrix(0, nrow=10, ncol=length(sizes))
tmp <- expand.grid(samplesize=c(100,200,300,400,500,600,700,800,900,1000),iteration=c(1:10))
tmp$condition <- factor(3,levels=1:3,labels=c('maximize','minimize','random'))
tmp$correlation <- numeric(100)
for ( k in seq(1,length(sizes) ) ){
  sample_size <- sizes[k]
  for ( j in seq(1,10) ) {
    ix <- sample(n, sample_size)
    # for ( i in seq(1,1000) ) {
    #   ix <- sample(n, sample_size)
      cc <- cor(
        as.dist(d.phon[ix,ix]),
        as.dist(d.orth[ix,ix])
      )
    #   if (cc > highest_observed_correlation) {
    #     most_similar_sample <- ix
    #     highest_observed_correlation <- cc
    #   }
    # }
      z <- (tmp$samplesize == sample_size) & tmp$iteration==j
      tmp$correlation[z] <- cc
    # RESULTS[j,k] <- highest_observed_correlation
  }
}

d.phon <- dist(phon[most_similar_sample,], method = "manhattan")
d.orth <- dist(orth[most_similar_sample,], method = "manhattan")

image(as.matrix(d.phon))
image(as.matrix(d.orth))

## Find samples where orthographic structure and phonological structure are
## **uncorrelated**
sample_size <- 200
n <- length(word)
lowest_observed_correlation <- 1
least_similar_sample <- 0
for ( i in seq(1,1000) ) {
    ix <- sample(n, sample_size)
    d.phon <- dist(phon[ix,], method = "manhattan")
    d.orth <- dist(orth[ix,], method = "manhattan")
    cc <- cor(d.phon,d.orth)
    if (cc < lowest_observed_correlation) {
        least_similar_sample <- ix
        lowest_observed_correlation <- cc
    }
}
d.phon <- dist(phon[least_similar_sample,], method = "manhattan")
d.orth <- dist(orth[least_similar_sample,], method = "manhattan")

image(as.matrix(d.phon))
image(as.matrix(d.orth))

ggplot(DD, aes(x=samplesize,y=correlation,color=condition)) +
  geom_point() +
  geom_point(data = group_by(DD,condition,samplesize) %>% summarize(correlation=mean(correlation)), size=3) +
  theme_bw(base_size = 16) + 
  ggtitle('Extreme correlation values by sample size', subtitle='Search budget per point: 10,000')
