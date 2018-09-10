#-----Packages------
#neuralnet, rpart, readr,adabag, caret


#-----General-------
above <- function(x) {
  use <- x > 10
  x[use]
  
}



colmean <- function(x, removeNA = TRUE){
  nc <- ncol(x)
  means <- numeric(nc)
  for (i in 1:nc){
    means[i] = mean(x[,i])
  }
  means
}
colstdev <- function(x, removeNA = TRUE){
  nc <- ncol(x)
  means <- numeric(nc)
  for (i in 1:nc){
    means[i] = sd(x[,i])
  }
  means
}


combNames <- function(data){
  data.names <- names(data)
  eq <- paste(data.names[2], "~")
  for (i in 3:length(data.names)){
    if(i!=length(data.names)){
      eq <- paste(eq,data.names[i], "+")
    }else{
      eq <- paste(eq,data.names[i])
    }
  }
  eq
}


#--------Stats--------------
pca <- function(data, removeNA = TRUE){
  
  nc <- ncol(data)
  nr <- nrow(data)
  avg<- numeric(nc)
  for(i in 1:nc){
    avg[i]=mean(data[,i])
  }
  centmat <- matrix(nrow=nrow(data), ncol = nc)
  
  for(j in 1:length(avg)){
    for(i in 1:nr){
      centmat[i,j] = data[i,j]-avg[j]
    }
  }
  
  covmat <- cov(centmat)
  eigen(covmat)
}

rsquared <- function(data, pre){
  avg = mean(data)
  sstot <- 0
  ssres <- 0
  
  for(i in 1:length(data)){
    sstot <- sstot + (data[i]-avg)^2
    ssres <- ssres + (data[i]-pre[i])^2
  }
  rsquared <- 1-sstot/ssres
  rsquared
}



meansd <- function(data, model){
  s <- sd(data)
  output <- array(length(data))
  for(i in 1:length(data)){
    output[i] <- abs(data[i] - model[i])
  }
  mean(output)
}

normdata <- function(data, oneortwo){
  norm <- data
  means = colmean(data)
  stds = colstdev(data)
  
  for(i in oneortwo:ncol(data)){
    for(j in 1:nrow(data)){
      norm[j,i] =(data[j,i] - means[i])/stds[i]
    }
  }
  #norm
  #stds
  means
}

denormdata <- function(data, means, stds, oneortwo){
  denorm <- data
  
  for(i in oneortwo:ncol(data)){
    for(j in 1:nrow(data)){
      denorm[j,i] =(data[j,i] * stds[i])+ means[i]
    }
  }
  denorm
}



#------ML-------------

regSpline <- function(data, MA1, error){
  #error is in units of sigma
  #assumes data has dates as the first column, y variable as the 2nd column
  form = combNames(data)
  fcns = list(0,0,0)
  
  start = pivot = end = 1
  i = 1
  #Activator Loop
  while(i < nrow(data)){
    if((start == end)&(start==pivot)&(pivot==end)){  #After classifying a regime, you start like in the beginning, and look for an viable LM
      if(i+6>=nrow(data)){break}
      startReg = lm(form, data[i:(i+6),])
      startResid = summary(startReg)$residuals
      i = i +6
      end = i
      i = i+1
    }
    if((start !=end)&(start==pivot)&(pivot!=end)){  #Looking for a pivot
      y = predict(startReg,data[i,])
      e = data[i,2]-y
      startResid = c(startResid,e)
      ma1 = mean(startResid[1:length(startResid)])
      ma2 = mean(startResid[(length(startResid)-MA1):length(startResid)])
      diffma = abs(ma2-ma1)
      startResidsd = sd(startResid)
      if(diffma > error*startResidsd){
        pivot = i
        end = i
        i=i+1
      }else{
        i = i +1
        end = i
      }
    }
    if((start !=end)&(start!=pivot)&(pivot==end)){  #Looking for the second pivot so we can generalize about the first pivot
      if(i+6>=nrow(data)){break}
      pivReg = lm(form, data[i:(i+6),])
      pivResid = summary(pivReg)$residuals
      i = i +7
      while((i<nrow(data))&(start !=end)&(start!=pivot)&(pivot==end)){
        y = predict(pivReg,data[i,])
        e = data[i,2]-y
        pivResid = c(pivResid,e)
        ma1 = mean(pivResid[1:length(pivResid)])
        ma2 = mean(pivResid[(length(pivResid)-MA1):length(pivResid)])
        diffma = abs(ma2-ma1)
        pivResidsd = sd(pivResid)
        if(diffma> error*pivResidsd){
          wholelm = lm(form,data[start:i,])
          startlm = lm(form,data[start:pivot,])
          pivlm = lm(form,data[(pivot+1):i,])
          wholeResid = wholelm$residuals
          partsResid = c(startlm$residuals,pivlm$residuals)
          if(sd(wholeResid)>=sd(partsResid)){
            temp1 = t(list(as.character(data[start,1]),as.character(data[pivot,1]),startlm))
            temp2 = t(list(as.character(data[pivot,1]),as.character(data[i,1]),pivlm))
            fcns =  rbind(fcns, temp1, temp2)
            start = end = pivot = i +1
            i = i+1
          }else{
            temp1 = t(list(as.character(data[start,1]), as.character(data[i,1]),wholelm))
            fcns = rbind(fcns,temp1)
            start = end = pivot = i +1
            i = i +1
          }
          
        }else{i = i +1}
      }
    }
    
  }
  temp1 = t(list(as.character(data[start,1]),as.character(data[nrow(data),1]),startReg))
  fcns = rbind(fcns,temp1)
  fcns = fcns[-(1),]
}

regSplineP <- function(fcns){
  width = length(summary(fcns[[1,3]])$coefficients[,4])
  result = matrix(0,1,width)
  for(i in 1:nrow(fcns)){
    temp = t(summary(fcns[[i,3]])$coefficients[,4])
    result = rbind(result,temp)
  }
  result = result[-(1),]
  result = cbind(fcns[,1:2],result)
}



#---nnet-----





iterateKfold <- function(data, FUN, min_CV, max_CV){
  size =  max_CV - min_CV+1
  output =  data.frame(Avg_Training_Score=1:size,Avg_Testing_Score=1:size,Train_STD=1:size,Testing_STD=1:size,Timer=1:size,CV=min_CV:max_CV)
  i =  1
  for(j in min_CV:max_CV){
    start = proc.time()
    out = kfold(data,FUN,j)
    #print(colmean(out))
    end=proc.time()
    run = end - start
    avgs = colmean(out)
    output[i,1]=avgs[1]
    output[i,2]=avgs[2]
    output[i,3]=sd(out[,1])
    output[i,4]=sd(out[,2])
    output[i,5]=run[3]
    i = i+1
  }
  output
}

cleanTSTdatannet <- function(tstdata){
  tstdata = tstdata[,-(1:2)]
}

#-----k cluster-------

clusterFit <- function(data, k, ordered, ordindex)
  #k cluster for a time series; returns ordered matrix grouped by clusters
{
  cleandata = data[,-(1)]
  cleandata <- as.matrix(cleandata)
  #k <- round(nrow(data)/10,0)
  
  if(ordered == 0){
    unordered = cleandata
    cleandata = cleandata[,-(ordindex)]
    mycluster <- kmeans(cleandata,k)
    
  }else{
    unordered = cleandata
    mycluster <- kmeans(cleandata,k)
  }
  
  
  ord <- mycluster$cluster
  
  ordMat <- matrix(0,nrow(cleandata),ncol(cleandata))
  counter = 1
  categ = matrix(0,nrow(cleandata),1)
  
  #This assumes the date is under variable X in the dataset
  dates = data.frame(data$X)
  
  for(j in 1:k){
    for(i in 1:nrow(cleandata)){
      if(ord[i]==j){
        ordMat[counter,] <- unordered[i,]
        dates[counter,1] = data[i,1]
        categ[counter]=j
        counter=counter+1
      }
    }
  }
  #dates[,1]
  data.frame(dates[,1],ordMat,categ)
  
}

clusterFitBT <- function(data, clusterFit){
  #assumes data has date as first column
  means = colmean(clusterFit[,-(1)])
  
  
}

#----regression Trees-------
regTree <- function(mydata){
  combo <- combNames(mydata)
  tree.model <- M5P(combo, data = mydata)
  tree.model
}

regTreeBT <- function(data, comp,lookfwd, oneortwo){
  #assumes in comp that the dates are ordered from most recent to less recent
  results = matrix(0,nrow(comp),3)
  results[,3] = -comp[,3]
  for(i in nrow(comp):(1+lookfwd)){
    results[i,2] = mean(data[(i-lookfwd):(i-1),oneortwo])-data[i,oneortwo]
    if((results[i,2]>=0&results[i,3]>=0)|(results[i,2]<0&results[i,3]<0)){
      results[i,1]=1
    }else{results[i,1]= 0}
    
  }
  
  results
}


regTreeStratBT <- function(data, tstdata, comp,lookfwd, oneortwo){
  #assumes in comp that the dates are ordered from most recent to less recent
  results = matrix(0,nrow(tstdata),3)
  results[,3] = -comp[,3]
  for(i in nrow(tstdata):1){
    for(j in nrow(data):1){
      if((tstdata[i,1]==data[j,1])&(j-lookfwd)>=0){
        results[i,2] = mean(data[(j-lookfwd):(j-1),oneortwo])-data[j,oneortwo]
        if((results[i,2]>=0&results[i,3]>=0)|(results[i,2]<0&results[i,3]<0)){
          results[i,1]=1
        }else{results[i,1]= 0}
      }
    }
  }
  results
}
regTreeComp <- function(tree.model,testdata){
  tree.predict <- predict(tree.model, testdata)
  output <- as.matrix(tree.predict)
  
  comp <- matrix(0,nrow(testdata),3)
  for(i in 1:nrow(testdata)){
    comp[i,1] <- testdata[i,2]
    comp[i,2] <- output[i,1]
    comp[i,3] <- comp[i,1] - comp[i,2]
  }
  
  comp
}

#Complete procedure that spits out the hit ratio for the lookfwd period using M5P regression tree
regTreeComplete <- function(data, tstdatamarker, oneortwo, lookfwd){
  form = combNames(data)
  learndata = data[tstdatamarker:nrow(data),]
  tstdata = data[1:tstdatamarker,]
  tree = M5P(form, learndata)
  comp = regTreeComp(tree, tstdata)
  bt = regTreeBT(tstdata, comp,lookfwd, oneortwo)
  result = cbind(comp, bt)
  #hitratio = sum(result[,4])/(nrow(result)-lookfwd)
}

regTreeCompletePeriod <- function(data, tstdatamarker, oneortwo, lookfwd, period){
  output = matrix(0,nrow=ceiling(nrow(data)/period),ncol=1)
  dates = data.frame(dates=1:nrow(output),index=1:nrow(output))
  for(i in 1:floor(nrow(data)/period)){
    if(i*period<nrow(data)){
      end = i*period
    }
    if(i*period>nrow(data)){
      end = nrow(data)
    }
    dates[i,1]=data[end,1]
    dates[i,2]=i*period
    temp = regTreeComplete(data[((i-1)*period+1):end,], tstdatamarker, oneortwo, lookfwd)
    output[i,1] = sum(temp[,4])/(nrow(temp)-lookfwd)
    
  }
  output
  output2 = data.frame(dates = dates,output=output)
}

#Performs a regTreeComplete on every data point and returns hit ratio. Uses trainper as the amount of data to train on.
regTreeCompleteBktest <- function(data, oneortwo, lookfwd, trainper){
  output = matrix(0,nrow=nrow(data),ncol=1)
  for(i in (nrow(data)-trainper):1+lookfwd){
    temp = regTreeComplete(data[(i-lookfwd):(i+trainper),],lookfwd+1, oneortwo, lookfwd)
    output[i,1]=temp[1+lookfwd,6]
  }
  output2 = data.frame(dates=data[,1],output=output)
  output2
  
}

regTreeCombinat <- function(data, tstdatamarker, oneortwo, lookfwd, choose){
  #does a combination of the number of dependant variables in data by the number in variable choose, outputs the hit ratio for all var combos
  learndata = data[tstdatamarker:nrow(data),]
  tstdata = data[1:tstdatamarker,]
  combos = regTreeComboNames(learndata, oneortwo+1, oneortwo, choose)
  wins = numeric(length(combos))
  
  for(i in 1:length(combos)){
    tree = M5P(combos[i], learndata)
    comp = regTreeComp(tree, tstdata)
    bt = regTreeBT(tstdata, comp,lookfwd, oneortwo)
    wins[i]=colmean(bt)[1]
  }
  result = as.data.frame(cbind(combos, wins))
  result
}

regTreeComboNames <- function(data, dependantstart, oneortwo, choose){
  #assumes first column is the dependant variable
  names = names(data)
  names = names[dependantstart:length(names)]
  
  combos = combn(names,choose)
  
  results = character(choose(length(names),choose))
  
  for(i in 1:ncol(combos)){
    fcn = paste(names(data)[oneortwo],"~")
    for(j in 1:nrow(combos)){
      if(j==nrow(combos)){
        fcn = paste(fcn,combos[j,i])
      }else{fcn = paste(fcn,combos[j,i],"+")}
    }
    results[i] = fcn
  }
  results
}

#-----Classifiction Trees using RPART---------






boostTree <-function(data){
  #Vehicle.adaboost <- boosting(Class ~.,data=Vehicle[sub, ],mfinal=mfinal, coeflearn="Zhu",
  #                             control=rpart.control(maxdepth=maxdepth))
}

#----------Trading Strategies------------------

#Rolling augmented dick fuller test
rollingADF <- function(data, period){
  #data has date in the first column
  ts = matrix(data[,2],nrow=nrow(data),ncol=ncol(data))
  output = matrix(0,nrow=ceiling(nrow(ts)/period),ncol=2)
  dates = data.frame(dates=1:nrow(output),index = 1:nrow(output))
  for(i in 1:floor(nrow(ts)/period)){
    if(i*period<nrow(ts)){
      tst = adf.test(ts[((i-1)*period+1):(i*period)],k=1)
      end = i*period
    }
    if(i*period>nrow(ts)){
      tst = adf.test(ts[((i-1)*period+1):nrow(ts)],k=1)
      end = nrow(ts)
    }
    dates[i,1]=data[end,1]
    dates[i,2]=i*period
    output[i,1] = tst$statistic
    output[i,2] = tst$p.value
    
  }
  output
  output2 = data.frame(dates = dates,output=output)
}

#Rolling ACF
rollingACF <- function(data, period, lag){
  #data has date in the first column
  ts = matrix(data[2:nrow(data),2]-data[1:(nrow(data)-1),2],nrow=nrow(data)-1,ncol=1)
  output = matrix(0,nrow=ceiling(nrow(ts)/period),ncol=1)
  dates = data.frame(dates=1:nrow(output))
  for(i in 1:floor(nrow(ts)/period)){
    if(i*period<nrow(ts)){
      tst = acf(ts[((i-1)*period+1):(i*period)])
      end = i*period
    }
    if(i*period>nrow(ts)){
      tst = acf(ts[((i-1)*period+1):nrow(ts)])
      end = nrow(ts)
    }
    dates[i,1]=data[end,1]
    output[i,1] = tst$acf[lag+1]
    
    
  }
  output
  output2 = data.frame(dates = dates,output=output)
}


timeADF <- function(data, per){
  #data has date in the first column
  ts = matrix(data[,2],nrow=nrow(data),ncol=2)
  output = ts
  for(i in (per+1):nrow(ts)){
    output[i,1] = adf.test(ts[(i-per):i])$statistic
    output[i,2] = adf.test(ts[(i-per):i])$p.value
  }
  output2 = data.frame(dates=data[,1],output=output)
}

RatesSim <- function(data, stopout){
  pos = matrix(0,nrow= nrow(data),ncol=1)
  pnl = matrix(0,nrow= nrow(data),ncol=1)
  hit = matrix(0,nrow= nrow(data),ncol=1)
  curpos  = 0
  rec = 0
  for(i in 2:nrow(data)){
    
    if(is.na(data[i,12])==FALSE){
      
      if(data[i,11]>=0&curpos<=0){
        curpos = curpos +1
      }
      if(data[i,11]<=0&curpos>=0){
        curpos = curpos -1
      }
      
    }
    pos[i,1]= curpos
    pnl[i,1] = pos[i-1,1]*(data[i,2]-data[i-1,2])
    
    if(rec==1&(pos[i-1,1]==pos[i,1])){
      temppnl = sum(pnl[ind:i,1])
      if(temppnl < stopout*-data[i,2]){
        pos[i,1]=0
        curpos = 0
      }
    }
    if(pos[i-1,1]==0&pos[i,1]!=0){
      ind=i+1
      rec=1
    }
    if(pos[i-1,1]!=0&pos[i,1]==0){
      rec=0
    }
    
    
  }
  
  
  #computes hit ratio
  for(i in 2:nrow(pos)){
    if(pos[i-1,1]!=0&pnl[i,1]>0){hit[i,1]=2}
    if(pos[i-1,1]!=0&pnl[i,1]<0){hit[i,1]=1}
  }
  
  hitratio = (sum(hit[,1])-nnzero(hit[,1]))/sum(hit[,1])
  #output = data.frame(date=data[,1],pnl=pnl)
  hitratio
}

#---momentum strategies-------
#---ARIMA stuff
rollingARIMA <- function(data, p, q, sample){
  output = data
  output[,2]=0
  se = data.frame(0,nrow=nrow(output))
  for(i in (sample+1):nrow(data)){
    curr = arima(data[(i-sample):(i-1),2],order=c(p,0,q),method="ML")
    pred = predict(curr,n.ahead=1)
    se[i,1]=sqrt(curr$sigma2)
    output[i,2]=pred
  }
  output = cbind(output,se)
}


#---TP Regression Model
bktestLMVolmaLoop <- function(data, thres, start, tradeItem, volma1, volma1divisor){
  #volma1divisor is the number to divide volma1 by to get the loop's volma12
  output = matrix(1,nrow=volma1,ncol=volma2)
  for(i in 2:volma1){
    for(j in 2:round(volma1/volma1divisor,0)){
      
    }
  }
}

bktestLM <- function(data,thres,start,tradeItem, volma1, volma2){
  diffs = bktestLMReg(data,2)
  pos = matrix(1,nrow=nrow(data),ncol=1)
  entry = bktestLMEntryCrossOver(data,thres,diffs,start)
  #pos = bktestLMPos(diffs[,1:2],volma1, volma2)
  pnl = bktestLMPNLCrossOver(data, entry, pos, start, tradeItem)
  output = data.frame(stats=diffs,pos=pos,entry=entry,pnl=pnl)
  output
}
#Entry doesn't include crossovers, i.e. when the data crosses from positive to negative, or vice versa
bktestLMEntry <- function(data, thres, diffs,start){
  entry=matrix(0,nrow=nrow(data),ncol=1)
  for(i in start:nrow(data)){
    #Should we Short?
    if(diffs[i,4]>=thres){
      entry[i,1]=-1
    }
    #Should we Long?
    if(diffs[i,4]<=-thres){
      entry[i,1]=1
    }
  }
  entry
}

#Entry distinguishes crossovers, -2 = buy, -1 = cross from neg to pos, 2 = short, 1 = cross from pos to neg
bktestLMEntryCrossOver <- function(data, thres, diffs,start){
  entry=matrix(0,nrow=nrow(data),ncol=1)
  for(i in start:nrow(data)){
    
    #Should we net out Short?
    if((diffs[i-1,4]>0)&(diffs[i-1,4]*diffs[i,4])<0){
      entry[i,1]=1
    }
    #Should we net out Long?
    if((diffs[i-1,4]<0)&(diffs[i-1,4]*diffs[i,4])<0){
      entry[i,1]=-1
    }
    #Should we Short?
    if(diffs[i,4]>=thres){
      entry[i,1]=-2
    }
    #Should we Long?
    if(diffs[i,4]<=-thres){
      entry[i,1]=2
    }
  }
  entry
}


bktestLMPNL <- function(data, entry, pos, start, tradeItem){
  #tradeItem is the data that's actually used for PnL. data might only provide the triggers. TradeItem has dates a the first column, data as the second column
  pnl = matrix(0,nrow=nrow(data),ncol=1)
  path = matrix(0,nrow=nrow(data),ncol=1)
  inandouts = matrix(0,nrow=nrow(data),ncol=1)
  lastDir = 0
  lastIdx = 1
  for(i in start:nrow(data)){
    if((entry[i,1] != 0)&(lastDir==0)){
      lastDir=entry[i,1]
      lastIdx=i
    }
    if((entry[i,1] != 0)&(entry[i,1]*lastDir<0)){
      if(lastDir>0){
        pnl[i,1]= (tradeItem[i,2]-tradeItem[lastIdx,2])*pos[lastIdx,1]
      }
      if(lastDir<0){
        pnl[i,1]= (tradeItem[lastIdx,2]-tradeItem[i,2])*pos[lastIdx,1]
      }
      for(j in lastIdx:i){
        path[j,1]=tradeItem[j,2]
      }
      inandouts[i,1]=1
      lastDir = 0
    }
  }
  output = data.frame(in_and_outs=inandouts,pnl=pnl,path=path)
  output
}

bktestLMPos <- function(data, volma1, volma2){
  pos = matrix(1,nrow=nrow(data),ncol=1)
  volmas1 = matrix(0,nrow=nrow(data),ncol=1)
  volmas2= matrix(0,nrow=nrow(data),ncol=1)
  for(i in (volma1+2):nrow(volmas1)){
    volmas1[i,1]=sd(data[(i-volma1):i,2])
    volmas2[i,1]=sd(data[(i-volma2):i,2])
    #how much to invest depends on ratio of MA of volatility
    pos[i,1]=volmas1[i,1]/volmas2[i,1]
  }
  
  pos
}
#Counterpart to bktestEntryCrossOver
bktestLMPNLCrossOver <- function(data, entry, pos, start,tradeItem){
  pnl = matrix(0,nrow=nrow(data),ncol=1)
  path = matrix(0,nrow=nrow(data),ncol=1)
  inandouts = matrix(0,nrow=nrow(data),ncol=1)
  lastDir = 0
  lastIdx = 1
  for(i in start:nrow(data)){
    if((abs(entry[i,1])>1)&(lastDir==0)){
      lastDir=entry[i,1]
      lastIdx=i
    }
    if((entry[i,1] != 0)&(entry[i,1]*lastDir<0)){
      if(lastDir>0){
        pnl[i,1]= (tradeItem[i,2]-tradeItem[lastIdx,2])*pos[lastIdx,1]
        for(j in lastIdx:i){
          path[j,1]=tradeItem[j,2]
        }
        inandouts[i,1]=1
        if(entry[i,1]*lastDir==-4){
          lastDir = -2
          lastIdx = i
          
          next
        }
        else{lastDir = 0}
      }
      if(lastDir<0){
        pnl[i,1]= (tradeItem[lastIdx,2]-tradeItem[i,2])*pos[lastIdx,1]
        for(j in lastIdx:i){
          path[j,1]=tradeItem[j,2]
        }
        inandouts[i,1]=1
        if(entry[i,1]*lastDir==-4){
          lastDir = 2
          lastIdx = i
        }
        else{lastDir = 0}
      }
    }
  }
  output = data.frame(in_and_outs=inandouts,pnl=pnl,path=path)
  output
}


bktestLMReg <- function(data,start){
  form = combNames(data)
  resid = data.frame(date="00/00/00",residual=1:nrow(data), stringsAsFactors = FALSE)
  sds = matrix(0,nrow=nrow(data),ncol=1)
  lvl = matrix(0,nrow=nrow(data),ncol=1)
  for(i in start:nrow(data)){
    currlm = lm(combNames(data), data[1:(i-1),])
    pred = predict(currlm,data[i,])
    resid[i,1]=as.character(data[i,1])
    resid[i,2]=data[i,2]-pred
    sds[i,1] = sd(resid[start:(i-1),2])
    lvl[i,1] = resid[i,2]/sds[i,1]
    #currsd = sd()
  }
  output = data.frame(resid=resid,sds=sds,level=lvl)
}



#----MA backtesting functions

#main backtest function - wrapper function for all parameter functions for backtesting
bktest <- function(data, lkbk, volma1, volma2){
  #data input consists of date and time series columns
  
  #pos = matrix(bktestPos(data,lkbk, volma1, volma2)[,1])
  pos=matrix(1,nrow(data),ncol=3)
  volmas1 = matrix(bktestPos(data,lkbk, volma1, volma2)[,2])
  volmas2 = matrix(bktestPos(data,lkbk, volma1, volma2)[,3])
  
  hit = matrix(bktestEntry(data,lkbk,volma1,pos)[,3])
  pnl = matrix(bktestEntry(data,lkbk,volma1,pos)[,4])
  
  hitratio = (sum(hit)-nnzero(hit))/nnzero(hit)
  totalpnl = sum(pnl)
  avgpnl = totalpnl/nnzero(hit)
  output = data.frame(date=as.character(data[,1]),position=pos,hit=hit, pnl=pnl)
  avgpnl
}

bktestPos <-function(data,lkbk,volma1,volma2){
  pos = matrix(0,nrow=nrow(data),ncol=1)
  volmas1 = matrix(0,nrow=nrow(data),ncol=1)
  volmas2= matrix(0,nrow=nrow(data),ncol=1)
  for(i in (volma1+1):nrow(data)){
    volmas1[i,1]=sd(data[(i-volma1):i,2])
    volmas2[i,1]=sd(data[(i-volma2):i,2])
    #how much to invest depends on ratio of MA of volatility
    pos[i,1]=volmas1[i,1]/volmas2[i,1]
  }
  
  output = data.frame(position=pos,ma1=volmas1,ma2=volmas2)
}

bktestEntry <-function(data,lkbk, volma1, pos){
  resid = matrix(0,nrow=nrow(data),ncol=1)
  ma = matrix(0,nrow=nrow(data),ncol=1)
  pnl = matrix(0,nrow=nrow(data),ncol=1)
  hit = matrix(0,nrow=nrow(data),ncol=1)
  for(i in (max(lkbk,volma1)+1):(nrow(data)-1)){
    ma[i,1]=mean(data[(i-lkbk):(i-1),2])
    resid[i,1] = data[i,2]-ma[i,1]
    if(resid[i-1,1]==0){
      next
    }
    if(resid[i,1]*resid[i-1,1]>=0){
      next
    }
    #looking for when the data crosses over the MA. Then look forward one period to see the return of a 1 month holding period
    if((resid[i,1]*resid[i-1,1]<0)&(resid[i,1]>=0)){
      pnl[i,1]=(data[i+1,2]-data[i,2])*pos[i,1]
      if(pnl[i,1]>=0){hit[i,1]=2}
      if(pnl[i,1]<0){hit[i,1]=1}
      #marks the data of when you hold a position, so you can calcualte std for the sharp ratio
      #unit = matrix(data[i+1,2])
      #rbind(path,)
      
    }
    
    if((resid[i,1]*resid[i-1,1]<0)&(resid[i,1]<0)){
      pnl[i,1]=(data[i,2]-data[i+1,2])*pos[i,1]
      if(pnl[i,1]>=0){hit[i,1]=2}
      if(pnl[i,1]<0){hit[i,1]=1}
    }
    
  }
  output=data.frame(ma=ma,resid=resid,hit=hit,pnl=pnl)
}



bktestvaryMA <- function(data, lkbk, volma1, volma2, adjper){
  topsd = sd(data[,2])
  #data inpu consists of date and time series columns
  ma = matrix(0,nrow=nrow(data),ncol=1)
  resid = matrix(0,nrow=nrow(data),ncol=1)
  pos = matrix(0,nrow=nrow(data),ncol=1)
  volmas1 = matrix(0,nrow=nrow(data),ncol=1)
  volmas2= matrix(0,nrow=nrow(data),ncol=1)
  pnl = matrix(0,nrow=nrow(data),ncol=1)
  hit = matrix(0,nrow=nrow(data),ncol=1)
  pnlcomp = matrix(0,nrow=lkbk,ncol=1)
  
  #path = matrix(0,nrow=1,ncol=1)
  #path[1,1]="A"
  
  for(i in adjper:(nrow(ma)-1)){
    persd = sd(data[(i-adjper+1):i,2])
    volmas1[i,1]=sd(data[(i-volma1):(i-1),2])
    volmas2[i,1]=sd(data[(i-volma2):(i-1),2])
    #how much to invest depends on ratio of MA of volatility
    lkbkadj = volmas1[i,1]/persd
    newlkbk = lkbkadj * lkbk
    pos[i,1]=volmas1[i,1]/volmas2[i,1]
    ma[i,1]=mean(data[(i-newlkbk):(i-1),2])
    resid[i,1] = data[i,2]-ma[i,1]
    if(resid[i-1,1]==0){
      next
    }
    if(resid[i,1]*resid[i-1,1]>=0){
      next
    }
    #looking for when the data crosses over the MA. Then look forward one period to see the return of a 1 month holding period
    if((resid[i,1]*resid[i-1,1]<0)&(resid[i,1]>=0)){
      pnl[i,1]=(data[i+1,2]-data[i,2])*pos[i,1]
      if(pnl[i,1]>=0){hit[i,1]=2}
      if(pnl[i,1]<0){hit[i,1]=1}
      #marks the data of when you hold a position, so you can calcualte std for the sharp ratio
      #unit = matrix(data[i+1,2])
      #rbind(path,)
      
    }
    
    if((resid[i,1]*resid[i-1,1]<0)&(resid[i,1]<0)){
      pnl[i,1]=(data[i,2]-data[i+1,2])*pos[i,1]
      if(pnl[i,1]>=0){hit[i,1]=1}
      if(pnl[i,1]<0){hit[i,1]=1}
    }
    
  }
  
  hitratio = (sum(hit)-nnzero(hit))/nnzero(hit)
  totalpnl = sum(pnl)
  avgpnl = totalpnl/nnzero(hit)
  hitratio
  
}

#Loops thru MA1 for bktest
bktestloopma1 <- function(data, lkbk){
  pnls = matrix(0, nrow=lkbk, ncol = 1)
  for(i in 8:lkbk){
    pnls[i,1]=bktest(data,i,i,floor(i/4))
    
  }
  pnls
}

bktestloopVaryma1 <- function(data, lkbk, adjper){
  pnls = matrix(0, nrow=lkbk, ncol = 1)
  for(i in 8:lkbk){
    pnls[i,1]=bktestvaryMA(data,i,i,floor(i/4),adjper)
  }
  pnls
}

#Loops thru MA2 for bktest
bktestloopma2 <- function(data, lkbk){
  pnls = matrix(0, nrow=lkbk, ncol = 1)
  for(i in 2:round(lkbk/2,digits=0)){
    pnls[i,1]=bktest(data,lkbk,lkbk,i)
  }
  pnls
}

#Returns the output of the best MA for rolling blocks of data
bktestLoopMAPeriod <- function(data, lkbk, period){
  ts = matrix(data[,2],nrow(data),ncol=1)
  output = matrix(0,nrow=ceiling(nrow(ts)/period),ncol=2)
  dates = data.frame(dates=1:nrow(output))
  for(i in 1:nrow(output)){
    if(i*period<nrow(ts)){
      mat = bktestloopma1(data,lkbk)
      temp = matrix(1:nrow(mat),nrow=nrow(mat),ncol=1)
      mat = cbind(temp,mat)
      sortmat = mat[order(mat[,2],decreasing=TRUE),]
      output[i,1]=sortmat[1,1]
      output[i,2]=sortmat[1,2]
      end = i*period
    }
    if(i*period>=nrow(ts)){
      
      end = nrow(ts)
    }
    dates[i,1]=data[end,1]
    
    
  }
  output
  output2 = data.frame(dates = dates,output=output)
  
  
}

#----------New Functions After This Line----------------------


svm <-function(data){
  forma = names(data)[2]
  svmmodel = ksvm(paste(forma,"~."),data, kernel = "vanilladot")
  #svmmodel
  forma
}

ksmoother <- function(data, bw){
  
  smoothed = data
  smoothed[,2] = 0
  for(i in 2:nrow(data)){
    temp = ksmooth(1:i,data[1:i,2],kernel =  c("normal"), bandwidth = bw)
    smoothed[i,2] = temp$y[i]
  }
  
  smoothed
}

ARMAfit <- function(data){
  #data has been an array, I think. No dates column
  final.aic = Inf
  for(p in 0:5){
    for(q in 0:5){
      if(q==0 && p==0){
        next
      }
      
      arimaFit = tryCatch(arima(data, order=c(p,0,q)),error=function( err ) FALSE, warning=function( err ) FALSE)
      
      if(!is.logical(arimaFit)){
        curr.aic = AIC(arimaFit)
        if(curr.aic < final.aic){
          final.aic = curr.aic
          final.order = c(p,0,q)
          final.arima = arima(data, order = final.order)
        }
      }
      else{next}
    }
  }
  output = list(final.arima, final.order)
  output
}

GARCHfit <- function(data,arima.order){
  spec = ugarchspec(variance.model=list(garchOrder=c(1,1)),mean.model=list(armaOrder=c(arima.order[1],arima.order[3]),include.mean=T),distribution.model="sged")
  fit = tryCatch(ugarchfit(spec,data,solver="hybrid"),error=function(e) e, warning=function(w) w)
  fit
  
}

GARCHpred <- function(data,lkbk){
  #data has a 1st column as dates
  #GARCHfit requires at least 100 data points
  pred  =  data
  adf = matrix(0,nrow=nrow(data),ncol=1)
  pred[,2] = 0
  for(i in (lkbk+1):(nrow(data)-1)){
    temp = array(data[(i-lkbk):i,2])
    armaft = ARMAfit(temp)
    garchft = GARCHfit(temp,armaft[[2]])
    fit = tryCatch({ugarchforecast(garchft,n.ahead=1)},error=function(e) {TRUE}, warning=function(w) TRUE)
    if(is.logical(fit)){
      next
    }
    else {pred[i+1,2] = fit@forecast$seriesFor[1]}
    adf[i,1]=adf.test(temp)$p.value
  }
  output = cbind(pred,adf)
  output
}

rollingGARCH <- function(data, lkbk, span, index){
  slice = data[((index-1)*(lkbk+span)+1):((lkbk+span)*index),]
  gfit = GARCHpred(slice,lkbk)
  comp = cbind(slice,gfit[,2])
  write.csv(comp,paste("arimaDaily",index,".csv"))
}
