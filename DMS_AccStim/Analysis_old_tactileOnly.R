#Fa_Rate = 1/(2*N) if (nFa+nCr)==0 else nFa/(nFa+nCr)
 #   P_correct = np.divide((nHit + nCr),(nHit + nCr + nMiss + nFa))
  #  P_error = np.divide((nFa + nMiss),(nHit + nCr + nMiss + nFa))
   # P_correct_corrected = P_correct - P_error # https://www.researchgate.net/profile/Stephen-Link-2/publication/232548798_Correcting_response_measures_for_guessing_and_partial_information/links/0a85e53bc1e2d5f277000000/Correcting-response-measures-for-guessing-and-partial-information.pdf


# path_to_data <- "~/Dokumente/GitHub/STIWA/DMS_AccStim/Data_DMS_tactileOnly/" # Raspberry pi 
path_to_data <- "~/Documents/GitHub/STIWA/DMS_AccStim/Data_DMS_tactileOnly/"
setwd(path_to_data)
allFileNames <- list.files(path=path_to_data)
dmsData_ids <- as.vector(sapply(allFileNames,function(i){grepl("main",i)}))
dmsData_fileNames <- allFileNames[dmsData_ids]
# merging data
code_x_data <- NULL
data_merged <- NULL

for (x in c(1:length(dmsData_fileNames))) {
  x_name <- dmsData_fileNames[x]
  code_x_data <- read.csv(file = x_name, header = TRUE, sep = ";")
  if(x==1){data_merged <- code_x_data}else{
    data_merged <- rbind(data_merged,code_x_data)
  }
}
test_data <- data_merged[data_merged$practice=="False",]
unique_codes <- unique(test_data$p_code)
N_sample <- length(unique_codes)

test_data$queriedPosition <- NA
test_data$response_sdt <- NA
for (i in 1:nrow(test_data)) {
  i_question <- test_data[i,"question"]
  i_question_split <- c(unlist(strsplit(i_question,"")))
  queriedPosition_i <- i_question_split[length(i_question_split)-1]
  test_data[i,"queriedPosition"] <- queriedPosition_i
  i_targetPosition <- test_data[i,"seqPos"]
  i_response <- test_data[i,"yes_no"]
  yes_key <- test_data[i,"yes_key"]
  i_yes <- NA
  if(i_response==yes_key){
    i_yes <- TRUE
  }else{
    i_yes <- FALSE
  }
  i_question <- test_data[i,"question"]
  i_question_split <- unlist(strsplit(i_question,""))
  equalQuestion <- i_question_split[3]
  if(equalQuestion=="="){
    equalQuestion <- TRUE
  }else{
    equalQuestion <- FALSE
  }
  if(equalQuestion==TRUE){
    if(queriedPosition_i==i_targetPosition){
      if(i_yes==TRUE){
        i_sdtResp = "Hit"  
      }else{
        i_sdtResp = "Miss"
      }
    }else{
      if(i_yes==FALSE){
        i_sdtResp = "Cr"  
      }else{
        i_sdtResp = "Fa"
      }
    }
  }else{
    if(queriedPosition_i!=i_targetPosition){
      if(i_yes==TRUE){
        i_sdtResp = "Hit"  
      }else{
        i_sdtResp = "Miss"
      }
    }else{
      if(i_yes==FALSE){
        i_sdtResp = "Cr"  
      }else{
        i_sdtResp = "Fa"
      }
    }
  }
  test_data[i,"response_sdt"] <- i_sdtResp
}

# compute and insert variable: queriedItem
# .....

# p correct
aggrFx2 <- function(pts,tns,question,targetPos,queriedPos){
  # pts <- "Same"; tns <- "low"; question <- "P = T1?"; targetPos=2; queriedPos=1;
  df_pCorrect <- NULL
  for(code_i in c(1:N_sample)){
    print(code_i)
    curCode <- unique_codes[code_i]
    print(curCode)
    curCodeData <- test_data[test_data$p_code==curCode,]
    pts_x_trials <- curCodeData$Same_or_Diff==pts
    tns_x_trials <- curCodeData$ITS==tns
    question_x_trials <- curCodeData$question==question
    targetPos_x_trials <- curCodeData$seqPos==targetPos
    queriedPos_x_trials <- curCodeData$queriedPosition==queriedPos
    curCode_condiData <- curCodeData[(pts_x_trials&tns_x_trials&question_x_trials&
                                        targetPos_x_trials&queriedPos_x_trials),]

    tbl_fqs <- table(curCode_condiData$response_sdt)
    if(is.element("Hit",names(tbl_fqs))){
      if(tbl_fqs["Hit"]==sum(tbl_fqs)){
        p_correct <- prop.table(tbl_fqs)["Hit"]
      }else{p_correct <- prop.table(tbl_fqs)["Hit"]-prop.table(tbl_fqs)["Miss"]}
    }else{
      if(tbl_fqs["Cr"]==sum(tbl_fqs)){
        p_correct <- prop.table(tbl_fqs)["Cr"]
      }else{
        p_correct <- prop.table(tbl_fqs)["Cr"]-prop.table(tbl_fqs)["Fa"] 
      }
    }
    df_pCorrect_code_i <- data.frame(code=curCode,
                                     pts,tns,question,
                                     targetPos,queriedPos,
                                     p_c_corrected=p_correct)
    
   df_pCorrect <- rbind(df_pCorrect,df_pCorrect_code_i) 
  }
  return(df_pCorrect)
}

sameLow_11 <- aggrFx2(pts="Same",tns="low",question="P = T1?",targetPos=1,queriedPos=1)
sameLow_21 <- aggrFx2(pts="Same",tns="low",question="P = T1?",targetPos=2,queriedPos=1)
df2 <- rbind(sameLow_11,sameLow_21)
df <- df2
sameLow_12 <- aggrFx2(pts="Same",tns="low",question="P = T2?",targetPos=1,queriedPos=2)
sameLow_22 <- aggrFx2(pts="Same",tns="low",question="P = T2?",targetPos=2,queriedPos=2)
df2 <- rbind(sameLow_12,sameLow_22)
df <- rbind(df,df2)
print(aggregate(p_c_corrected~targetPos*queriedPos,data=df,FUN=function(i){
  return(c(mean(i),sd(i)))}))

sameHigh_11 <- aggrFx2(pts="Same",tns="high",question="P = T1?",targetPos=1,queriedPos=1)
sameHigh_21 <- aggrFx2(pts="Same",tns="high",question="P = T1?",targetPos=2,queriedPos=1)
df2 <- rbind(sameHigh_11,sameHigh_21)
df <- rbind(df,df2)
sameHigh_12 <- aggrFx2(pts="Same",tns="high",question="P = T2?",targetPos=1,queriedPos=2)
sameHigh_22 <- aggrFx2(pts="Same",tns="high",question="P = T2?",targetPos=2,queriedPos=2)
df2 <- rbind(sameHigh_12,sameHigh_22)
df <- rbind(df,df2)
df$code <- as.factor(df$code)
df$pts <- as.factor(df$pts)
df$tns <- as.factor(df$tns)
df$question <- as.factor(df$question)
df$queriedPos <- as.factor(df$queriedPos)

aggregate(p_c_corrected~targetPos*queriedPos*tns,data=df,
          FUN=function(i){return(c(mean(i),sd(i)))})
aggregate(p_c_corrected~targetPos*queriedPos,data=df2,
          FUN=function(i){return(c(mean(i),sd(i)))})

aov_res <- aov(p_c_corrected~targetPos*queriedPos*tns + 
                 Error(code/(targetPos*tns)),
               data=df)
summary(aov_res)
aggr_2wayInteraction <- aggregate(p_c_corrected~targetPos*queriedPos, 
          data=df2,FUN=function(i){c(mean(i),sd(i))})
aggr_3wayInteraction <- aggregate(p_c_corrected~targetPos*queriedPos*tns, 
          data=df2,FUN=function(i){c(mean(i),sd(i))})
