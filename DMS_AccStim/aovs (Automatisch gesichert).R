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
	⁃	
