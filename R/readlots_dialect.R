root <- file.path("models","BothWays","250")
stopifnot(file.exists(root))

A <- c("Blocked","Interleaved")
B <- c("standard") # weak not run
C <- c("Both")
D <- 0:9

n <- 50000
DF <- data.frame(epoch=numeric(n),condition=character(n), dialect=character(n), accent=character(n), iter=numeric(n), teston=character(n), input=character(n), output=character(n), sensspec=numeric(n), error=numeric(n), stringsAsFactors = F)
M <- expand.grid(iter=D,dialect=C,accent=B,condition=A)
i = 0
for (r in 1:nrow(M)) {
  m <- M[r,]
  fpath <- file.path(root,M$condition[r],M$iter[r],"phase01_MFHC.csv")
  stopifnot(file.exists(fpath))
  print(fpath)
  f <- file(fpath,'r')
  ctr = 0
  epoch = 0
  while (TRUE) {
    lines <- readLines(f,500)
    if (length(lines)<500) {break}
    i = i + 1
    df <- read.csv(textConnection(lines),header=F)
    error <- ((df[,11]/(df[,9]+df[,11])) - (df[,10]/(df[,10]+df[,12]))) < 1
    miss <- sum(df[,9])
    fp <- sum(df[,10])
    hit <- sum(df[,11])
    cr <- sum(df[,12])
    DF[i,"epoch"] <- epoch
    DF[i,"condition"] <- as.character(M$condition[r])
    DF[i,"dialect"] <- as.character(M$dialect[r])
    DF[i,"accent"] <- as.character(M$accent[r])
    DF[i,"iter"] <- M$iter[r]
    DF[i,"sensspec"] <- (hit/(hit+miss)) - (fp/(fp+cr))
    DF[i,"error"] <- mean(error)
    STEP = ctr %% 8
    if (STEP==0) {
      DF[i,"dialect"] <- "SAE"
      DF[i,"teston"] <- "SAE"
      DF[i,"input"] <- "phon"
      DF[i,"output"] <- "phon"
    } else if (STEP==1) {
      DF[i,"dialect"] <- "SAE"
      DF[i,"teston"] <- "SAE"
      DF[i,"input"] <- "sem"
      DF[i,"output"] <- "phon"
    } else if (STEP==2) {
      DF[i,"dialect"] <- "AAE"
      DF[i,"teston"] <- "AAE"
      DF[i,"input"] <- "phon"
      DF[i,"output"] <- "phon"
    } else if (STEP==3) {
      DF[i,"dialect"] <- "AAE"
      DF[i,"teston"] <- "AAE"
      DF[i,"input"] <- "sem"
      DF[i,"output"] <- "phon"
    } else if (STEP==4) {
      DF[i,"dialect"] <- "SAE"
      DF[i,"teston"] <- "SAE"
      DF[i,"input"] <- "phon"
      DF[i,"output"] <- "sem"
    } else if (STEP==5) {
      DF[i,"dialect"] <- "SAE"
      DF[i,"teston"] <- "SAE"
      DF[i,"input"] <- "sem"
      DF[i,"output"] <- "sem"
    } else if (STEP==6) {
      DF[i,"dialect"] <- "AAE"
      DF[i,"teston"] <- "AAE"
      DF[i,"input"] <- "phon"
      DF[i,"output"] <- "sem"
    } else {
      DF[i,"dialect"] <- "AAE"
      DF[i,"teston"] <- "AAE"
      DF[i,"input"] <- "sem"
      DF[i,"output"] <- "sem"
      epoch = epoch + 1
    }
    ctr <- ctr + 1
  }
  close(f)
}
DF2 <- DF[''!=DF$condition,]
DF2$condition <- as.factor(DF2$condition)
DF2$dialect <- as.factor(DF2$dialect)
DF2$accent <- as.factor(DF2$accent)
DF2$output <- as.factor(DF2$output)
DF2$input <- as.factor(DF2$input)
DF2$teston <- as.factor(DF2$teston)

DIALECT <- DF2
