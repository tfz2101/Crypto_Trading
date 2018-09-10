
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



#---nnet-----

nnet <- function(data,testdata){
  #test the nnnetwork against the nth most recent data points in testdata
  #testdata contains the date column and target column
  nn.tstdata =  testdata[,-(1:2)]
  nn.model <- neuralnet(combNames(data), data, hidden = 1,linear.output=TRUE, rep=1)
  nn.pred <- compute(nn.model, nn.tstdata)
  comp = cbind(testdata[,1:2],nn.pred$net.result)
  hit = data.frame(1:nrow(comp))
  for(i in 1:nrow(comp)){
    if(comp[i,2]==round(comp[i,ncol(comp)],0)){
      hit[i,1]=1
    }
    else{
      hit[i,1]=0
    }  
  }
  output =  cbind(comp,hit)
  output
}

ml3fcn <- function(data){
  div = round(nrow(data)*2/3,0)
  start = proc.time()
  nn = nnet(data[1:div,],data[-(1:div),])
  end = proc.time()
  time = end-start
  print(time[3])
  nn
}

temp <- function(){
  wine_km_7 = read.csv('wine_normal_DR.csv')
  wine_km_7 = wine_km_7[,-ncol(wine_km_7)]
  tst_km_7 = ml3fcn(wine_km_7)
  for(i in 1:1){tst_km_7 = ml3fcn(wine_km_7)}
  mean(tst_km_7[,4])
}

#-----test times of nnet by iterations-----
#This involves changing the nnet function by adding an extra parameter i to be passed into the instantiation of the neuralnet model. The parameter 'rep' is allowed to be i
timeNNET<-function(data,max_i){
  for(i in seq(1000,max_i,1000)){
    start = proc.time()
    nnet(data,data,i)
    end = proc.time()
    time = end-start
    print(time[3])
  }
}

#-----Classifiction Trees using RPART---------
treepart <- function(data,testdata,prune=1){
  #rp = rpart(combNames(data),data,method='class',control=rpart.control(maxdepth=3))
  rp = rpart(combNames(data),data,method='class')
  
  if(prune==1){
    rp = prune(rp, cp=rp$cptable[which.min(rp$cptable[,'xerror']),'CP'])
  }
  pred = predict(rp, testdata, type=c("class"))
  pred = matrix(pred,nrow=length(pred),ncol= 1)
  comp = cbind(testdata,pred)
  hit = data.frame(1:nrow(comp))
  for(i in 1:nrow(comp)){
    if(comp[i,2]==comp[i,ncol(comp)]){
      hit[i,1]=1
    }
    else{
      hit[i,1]=0
    }  
  }
  output = cbind(comp,hit)
  output
}

comp <-function(data,idx,pred){
  comp = cbind(data[,idx],pred)
  pred = matrix(pred,nrow=length(pred),ncol= 1)
  hit = matrix(NA,nrow(data),ncol=1)
  for(i in 1:nrow(data)){
    if(data[i,idx]==pred[i,1]){
      hit[i,1]=1
    }
    else{
      hit[i,1]=0
    }
    
  }
out = cbind(comp,hit)
out
  
}

kfold <- function(data,FUN,folds){
  cv.size = floor(nrow(data)/folds)
  hit = data.frame(Train_Accuracy=1:cv.size,Testing_Accuracy=1:cv.size,Timer=1:cv.size)
  
  for(i in 1:cv.size){
    testset = ((i-1)*folds+1):(i * folds)
    start = proc.time()
    comp_train = FUN(data[-(testset),],data[-(testset),])
    hit[i,1]=mean(comp_train[,ncol(comp_train)])
    
    comp_test = FUN(data[-(testset),],data[testset,])
    hit[i,2]=mean(comp_test[,ncol(comp_test)])
    end = proc.time()
    time = end - start
    hit[i,3]=time[3]
  }
  hit 
}

work <-function(train,test){
  N_FOLD = 100
  
  train_tst_crv = data.frame(k=1:2,Train_Accuracy=1:2,Test_Accuracy=1:2)

  print(nrow(train))
  print(nrow(test))
  
  
  #Creates the train/test accuracy as a function of sample size
  
  c = 50
  index = 1
  for(i in seq(200,nrow(train)*0+1000,c)){
    train_loop = train[1:i,]
    train_tmp = kfold(train_loop,nnet,N_FOLD)#CHANGE
    train_acc = mean(train_tmp[,2])
    #print(train_acc)

    tst_tmp = nnet(train_loop,test)#CHANGE
    tst_acc = mean(tst_tmp[,ncol(tst_tmp)])
    #print(tst_acc)
    train_tst_crv[index,1] = i
    train_tst_crv[index,2] = train_acc
    train_tst_crv[index,3] = tst_acc
    index = index+1
    c = round(c * 2,0)
  }
  print(train_tst_crv)
  
  
  #Test hyperparameters of neuralnet/decision tree based on K Fold Validation (using my kfold function)
  #test = kfold(train, treepart, N_FOLD)
  #print(mean(test[,2]))
  
}


