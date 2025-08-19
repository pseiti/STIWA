
getwd()
setwd("/Users/paulseitlinger/Documents/GitHub/STIWA")
data <- read.csv("_5f6hb2#.csv")
A_rows <- data$A_or_B_track=="A"
A_data <- data[A_rows,]
B_data <- data[A_rows==FALSE,]
unique_tracks_A <- unique(A_data[,"track"])
unique_tracks_B <- unique(B_data[,"track"])

df <- NULL
nLastElements <- 10
for(i in 1:length(unique_tracks_A)){
	i_track <- unique_tracks_A[i]
	A_track_i_rows <- A_data[,"track"]==i_track
	nRows <- length(which(A_track_i_rows)==TRUE)
	A_track_i_CBAs <- A_data[A_track_i_rows,"cur_back_ang"]
	A_track_i_CBAs <- tail(A_track_i_CBAs,nLastElements)
	df <- rbind(df,
		data.frame(A_or_B="A",track=i_track,x=c(1:nLastElements),CBA=A_track_i_CBAs)
	)
}
aggregate(CBA~x,mean,data=df)

for(i in 1:length(unique_tracks_B)){
	i_track <- unique_tracks_B[i]
	B_track_i_rows <- B_data[,"track"]==i_track
	nRows <- length(which(B_track_i_rows)==TRUE)
	B_track_i_CBAs <- B_data[B_track_i_rows,"cur_back_ang"]
	B_track_i_CBAs <- tail(B_track_i_CBAs,nLastElements)
	df <- rbind(df,
		data.frame(A_or_B="A",track=i_track,x=c(1:nLastElements),CBA=A_track_i_CBAs)
	)
}
aggregate(CBA~x,mean,data=df)