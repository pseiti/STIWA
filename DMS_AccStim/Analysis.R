#Fa_Rate = 1/(2*N) if (nFa+nCr)==0 else nFa/(nFa+nCr)
 #   P_correct = np.divide((nHit + nCr),(nHit + nCr + nMiss + nFa))
  #  P_error = np.divide((nFa + nMiss),(nHit + nCr + nMiss + nFa))
   # P_correct_corrected = P_correct - P_error # https://www.researchgate.net/profile/Stephen-Link-2/publication/232548798_Correcting_response_measures_for_guessing_and_partial_information/links/0a85e53bc1e2d5f277000000/Correcting-response-measures-for-guessing-and-partial-information.pdf


path_to_data <- "~/Dokumente/GitHub/STIWA/DMS_AccStim/Data"
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

# aggregate over conditions per participant
df_rocPoints_individual <- NULL
for(code_i in c(1:N_sample)){
  curCode <- unique_codes[code_i]
  curCodeData <- test_data[test_data$pcode==curCode,]
  Same_trials <- curCodeData$PTS=="Same"
  curCode_sameData <- curCodeData[Same_trials,]
  T1_trials <- curCode_sameData$TargetPosition==1
  qType_equal_trials <- curCode_sameData$questionType=="equal"
  respYes_trials <- curCode_sameData$response_dicho=="Yes"
  
  responses_sdt <- curCode_sameData$response_sdt

  hitRates_123_data <- curCode_sameData[T1_trials&qType_equal_trials&respYes_trials,]
  fqs_hitRates_123 <- table(hitRates_123_data$response_rating)
  fq_ids <- match(c("sure","quiteSure","unsure"),names(fqs_hitRates_123))
  fqs_hitRates_123 <- fqs_hitRates_123[fq_ids]
  
  hitRates_456_data <- curCode_sameData[T1_trials&(qType_equal_trials==FALSE)&respYes_trials,]
  fqs_hitRates_456 <- table(hitRates_456_data$response_rating)
  fq_ids <- match(c("unsure","quiteSure","sure"),names(fqs_hitRates_456))
  fqs_hitRates_456 <- fqs_hitRates_456[fq_ids]
  
  fqs_hits <- c(fqs_hitRates_123,fqs_hitRates_456)
  props_hits <- fqs_hits / sum(fqs_hits)
  hitRates_cumul <- cumsum(props_hits)

  faRates_123_data <- curCode_sameData[(T1_trials==FALSE)&qType_equal_trials&respYes_trials,]
  fqs_faRates_123 <- table(faRates_123_data$response_rating)
  fq_ids <- match(c("sure","quiteSure","unsure"),names(fqs_faRates_123))
  fqs_faRates_123 <- fqs_faRates_123[fq_ids]
  
  faRates_456_data <- curCode_sameData[(T1_trials==FALSE)&(qType_equal_trials==FALSE)&respYes_trials,]
  fqs_faRates_456 <- table(faRates_123_data$response_rating)
  fq_ids <- match(c("unsure","quiteSure","sure"),names(fqs_faRates_456))
  fqs_faRates_456 <- fqs_faRates_456[fq_ids]
  
  fqs_fas <- c(fqs_faRates_123,fqs_faRates_456)
  props_fas <- fqs_fas / sum(fqs_fas)
  faRates_cumul <- cumsum(props_fas)

  curCode_df <- data.frame(curCode)
  for (i in 1:10) {
    if(i<6) {
      curCode_df <- cbind(curCode_df, hitRates_cumul[i])
      } else { 
      curCode_df <- cbind(curCode_df, faRates_cumul[i-5])
    }
  }
  colnames(curCode_df) <- c("code",paste("hitRate_",1:5,sep=""),paste("faRate_",6:10,sep=""))
  if(code_i==1){
    df_rocPoints_individual <- curCode_df
  } else {
    df_rocPoints_individual <- rbind(df_rocPoints_individual, curCode_df)
  }
}
roc_means <- colMeans(df_rocPoints_individual[,2:11],na.rm=T)

path_to_plot <- "~/Dokumente/GitHub/STIWA/DMS_AccStim/"
setwd(path_to_data)
pdf("test.pdf")
plot(roc_means[1:5]~roc_means[6:10],xlim=c(0,1),ylim=c(0,1))
points(c(0,1),c(0,1),type="l")
dev.off()