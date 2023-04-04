setwd("/home/hugo/Dropbox/Forskning/GeophysAI/Hanna_Svennevik/Computations/ECClinreg")

options("width"=220)

library(ncdf4)
library(abind)

path = "/home/hugo/ECC/"
months. = c("01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12")
ndays = c(31,28,31,30,31,30,31,31,30,31,30,31)
leapyears = c(2004,2008,2012,2016)

loadvar = function(vbl) {
  vbltrainM = c()
  for(year in 2004:2013) {
    if(year %in% leapyears) {
      ndays[2] = 29
    } else {
      ndays[2] = 28    
    }
    for(month in 1:12) {
      cat(vbl, "_", year, "_", months.[month], "\n", sep = "")
      if(!(year == 2004 & month <= 3)) {
        filename = paste(path, year, "_", months.[month], "_", vbl, ".nc", sep = "")
        file.nc = nc_open(filename)
        if(vbl == 'tcc') {
          content = ncvar_get(file.nc, 'tcc')
        } else {
          content = ncvar_get(file.nc)
        }
        ntimedata = dim(content)[3]
        ntime = ndays[month]*24
        if(ntimedata != ntime) {
          alltimes = 1:ntime
          if(vbl == 'tcc') {
            time. = ncvar_get(file.nc, 'time')+1
            content2 = array(dim = c(nrow,ncol,ntime))
            content2[,,time.] = content
            content2[,,!(alltimes %in% time.)] = mean(content, na.rm = TRUE)
            content = content2
            rm(content2)
          } else {
            cat("Something wrong with dimensions also for ERA5. Terminate program...\n")
            break
          }
        }
        vbltrainM = abind(vbltrainM, content)
        nc_close(file.nc)
      }
    }
  }
  vbltestM = c()
  for(year in 2014:2018) {
    if(year %in% leapyears) {
      ndays[2] = 29
    } else {
      ndays[2] = 28    
    }
    for(month in 1:12) {
      cat(vbl, "_", year, "_", months.[month], "\n", sep = "")
      filename = paste(path, year, "_", months.[month], "_", vbl, ".nc", sep = "")
      file.nc = nc_open(filename)
      if(vbl == 'tcc') {
        content = ncvar_get(file.nc, 'tcc')
      } else {
        content = ncvar_get(file.nc)
      }
      ntimedata = dim(content)[3]
      ntime = ndays[month]*24
      if(ntimedata != ntime) {
        alltimes = 1:ntime
        if(vbl == 'tcc') {
          time. = ncvar_get(file.nc, 'time')+1
          content2 = array(dim = c(nrow,ncol,ntime))
          content2[,,time.] = content
          content2[,,!(alltimes %in% time.)] = mean(content, na.rm = TRUE)
          content = content2
          rm(content2)
        } else {
          cat("Something wrong with dimensions also for ERA5. Terminate program...\n")
          break
        }
      }
      vbltestM = abind(vbltestM, content)
      nc_close(file.nc)
    }
  }
  return(list(vbltrainM,vbltestM))
}

nrow = 161
ncol = 81

cat("Load q...\n")
vbl = "q"
ql = loadvar(vbl)
save(ql, file = "/home/hugo/ECCRdata/ql.Rdata")
qtrain = ql[[1]]
qtest = ql[[2]]

cat("Load r...\n")
vbl = "r"
rl = loadvar(vbl)
save(rl, file = "/home/hugo/ECCRdata/rl.Rdata")
rtrain = rl[[1]]
rtest = rl[[2]]

cat("Load sp...\n")
vbl = "sp"
spl = loadvar(vbl)
save(spl, file = "/home/hugo/ECCRdata/spl.Rdata")
sptrain = spl[[1]]
sptest = spl[[2]]

cat("Load t2m...\n")
vbl = "t2m"
t2ml = loadvar(vbl)
save(t2ml, file = "/home/hugo/ECCRdata/t2ml.Rdata")
t2mtrain = t2ml[[1]]
t2mtest = t2ml[[2]]

cat("Load tcc...\n")
vbl = "tcc"
tccl = loadvar(vbl)
save(tccl, file = "/home/hugo/ECCRdata/tccl.Rdata")
tcctrain = tccl[[1]]
tcctest = tccl[[2]]
