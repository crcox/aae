bin2factor <- function(df) {
  items <- character()
  for (i in 1:nrow(df)) {
    z <- as.logical(df[i,])
    if ( any(z) ) {
      items <- append(items,paste(names(df)[z], sep="+"))
    } else {
      items <- append(items,'none')
    }
  }
  return(as.factor(items))
}