ind2bin <- function(ind, n=NULL) {
  if (is.null(n)) {
    n <- log2(max(ind)+1)
  }
  
  # Taken from R.utils::intToBin 
  y <- as.integer(ind)
  class(y) <- "binmode"
  y <- as.character(y)
  dim(y) <- dim(ind)
  y
  
  return(do.call(rbind,strsplit(y,split='')) == "1")
}