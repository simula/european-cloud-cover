setwd("/home/hugo/Dropbox/Forskning/GeophysAI/Hanna_Svennevik/Computations/ECClinreg")

options("width"=220)

library(parallel)

predictj = function(j) {
  MAEij = c(seqlen+1)
  #rm(envtrain,envtest)
  #envtrain = as.data.frame(cbind(qtrain[i,j,], rtrain[i,j,], sptrain[i,j,], t2mtrain[i,j,]))
  #colnames(envtrain) = c("q", "r", "sp", "t2m")
  #envtest = as.data.frame(cbind(qtest[i,j,], rtest[i,j,], sptest[i,j,], t2mtest[i,j,]))
  #colnames(envtest) = c("q", "r", "sp", "t2m")
  for(h in 0:seqlen) {
    #reg = lm(tcctrain[i,j,1:(ntrain-seqlen)+h] ~ 1, na.action=na.omit)
    #tccpred = predict(object=reg, newdata=envtest[1:(ntest-seqlen),])
    #tccpred = runif(length(tcctest[i,j,1:(ntest-seqlen)+h]))
    tccpred = mean(tcctrain[i,j,1:(ntrain-seqlen)+h], na.rm = TRUE)
    MAEij[h+1] = mean(abs(tcctest[i,j,1:(ntest-seqlen)+h] - tccpred), na.rm = TRUE)
  }
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

seqlen = 24
ntrain = dim(tcctrain)[3]
ntest = dim(tcctest)[3]
envtrain = 0
envtest = 0

MAE = array(dim = c(nrow, ncol, seqlen+1))

cat("Start training and prediction in each geographic location...\n")
for(i in 1:nrow) {
  cat("i =", i, "of", nrow, "\n")
  retur = mclapply(1:ncol, predictj, mc.cores = 41)
  #save(retur, file = paste("retur", i, ".Rdata", sep = ""))
  for(j in 1:ncol) {
    MAE[i,j,] = retur[[j]]
  }
}

save(MAE, file = "MAEintercept.Rdata")

apply(MAE,3,mean)

