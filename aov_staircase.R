
getwd()
setwd("/Users/paulseitlinger/Documents/GitHub/STIWA")
data <- read.csv("_5f6hb2#.csv")
A_rows <- data$A_or_B_track=="A"
unique_tracks_A <- unique(data[A_rows,"track"])
unique_tracks_B <- unique(data[A_rows==FALSE,"track"])
df <- NULL
for(i in unique_tracks_A){
	A_track_i_rows <- data[A_rows,"track"]==i
	A_track_i_CBAs <- data[A_track_i_rows,"cur_back_ang"]
	df <- rbind(df,data.frame(A_or_B="A",x=1:length(A_track_i_CBAs),CBA= A_track_i_CBAs))
}