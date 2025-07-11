
r <- c(T,F,F,NA)
print(any(r==T))
print(any(is.na(r)))
print(length(which(is.na(r)==T)))

print(paste(r[1]))
