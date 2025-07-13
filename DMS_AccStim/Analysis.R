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
  df <- NULL
  for(code_i in c(1:N_sample)){
    curCode <- unique_codes[code_i]
    curCodeData <- test_data[test_data$pcode==curCode,]

    pts_x_trials <- curCodeData$PTS==pts
    tns_x_trials <- curCodeData$TNS==tns
    # queriedPosition_x_trials <- curCodeData$queriedPosition==qPos
    accessoryPosition_x_trials <- curCodeData$AccessoryPosition==accPos

    # curCode_condiData <- curCodeData[pts_x_trials&tns_x_trials&queriedPosition_x_trials&accessoryPosition_x_trials,]
    # curCode_condiData_eqQ1 <- curCode_condiData[curCode_condiData$question=="P = T1?",]
    # curCode_condiData_xqQ1 <- curCode_condiData[curCode_condiData$question=="P != T1?",]
    # curCode_condiData_eqQ2 <- curCode_condiData[curCode_condiData$question=="P = T2?",]
    # curCode_condiData_xqQ2 <- curCode_condiData[curCode_condiData$question=="P != T2?",]
    curCode_condiData <- curCodeData[pts_x_trials&tns_x_trials&accessoryPosition_x_trials,]
    curCode_condiData_eqQ1 <- curCode_condiData[curCode_condiData$question=="P = T1?",]
    curCode_condiData_eqQ2 <- curCode_condiData[curCode_condiData$question=="P = T2?",]
    list_qType_specific_data <- list(PisT1=curCode_condiData_eqQ1,PisT2=curCode_condiData_eqQ2)

    df_code_i <- NULL; df2_code_i <- NULL
    for (x in 1:2) {
      curData <- list_qType_specific_data[[x]]
      # if(x==2){print(head(curData))}
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
      # df_code_i <- rbind(df_code_i,
      #   data.frame(code=curCode,qType=qTypeNames[x],targetPosition=1,
      #     rating=c("sure","quiteSure","unsure"),
      #     respType="hit",fq=fqs_hitRate_perConfidence)
      #   )
      
      fqs_faRate_perConfidence <- fx(data_x=data_faRate)
      fqs_faRate_sum <- sum(fqs_faRate_perConfidence)
      # df_code_i <- rbind(df_code_i,
      #   data.frame(code=curCode,qType=qTypeNames[x],targetPosition=2,
      #     rating=c("sure","quiteSure","unsure"),
      #     respType="fa",fq=fqs_faRate_perConfidence)
      #   )
      
      fqs_missRate_perConfidence <- fx(data_x=data_missRate)
      fqs_missRate_sum <- sum(fqs_missRate_perConfidence)
      # df_code_i <- rbind(df_code_i,
      #   data.frame(code=curCode,qType=qTypeNames[x],targetPosition=1,
      #     rating=c("sure","quiteSure","unsure"),
      #     respType="miss",fq=fqs_missRate_perConfidence)
      #   )

      fqs_crRate_perConfidence <- fx(data_x=data_crRate)
      fqs_crRate_sum <- sum(fqs_crRate_perConfidence)
      # df_code_i <- rbind(df_code_i,
      #   data.frame(code=curCode,qType=qTypeNames[x],targetPosition=2,
      #     rating=c("sure","quiteSure","unsure"),
      #     respType="cr",fq=fqs_crRate_perConfidence)
      #   )

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

      df2_code_i <- rbind(df2_code_i,
        data.frame(code=curCode,qName=qTypeNames[x],
          tns=tns,pts=pts,queriedPosition=x,accessoryPosition=accPos,
          qType="eq",
          hit_fq=fqs_hitRate_sum,fa_fq=fqs_faRate_sum,
          miss_fq=fqs_missRate_sum,cr_fq=fqs_crRate_sum,
          sumOfsums=sumOfsums,hitRate=hitRate,faRate=faRate,dPrime=dPrime)
        )

    }
    df <- rbind(df,df2_code_i)
  }
  return(df)
}
same_low_1_1 <- aggrFx(pts="Same",tns="low",accPos=1)
same_low_1_2 <- aggrFx(pts="Same",tns="low",accPos=2)
same_high_1_1 <- aggrFx(pts="Same",tns="high",accPos=1)
same_high_1_2 <- aggrFx(pts="Same",tns="high",accPos=2)

print(
  aggregate(dPrime ~ queriedPosition,mean,data=same_low_1_1)
)
print(
  aggregate(dPrime ~ queriedPosition,mean,data=same_low_1_2)
)
print(
  aggregate(dPrime ~ queriedPosition,mean,data=same_high_1_1)
)
print(
  aggregate(dPrime ~ queriedPosition,mean,data=same_high_1_2)
)
# aggregate over conditions per participant


# print(df_code_i)
# print(df2_code_i)

# path_to_plot <- "~/Dokumente/GitHub/STIWA/DMS_AccStim/"
# setwd(path_to_plot)
# pdf("test.pdf")
# plot(roc_means[1:5]~roc_means[6:10],xlim=c(0,1),ylim=c(0,1))
# points(c(0,1),c(0,1),type="l")
# dev.off()