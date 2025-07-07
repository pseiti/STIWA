
# path_to_data <- "~/Desktop/Schreibtisch_0/FFG-Haptics/Exp_AT_synchron_1/data/"
# setwd(path_to_data)
# allFileNames <- list.files(path=path_to_data)
# dmsData_ids <- as.vector(sapply(allFileNames,function(i){grepl("dms",i)}))
# dmsData_fileNames <- allFileNames[dmsData_ids]
# N_sample <- length(dmsData_fileNames)

# # merging data
# for (x in dmsData_fileNames) {
#   code_x_data <- read.csv(file = x, header = TRUE)
#   if(x==dmsData_fileNames[1]){data_merged <- code_x_data}else{
#     data_merged <- rbind(data_merged,code_x_data)
#   }
# }
# test_data <- data_merged[data_merged$practice=="False",]

# # aggregate over conditions per participant
# for (file_i in dmsData_fileNames) {
#   # file_i <- dmsData_fileNames[1]
#   file_i_content <- read.csv(file_i, header = T)
#   # head(file_i_content)
#   # loop structure: 
#   # # queried_target (T=1 and T!=1, or, T=2 and T=!2) 
#   # # hits (e.g., a T1-trial with a 'T=1?'-question and a 'yes' response)
#   # # fas (e.g., a T1-trial with a  'T=2'-question and  a 'yes' response)
#   P_is_T1_rows <- file_i_content$question=="P == T1?"
#   P_isNot_T1_rows <- file_i_content$question=="P != T1?"
  
    
# }

# print(P_is_T1_rows[:4])
print("hello")