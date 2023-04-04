setwd("/home/hugo/Dropbox/Forskning/GeophysAI/Hanna_Svennevik/Computations/ECClinreg")

options("width"=220)

library(parallel)

predictj = function(j) {
  MAEij = c(nhours)
  rm(envtrain,envtest)
  envtrain = as.data.frame(cbind(qtrain[i,j,], rtrain[i,j,], sptrain[i,j,], t2mtrain[i,j,]))
  colnames(envtrain) = c("q", "r", "sp", "t2m")
  envtest = as.data.frame(cbind(qtest[i,j,], rtest[i,j,], sptest[i,j,], t2mtest[i,j,]))
  colnames(envtest) = c("q", "r", "sp", "t2m")
  reg = lm(tcctrain[i,j,] ~ q + r + sp + t2m, data = envtrain, na.action=na.omit)
  tccpred = predict(object=reg, newdata=envtest)
  AE = abs(tccpred - tcctest[i,j,])
  MAEij = rowMeans(matrix(AE, nrow = nhours), na.rm = TRUE)
  return(MAEij)
}

nrow = 161
ncol = 81

cat("Load q...\n")
load(file = "/home/hugo/ECCRdata/ql.Rdata")
qtrain = ql[[1]]
qtest = ql[[2]]
rm(ql)

cat("Load r...\n")
load(file = "/home/hugo/ECCRdata/rl.Rdata")
rtrain = rl[[1]]
rtest = rl[[2]]
rm(rl)

cat("Load sp...\n")
load(file = "/home/hugo/ECCRdata/spl.Rdata")
sptrain = spl[[1]]
sptest = spl[[2]]
rm(spl)

cat("Load t2m...\n")
load(file = "/home/hugo/ECCRdata/t2ml.Rdata")
t2mtrain = t2ml[[1]]
t2mtest = t2ml[[2]]
rm(t2ml)

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

save(MAE, file = "MAEOnlyCurrent.Rdata")

apply(MAE,3,mean)
