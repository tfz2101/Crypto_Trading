DecisionTreePlot <- function() {
  library(rpart)
  library(rpart.plot)
  ml_data <- read.csv("C:/Users/Frank Zhi/PycharmProjects/Crypto_Trading/R_Scripts/r_input.csv")
  model <- rpart(Y_5 ~ Pos_Change_Signal + acf_pval + df_pval, data = ml_data, control=rpart.control(minsplit=1,minbucket = 1))
  #Dates gets stored as variable X, so the dependent factors need to be named. 
  pred = predict(model, ml_data)
  rpart.plot(model)
}

DecisionTreePlot_RWEKA <- function() {
  library(RWeka)
  ml_data <- read.csv("C:/Users/Frank Zhi/PycharmProjects/Crypto_Trading/R_Scripts/r_input.csv")
  model <- rpart(Y_5 ~ Pos_Change_Signal + acf_pval + df_pval, data = ml_data, control=rpart.control(minsplit=1))
  #Dates gets stored as variable X, so the dependent factors need to be named. 
  pred = predict(model, ml_data)
  rpart.plot(model)
}

