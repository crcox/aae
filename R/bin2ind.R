bin2ind <- function(x) {
  M <- as.matrix(x)
  n <- ncol(M)
  b <- matrix(rev(2^seq(0,n-1)),nrow=n)
  return(M%*%b)
}