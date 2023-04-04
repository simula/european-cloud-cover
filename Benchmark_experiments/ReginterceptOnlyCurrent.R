setwd("/home/hugo/Dropbox/Forskning/GeophysAI/Hanna_Svennevik/Computations/ECClinreg")

#setwd("C:/Users/hugoh/Dropbox (Simula)/Forskning/GeophysAI/Hanna_Svennevik/Computations/ECClinreg")


options("width"=220)

library(parallel)

predictj = function(j) {
  MAEij = c(nhours)
  tccpred = mean(tcctrain[i,j,], na.rm = TRUE)
  AE = abs(tccpred - tcctest[i,j,])
  MAEij = rowMeans(matrix(AE, nrow = nhours), na.rm = TRUE)
  return(MAEij)
}

nrow = 161
ncol = 81

cat("Load tcc...\n")
load(file = "/home/hugo/ECCRdata/tccl.Rdata")
tcctrain = tccl[[1]]
tcctest2 = tccl[[2]]
rm(tccl)

cat("Reload tcctest with NA...\n")
load(file = "/home/hugo/ECCRdata/tcctestwithNA.Rdata")

nhours = 24
ntrain = dim(tcctrain)[3]
ntest = dim(tcctest)[3]
envtrain = 0
envtest = 0

MAE = array(dim = c(nrow, ncol, nhours))

cat("Start training and prediction in each geographic location...\n")
for(i in 1:nrow) {
  cat("i =", i, "of", nrow, "\n")
  retur = mclapply(1:ncol, predictj, mc.cores = 41)
  #save(retur, file = paste("retur", i, ".Rdata", sep = ""))
  for(j in 1:ncol) {
    MAE[i,j,] = retur[[j]]
  }
}

save(MAE, file = "MAEinterceptOnlyCurrent.Rdata")

apply(MAE,3,mean)

apply(MAE,c(1,2),mean)

write.table(data, file = "MAElinreg.txt", col.names = F, row.names = F, sep = ",")

