
getwd()
setwd("/Users/paulseitlinger/Documents/GitHub/STIWA")

nLastElements <- 10
fx <- function(d){
	data <- read.csv(d)
	A_rows <- data$A_or_B_track=="A"
	A_data <- data[A_rows,]
	B_data <- data[A_rows==FALSE,]
	unique_tracks_A <- unique(A_data[,"track"])
	unique_tracks_B <- unique(B_data[,"track"])
	
	df_mean <- NULL
	df_revPoints <- NULL
	
	for(i in 1:length(unique_tracks_A)){
		i_track <- unique_tracks_A[i]
		A_track_i_rows <- A_data[,"track"]==i_track
		nRows <- length(which(A_track_i_rows)==TRUE)
		A_track_i_CBAs <- A_data[A_track_i_rows,"cur_back_ang"]
		A_track_i_CBAs_tail <- tail(A_track_i_CBAs,nLastElements)
		revPoints <- match(c(1:12),A_data$revs)
		CBA_at_revPoints <- A_track_i_CBAs[revPoints]
		df_mean <- rbind(df_mean,
			data.frame(A_or_B="A",track=i_track,CBA_mean=mean(A_track_i_CBAs_tail),
			CBA_SD=sd(A_track_i_CBAs))
		)
		df_revPoints <- rbind(df_revPoints,
			data.frame(A_or_B="A",track=i_track,revPoints=1:12,CBA=CBA_at_revPoints)
		)
	}
	for(i in 1:length(unique_tracks_B)){
		i_track <- unique_tracks_B[i]
		B_track_i_rows <- B_data[,"track"]==i_track
		nRows <- length(which(B_track_i_rows)==TRUE)
		B_track_i_CBAs <- B_data[B_track_i_rows,"cur_back_ang"]
		B_track_i_CBAs_tail <- tail(B_track_i_CBAs,nLastElements)
		M_B_track <- B_track_i_CBAs
		revPoints <- match(c(1:12),B_data$revs)
		CBA_at_revPoints <- B_track_i_CBAs[revPoints]
		df_mean <- rbind(df_mean,
			data.frame(A_or_B="B",track=i_track,CBA_mean=mean(B_track_i_CBAs_tail),
			CBA_SD=sd(B_track_i_CBAs))
		)
		df_revPoints <- rbind(df_revPoints,
			data.frame(A_or_B="B",track=i_track,revPoints=1:12,CBA=CBA_at_revPoints)
		)
	}
	M_CBA_ATrack <- mean(df_mean[df_mean$A_or_B=="A",]$CBA_mean)
	M_CBA_BTrack <- mean(df_mean[df_mean$A_or_B=="B",]$CBA_mean)
	SD_CBA_ATrack <- mean(df_mean[df_mean$A_or_B=="A",]$CBA_SD)
	SD_CBA_BTrack <- mean(df_mean[df_mean$A_or_B=="B",]$CBA_SD)
	
	df_res_means <- data.frame(M_A=M_CBA_ATrack,SD_A= SD_CBA_ATrack,
	M_B=M_CBA_BTrack,SD_B=SD_CBA_BTrack)
	df_res_CBA_at_revPoints = aggregate(CBA~revPoints*A_or_B,data=df_revPoints,mean)
	
	return(list(df_res_means=df_res_means,
	df_res_CBA_at_revPoints=df_res_CBA_at_revPoints))
}
fx_out <- fx(d="_5f6hb2#.csv")
df_res_CBA_at_revPoints <- fx_out$df_res_CBA_at_revPoints
CBA_at_revPoints_ATrack <- df_res_CBA_at_revPoints[df_res_CBA_at_revPoints$A_or_B=="A","CBA"]
CBA_at_revPoints_BTrack <- df_res_CBA_at_revPoints[df_res_CBA_at_revPoints$A_or_B=="B","CBA"]
pdf("CBA_at_revPoints.pdf")
plot(CBA_at_revPoints,ylim=c(0,5),type="o",xlab="Number revisions",ylab="Mean number")
arrows(1:12, avg-sdev, 1:nBack, avg+sdev, length=0.05, angle=90, code=3) # https://stackoverflow.com/questions/13032777/scatter-plot-with-error-bars
points(CBA_at_revPoints_BTrack,type="o",lty=2)
dev.off()

