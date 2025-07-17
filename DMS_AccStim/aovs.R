#Fa_Rate = 1/(2*N) if (nFa+nCr)==0 else nFa/(nFa+nCr)
 #   P_correct = np.divide((nHit + nCr),(nHit + nCr + nMiss + nFa))
  #  P_error = np.divide((nFa + nMiss),(nHit + nCr + nMiss + nFa))
   # P_correct_corrected = P_correct - P_error # https://www.researchgate.net/profile/Stephen-Link-2/publication/232548798_Correcting_response_measures_for_guessing_and_partial_information/links/0a85e53bc1e2d5f277000000/Correcting-response-measures-for-guessing-and-partial-information.pdf


# path_to_data <- "~/Dokumente/GitHub/STIWA/DMS_AccStim/Data/"
path_to_data <- "~/Documents/GitHub/STIWA/DMS_AccStim/Data/"
setwd(path_to_data)
allFileNames <- list.files(path=path_to_data)
dmsData_ids <- as.vector(sapply(allFileNames,function(i){grepl("dms",i)}))
dmsData_fileNames <- allFileNames[dmsData_ids]
# merging data
for (x in dmsData_fileNames) {
  code_x_data <- read.csv(file = x, header = TRUE)
  if(x==dmsData_fileNames[1]){data_merged <- code_x_data}else{
    data_merged <- rbind(data_merged,code_x_data)
  }
}
test_data <- data_merged[data_merged$practice=="False",]
unique_codes <- unique(test_data$pcode)
N_sample <- length(unique_codes)

test_data$queriedPosition <- NA
for (i in 1:nrow(test_data)) {
  i_question <- test_data[i,"question"]
  i_question_split <- c(unlist(strsplit(i_question,"")))
  queriedPosition_i <- i_question_split[length(i_question_split)-1]
  test_data[i,"queriedPosition"] <- queriedPosition_i
}

print(paste("Sample size: ",N_sample))

# compute and insert variable: queriedItem
# .....

aggrFx <- function(pts,tns,accPos){
  
  df_rocPoints_individual <- NULL
  qTypeNames <- c("P = T1?","P = T2?")
  df_dPrime <- NULL
  df_pCorrect <- NULL
  for(code_i in c(1:N_sample)){
    curCode <- unique_codes[code_i]
    curCodeData <- test_data[test_data$pcode==curCode,]

    pts_x_trials <- curCodeData$PTS==pts
    tns_x_trials <- curCodeData$TNS==tns
    accessoryPosition_x_trials <- curCodeData$AccessoryPosition==accPos

    curCode_condiData <- curCodeData[pts_x_trials&tns_x_trials&accessoryPosition_x_trials,]
    curCode_condiData_eqQ1 <- curCode_condiData[curCode_condiData$question=="P = T1?",]
    curCode_condiData_eqQ2 <- curCode_condiData[curCode_condiData$question=="P = T2?",]
    list_qType_specific_data <- list(PisT1=curCode_condiData_eqQ1,PisT2=curCode_condiData_eqQ2)

    curCode_condiData_eqQ1$
    
    df_code_i <- NULL
    df_pCorrect_code_i <- NULL
    for (x in 1:2) {
      curData <- list_qType_specific_data[[x]]
      respYes_trials <- curData$response_dicho=="Yes"
      T1_trials <- curData$TargetPosition==1
      if(x==1) {
        data_hitRate <- curData[T1_trials&respYes_trials,]
        data_faRate <- curData[(T1_trials==FALSE)&respYes_trials,]
        data_missRate <- curData[T1_trials&(respYes_trials==FALSE),]
        data_crRate <- curData[(T1_trials==FALSE)&(respYes_trials==FALSE),]
      } else {
        data_hitRate <- curData[(T1_trials==FALSE)&respYes_trials,]
        data_faRate <- curData[T1_trials&respYes_trials,]
        data_missRate <- curData[(T1_trials==FALSE)&(respYes_trials==FALSE),]
        data_crRate <- curData[T1_trials&(respYes_trials==FALSE),]
      }
      fx <- function(data_x){
        fqs_xRate_perConfidence <- table(data_x$response_rating)
        fq_ids <- match(c("sure","quiteSure","unsure"),names(fqs_xRate_perConfidence))
        fqs_xRate_perConfidence <- as.vector(fqs_xRate_perConfidence[fq_ids])
        if(any(is.na(fqs_xRate_perConfidence))){
          ids_NAs <- which(is.na(fqs_xRate_perConfidence)==TRUE)
          fqs_xRate_perConfidence[ids_NAs] <- 0
        }
        return(fqs_xRate_perConfidence)
      }
      fqs_hitRate_perConfidence <- fx(data_x=data_hitRate)
      fqs_hitRate_sum <- sum(fqs_hitRate_perConfidence)
      
      fqs_faRate_perConfidence <- fx(data_x=data_faRate)
      fqs_faRate_sum <- sum(fqs_faRate_perConfidence)
      
      fqs_missRate_perConfidence <- fx(data_x=data_missRate)
      fqs_missRate_sum <- sum(fqs_missRate_perConfidence)
      
      fqs_crRate_perConfidence <- fx(data_x=data_crRate)
      fqs_crRate_sum <- sum(fqs_crRate_perConfidence)
      
      fqs_correct <- sum(c(fqs_hitRate_sum,fqs_crRate_sum))
      fqs_error <- sum(c(fqs_faRate_sum,fqs_missRate_sum))
      p_correct <- fqs_correct/(fqs_correct+fqs_error)
      p_error <- fqs_errors/(fqs_correct+fqs_error)
      p_correct_corrected <- p_correct-p_error
      
      sumOfsums <- sum(c(fqs_hitRate_sum,fqs_faRate_sum,fqs_missRate_sum,fqs_crRate_sum))
      hitRate <- fqs_hitRate_sum/sum(c(fqs_hitRate_sum,fqs_missRate_sum))
      if(hitRate==1){
        hitRate <- 1 - 1/(2*N_sample) # https://stats.stackexchange.com/questions/134779/d-prime-with-100-hit-rate-probability-and-0-false-alarm-probability
      }
      faRate <- fqs_faRate_sum/sum(c(fqs_faRate_sum,fqs_crRate_sum))
      if(faRate==0){
        faRate <- 1/(2*N_sample)
      }
      dPrime <- qnorm(hitRate)-qnorm(faRate)
      
      # percent correct corrected
      df_pCorrect_code_i <- rbind(df_pCorrect_code_i,
                                  data.frame(code=curCode,qName=qTypeNames[x],
                                             tns=tns,pts=pts,targetPosition=))

      df_code_i <- rbind(df_code_i,
        data.frame(code=curCode,qName=qTypeNames[x],
          tns=tns,pts=pts,queriedPosition=x,accessoryPosition=accPos,
          qType="eq",
          hit_fq=fqs_hitRate_sum,fa_fq=fqs_faRate_sum,
          miss_fq=fqs_missRate_sum,cr_fq=fqs_crRate_sum,
          sumOfsums=sumOfsums,hitRate=hitRate,faRate=faRate,dPrime=dPrime)
        )

    }
    df_dPrime <- rbind(df_dPrime,df_code_i)
  }
  return(df_dPrime)
}
same_low_1_1 <- aggrFx(pts="Same",tns="low",accPos=1)
same_low_1_2 <- aggrFx(pts="Same",tns="low",accPos=2)
same_high_1_1 <- aggrFx(pts="Same",tns="high",accPos=1)
same_high_1_2 <- aggrFx(pts="Same",tns="high",accPos=2)

df_same <- rbind(same_low_1_1,same_low_1_2)
df_same <- rbind(df_same,same_high_1_1)
df_same <- rbind(df_same,same_high_1_2)

df_aggr <- aggregate(dPrime~queriedPosition*accessoryPosition*tns,data=df_same,
          FUN=function(i){c(mean(i),sd(i))})

# p correct
aggrFx2 <- function(pts,tns,question,accPos,targetPos,queriedPos){
  #pts <- "Same";tns <- "low"; question <- "P = T1?"; targetPos=2;accPos=1;queriedPos=1;
  df_pCorrect <- NULL
  for(code_i in c(1:N_sample)){
    curCode <- unique_codes[code_i]
    curCodeData <- test_data[test_data$pcode==curCode,]
    pts_x_trials <- curCodeData$PTS==pts
    tns_x_trials <- curCodeData$TNS==tns
    question_x_trials <- curCodeData$question==question
    targetPos_x_trials <- curCodeData$TargetPosition==targetPos
    accessoryPos_x_trials <- curCodeData$AccessoryPosition==accPos
    queriedPos_x_trials <- curCodeData$queriedPosition==queriedPos
    curCode_condiData <- curCodeData[(pts_x_trials&tns_x_trials&question_x_trials&
                                        targetPos_x_trials&accessoryPos_x_trials&
                                        queriedPos_x_trials),]
    tbl_fqs <- table(curCode_condiData$response_sdt)
    if(is.element("hit",names(tbl_fqs))){
      if(tbl_fqs["hit"]==sum(tbl_fqs)){
        p_correct <- prop.table(tbl_fqs)["hit"]
      }else{p_correct <- prop.table(tbl_fqs)["hit"]-prop.table(tbl_fqs)["miss"]}
    }else{
      if(tbl_fqs["cr"]==sum(tbl_fqs)){
        p_correct <- prop.table(tbl_fqs)["cr"]
      }else{
        p_correct <- prop.table(tbl_fqs)["cr"]-prop.table(tbl_fqs)["fa"] 
      }
    }
    df_pCorrect_code_i <- data.frame(code=curCode,
                                     pts,tns,question,accPos,
                                     targetPos,queriedPos,
                                     p_c_corrected=p_correct)
    
   df_pCorrect <- rbind(df_pCorrect,df_pCorrect_code_i) 
  }
  return(df_pCorrect)
}

sameLow_PisT1_111 <- aggrFx2(pts="Same",tns="low",question="P = T1?",accPos=1,targetPos=1,queriedPos=1)
sameLow_PisT1_211 <- aggrFx2(pts="Same",tns="low",question="P = T1?",accPos=2,targetPos=1,queriedPos=1)
sameLow_PisT1_121 <- aggrFx2(pts="Same",tns="low",question="P = T1?",accPos=1,targetPos=2,queriedPos=1)
sameLow_PisT1_221 <- aggrFx2(pts="Same",tns="low",question="P = T1?",accPos=2,targetPos=2,queriedPos=1)
df2 <- rbind(sameLow_PisT1_111,sameLow_PisT1_211,sameLow_PisT1_121,sameLow_PisT1_221)
sameLow_PisT2_112 <- aggrFx2(pts="Same",tns="low",question="P = T2?",accPos=1,targetPos=1,queriedPos=2)
sameLow_PisT2_212 <- aggrFx2(pts="Same",tns="low",question="P = T2?",accPos=2,targetPos=1,queriedPos=2)
sameLow_PisT2_122 <- aggrFx2(pts="Same",tns="low",question="P = T2?",accPos=1,targetPos=2,queriedPos=2)
sameLow_PisT2_222 <- aggrFx2(pts="Same",tns="low",question="P = T2?",accPos=2,targetPos=2,queriedPos=2)
aggregate(p_c_corrected~targetPos*accPos*queriedPos,data=df2,FUN=function(i){
  return(c(mean(i),sd(i)))})

sameHigh_PisT1_111 <- aggrFx2(pts="Same",tns="high",question="P = T1?",accPos=1,targetPos=1,queriedPos=1)
sameHigh_PisT1_211 <- aggrFx2(pts="Same",tns="high",question="P = T1?",accPos=2,targetPos=1,queriedPos=1)
sameHigh_PisT1_121 <- aggrFx2(pts="Same",tns="high",question="P = T1?",accPos=1,targetPos=2,queriedPos=1)
sameHigh_PisT1_221 <- aggrFx2(pts="Same",tns="high",question="P = T1?",accPos=2,targetPos=2,queriedPos=1)
df2 <- rbind(df2,sameHigh_PisT1_111,sameHigh_PisT1_211,sameHigh_PisT1_121,sameHigh_PisT1_221)
sameHigh_PisT2_112 <- aggrFx2(pts="Same",tns="high",question="P = T2?",accPos=1,targetPos=1,queriedPos=2)
sameHigh_PisT2_212 <- aggrFx2(pts="Same",tns="high",question="P = T2?",accPos=2,targetPos=1,queriedPos=2)
sameHigh_PisT2_122 <- aggrFx2(pts="Same",tns="high",question="P = T2?",accPos=1,targetPos=2,queriedPos=2)
sameHigh_PisT2_222 <- aggrFx2(pts="Same",tns="high",question="P = T2?",accPos=2,targetPos=2,queriedPos=2)
df2 <- rbind(df2,sameHigh_PisT2_112,sameHigh_PisT2_212,sameHigh_PisT2_122,sameHigh_PisT2_222)
df2 <- rbind(df2,sameLow_PisT2_112,sameLow_PisT2_212,sameLow_PisT2_122,sameLow_PisT2_222)
df2$code <- as.factor(df2$code)
df2$pts <- as.factor(df2$pts)
df2$tns <- as.factor(df2$tns)
df2$question <- as.factor(df2$question)
df2$accPos <- as.factor(df2$accPos)
df2$queriedPos <- as.factor(df2$queriedPos)

aggregate(p_c_corrected~targetPos*accPos*queriedPos*tns,data=df2,
          FUN=function(i){return(c(mean(i),sd(i)))})
aggregate(p_c_corrected~targetPos*queriedPos,data=df2,
          FUN=function(i){return(c(mean(i),sd(i)))})
aggregate(p_c_corrected~targetPos*queriedPos*accPos,data=df2,
          FUN=function(i){return(c(mean(i),sd(i)))})
aggregate(p_c_corrected~queriedPos*accPos*tns,data=df2,
          FUN=function(i){return(c(mean(i),sd(i)))})

aov_res <- aov(p_c_corrected~targetPos*accPos*queriedPos*tns + 
                 Error(code/(targetPos*accPos*tns)),
               data=df2)
summary(aov_res)
aggr_2wayInteraction <- aggregate(p_c_corrected~targetPos*queriedPos, 
          data=df2,FUN=function(i){c(mean(i),sd(i))})
aggr_3wayInteraction <- aggregate(p_c_corrected~targetPos*queriedPos*tns, 
          data=df2,FUN=function(i){c(mean(i),sd(i))})
