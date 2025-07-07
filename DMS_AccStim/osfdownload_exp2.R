############################################################
### CatCim R script, March 2022
############################################################

library(osfr)
# setwd("~/Desktop/Schreibtisch_0/FFG-Haptics/Exp_AT_synchron_1/")
setwd("/home/saulpeitlinger/Dokumente/GitHub/STIWA/DMS_AccStim/")

## download data
getCatCimDataFx <- function(url){
	
	osf_catcim_link <- url
	osf_catcim <- osf_retrieve_node(osf_catcim_link)
	print(osf_catcim)
	# analysis_folder <- osf_ls_files(osf_catcim,pattern="Analysis")#, type="folder")
	data_folder <- osf_ls_files(osf_catcim,pattern="Data")#, type="folder")
	#exp1_folder <- osf_ls_files(data_folder,pattern="Experiment_1")
	#exp2_folder <- osf_ls_files(data_folder,pattern="Experiment_2.1")
	#main_folder <- osf_ls_files(exp2_folder,pattern="Main")
	
	osf_download(
	  data_folder,
	  path = NULL,
	  recurse = TRUE, # in case of a folder
	  conflicts = "skip",
	  verbose = FALSE,
	  progress = FALSE
	)
	getwd() # to directly show in terminal where the data is
}
getCatCimDataFx(url="https://osf.io/mf34h/")


#allFileNames <- list.files(path=getwd())
#allFileNames
