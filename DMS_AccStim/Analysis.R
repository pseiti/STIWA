#Fa_Rate = 1/(2*N) if (nFa+nCr)==0 else nFa/(nFa+nCr)
 #   P_correct = np.divide((nHit + nCr),(nHit + nCr + nMiss + nFa))
  #  P_error = np.divide((nFa + nMiss),(nHit + nCr + nMiss + nFa))
   # P_correct_corrected = P_correct - P_error # https://www.researchgate.net/profile/Stephen-Link-2/publication/232548798_Correcting_response_measures_for_guessing_and_partial_information/links/0a85e53bc1e2d5f277000000/Correcting-response-measures-for-guessing-and-partial-information.pdf


path_to_data <- "~/Dokumente/GitHub/STIWA/DMS_AccStim/Data/"
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

print(paste("Sample size: ",N_sample))

# compute and insert variable: queriedItem
# .....

# aggregate over conditions per participant
df_rocPoints_individual <- NULL
qTypeNames <- c("P = T1?","P = T2?")
for(code_i in c(1:N_sample)){
  curCode <- unique_codes[code_i]
  curCodeData <- test_data[test_data$pcode==curCode,]

  Same_trials <- curCodeData$PTS=="Same"
  curCode_sameData <- curCodeData[Same_trials,]

  curCode_sameData_eqQ1 <- curCode_sameData[curCode_sameData$question=="P = T1?",]
  curCode_sameData_xqQ1 <- curCode_sameData[curCode_sameData$question=="P != T1?",]
  curCode_sameData_eqQ2 <- curCode_sameData[curCode_sameData$question=="P = T2?",]
  curCode_sameData_xqQ1 <- curCode_sameData[curCode_sameData$question=="P != T2?",]

  list_qType_specific_data <- list(PisT1=curCode_sameData_eqQ1,PisT2=curCode_sameData_eqQ2)

  df_code_i <- NULL; df2_code_i <- NULL
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
    df_code_i <- rbind(df_code_i,
      data.frame(code=curCode,qType=qTypeNames[x],targetPosition=1,
        rating=c("sure","quiteSure","unsure"),
        respType="hit",fq=fqs_hitRate_perConfidence)
      )
    
    fqs_faRate_perConfidence <- fx(data_x=data_faRate)
    fqs_faRate_sum <- sum(fqs_faRate_perConfidence)
    df_code_i <- rbind(df_code_i,
      data.frame(code=curCode,qType=qTypeNames[x],targetPosition=2,
        rating=c("sure","quiteSure","unsure"),
        respType="fa",fq=fqs_faRate_perConfidence)
      )
    
    fqs_missRate_perConfidence <- fx(data_x=data_missRate)
    fqs_missRate_sum <- sum(fqs_missRate_perConfidence)
    df_code_i <- rbind(df_code_i,
      data.frame(code=curCode,qType=qTypeNames[x],targetPosition=1,
        rating=c("sure","quiteSure","unsure"),
        respType="miss",fq=fqs_missRate_perConfidence)
      )

    fqs_crRate_perConfidence <- fx(data_x=data_crRate)
    fqs_crRate_sum <- sum(fqs_crRate_perConfidence)
    df_code_i <- rbind(df_code_i,
      data.frame(code=curCode,qType=qTypeNames[x],targetPosition=2,
        rating=c("sure","quiteSure","unsure"),
        respType="cr",fq=fqs_crRate_perConfidence)
      )

    sumOfsums <- sum(c(fqs_hitRate_sum,fqs_faRate_sum,fqs_missRate_sum,fqs_crRate_sum))
    hitRate <- fqs_hitRate_sum/sum(c(fqs_hitRate_sum,fqs_missRate_sum))
    faRate <- fqs_faRate_sum/sum(c(fqs_faRate_sum,fqs_crRate_sum))
    dPrime <- qnorm(hitRate)-qnorm(faRate)

    df2_code_i <- rbind(df2_code_i,
      data.frame(code=curCode,qName=qTypeNames[x],
        queriedPosition=x,qType="eq",
        hit_fq=fqs_hitRate_sum,fa_fq=fqs_faRate_sum,
        miss_fq=fqs_missRate_sum,cr_fq=fqs_crRate_sum,
        sumOfsums=sumOfsums,hitRate=hitRate,faRate=faRate,dPrime=dPrime)
      )

  }
}

print(df_code_i)
print(df2_code_i)

# path_to_plot <- "~/Dokumente/GitHub/STIWA/DMS_AccStim/"
# setwd(path_to_plot)
# pdf("test.pdf")
# plot(roc_means[1:5]~roc_means[6:10],xlim=c(0,1),ylim=c(0,1))
# points(c(0,1),c(0,1),type="l")
# dev.off()